"""Instagram 抓取 service — 雙軌策略。

兩種抓法：
1. fetch_media_info(): 用 session cookie 直接打非官方 /api/v1/media/.../info/
   - 可以拿到 IG + FB 合計播放數（fb_play_count）
   - 需要 IG_SESSION_ID + IG_CSRF_TOKEN
2. fetch_media_info_with_token(): 用 OAuth access_token 打 Graph API
   - 只有 IG 純播放數
   - 不需要 cookie，比較合規

videos.py 會看狀況選一個。
"""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import quote, unquote

import httpx

from config import IG_CSRF_TOKEN, IG_SESSION_ID

_IG_WEB_APP_ID = "936619743392459"
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


# ── helpers ───────────────────────────────────────────────────────────────────


def extract_shortcode(url: str) -> str | None:
    """從 IG URL 撈 shortcode。
    支援 /p/、/reel/、/reels/ 三種路徑。
    """
    m = re.search(r"/(p|reel|reels)/([A-Za-z0-9_-]+)", url)
    return m.group(2) if m else None


def shortcode_to_media_id(shortcode: str) -> str:
    """IG 的 base64 編碼：shortcode 字符對應 0-63，組成大整數就是 media id。"""
    n = 0
    for ch in shortcode:
        n = n * 64 + _ALPHABET.index(ch)
    return str(n)


def _bearer_token(session_id: str) -> str:
    """從 sessionid cookie 組出 Authorization: Bearer IGT:2:... header。
    這個格式是 IG App 內部用的。
    """
    decoded = unquote(session_id)
    uid = decoded.split(":")[0]
    encoded = quote(decoded)
    payload = json.dumps({"ds_user_id": uid, "sessionid": encoded})
    return f"IGT:2:{base64.b64encode(payload.encode()).decode()}"


# ── 回傳結構 ─────────────────────────────────────────────────────────────────


@dataclass
class MediaInfo:
    shortcode: str
    mediaId: str
    username: str
    userId: str
    caption: str
    views: int | None
    igViews: int | None
    fbViews: int | None
    likes: int | None
    comments: int | None
    shares: int | None
    uploadedAt: str


# ── 1. 非官方 scraping（session cookie，可拿 IG+FB 合計）──────────────────────


def fetch_media_info(shortcode: str) -> MediaInfo:
    """用 sessionid 直接打 IG 內部 API。可以拿到 fb_play_count。"""
    if not IG_SESSION_ID:
        raise ValueError("缺少 IG_SESSION_ID 環境變數")

    media_id = shortcode_to_media_id(shortcode)
    bearer = _bearer_token(IG_SESSION_ID)
    cookie_session = unquote(IG_SESSION_ID)

    headers = {
        "User-Agent": "Instagram 275.0.0.27.98 Android (33/13; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100)",
        "X-IG-App-ID": _IG_WEB_APP_ID,
        "Authorization": f"Bearer {bearer}",
        "Cookie": f"sessionid={cookie_session}; csrftoken={IG_CSRF_TOKEN};",
        "X-CSRFToken": IG_CSRF_TOKEN,
        "Accept": "*/*",
    }

    with httpx.Client(timeout=10) as client:
        r = client.get(
            f"https://www.instagram.com/api/v1/media/{media_id}/info/",
            headers=headers,
        )
        data = r.json()

    if data.get("status") != "ok" or not data.get("items"):
        raise ValueError(f"IG API 回傳異常: {json.dumps(data)[:300]}")

    item = data["items"][0]
    user_id = str(item.get("user", {}).get("pk", ""))
    username = item.get("user", {}).get("username", "")
    ig_views: int = (
        item.get("ig_play_count")
        or item.get("play_count")
        or item.get("view_count")
        or 0
    )
    fb_play_raw: int = item.get("fb_play_count") or 0

    # 再打 GraphQL clips 拿總流量（可選）
    total_views = ig_views
    fb_views = fb_play_raw

    try:
        variables = json.dumps({
            "data": {
                "include_feed_video": True,
                "page_size": 12,
                "target_user_id": user_id,
            }
        })
        web_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "X-IG-App-ID": _IG_WEB_APP_ID,
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": IG_CSRF_TOKEN,
            "Cookie": f"sessionid={cookie_session}; csrftoken={IG_CSRF_TOKEN};",
            "Referer": f"https://www.instagram.com/{username}/reels/",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        with httpx.Client(timeout=15) as client:
            r = client.post(
                "https://www.instagram.com/graphql/query",
                headers=web_headers,
                content=f"variables={quote(variables)}&doc_id=26034716619511614",
            )
        clips_data = r.json()
        edges = (
            clips_data.get("data", {})
            .get("xdt_api__v1__clips__user__connection_v2", {})
            .get("edges", [])
        )
        target = next(
            (e for e in edges if e.get("node", {}).get("media", {}).get("code") == shortcode),
            None,
        )
        if target:
            total_views = target["node"]["media"].get("play_count", ig_views)
            fb_views = total_views - ig_views
    except Exception:
        # GraphQL 拿不到就只用 v1 那筆
        pass

    taken_at = item.get("taken_at", 0)
    uploaded = (
        datetime.fromtimestamp(taken_at, tz=timezone.utc).isoformat()
        if taken_at
        else datetime.now(timezone.utc).isoformat()
    )

    return MediaInfo(
        shortcode=shortcode,
        mediaId=media_id,
        username=username,
        userId=user_id,
        caption=(item.get("caption") or {}).get("text", ""),
        views=total_views,
        igViews=ig_views,
        fbViews=fb_views,
        likes=item.get("like_count"),
        comments=item.get("comment_count"),
        shares=item.get("share_count"),
        uploadedAt=uploaded,
    )


# ── 2. 官方 Graph API（OAuth token，IG only）──────────────────────────────────


def fetch_media_info_with_token(shortcode: str, access_token: str) -> MediaInfo:
    """用 OAuth token 打 Graph API。比較合規但拿不到 FB 流量。"""
    with httpx.Client(timeout=15) as client:
        # 找出對應的 media（要分頁 search）
        url: str | None = (
            f"https://graph.instagram.com/me/media"
            f"?fields=id,caption,media_type,timestamp,permalink,like_count,comments_count"
            f"&limit=50&access_token={access_token}"
        )
        media_obj = None
        media_id = None
        page = 0

        while url and page < 5:
            r = client.get(url)
            data = r.json()
            for item in data.get("data", []):
                m = re.search(r"/(p|reel|reels)/([A-Za-z0-9_-]+)", item.get("permalink", ""))
                if m and m.group(2) == shortcode:
                    media_obj = item
                    media_id = item["id"]
                    break
            if media_id:
                break
            url = data.get("paging", {}).get("next")
            page += 1

        if not media_id or not media_obj:
            raise ValueError(f"找不到 shortcode {shortcode} 的影片")

        # Insights
        plays = None
        shares = None
        try:
            r = client.get(
                f"https://graph.instagram.com/{media_id}/insights",
                params={"metric": "views,reach,shares", "access_token": access_token},
            )
            for metric in r.json().get("data", []):
                val = (
                    (metric.get("values") or [{}])[0].get("value")
                    if metric.get("values")
                    else metric.get("value")
                )
                if metric["name"] == "views":
                    plays = val
                if metric["name"] == "shares":
                    shares = val
        except Exception:
            pass

        # 用戶資訊
        r = client.get(
            "https://graph.instagram.com/me",
            params={"fields": "id,username", "access_token": access_token},
        )
        user_data = r.json()

    return MediaInfo(
        shortcode=shortcode,
        mediaId=media_id,
        username=user_data.get("username", ""),
        userId=user_data.get("id", ""),
        caption=media_obj.get("caption", ""),
        views=plays,
        igViews=plays,
        fbViews=None,
        likes=media_obj.get("like_count"),
        comments=media_obj.get("comments_count"),
        shares=shares,
        uploadedAt=media_obj.get("timestamp", ""),
    )

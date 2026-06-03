import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from services.instagram import fetch_media_info

router = APIRouter(prefix="/api")

@router.get("/reels")
def list_reels(request: Request) -> JSONResponse:
    """列出 IG Reels 影片清單，包含流量資訊"""
    
    access_token = request.cookies.get("ig_access_token")
    if not access_token:
        return JSONResponse({"error": "未登入"}, status_code=401)

    # 1. OAuth token 拿影片清單
    with httpx.Client(timeout=15) as client:
        r = client.get(
            "https://graph.instagram.com/me/media",
            params={
                "fields": "id,media_type,timestamp,permalink,thumbnail_url",
                "limit": "50",
                "access_token": access_token,
            },
        )
        media_data = r.json()

    if "error" in media_data:
        return JSONResponse(
            {"error": media_data["error"].get("message", "未知錯誤")},
            status_code=400,
        )

    # 2. 只留 reel / video
    reels = []
    for m in media_data.get("data", []):
        if m.get("media_type") not in ("REEL", "VIDEO"):
            continue
        match = re.search(
            r"/(p|reel|reels)/([A-Za-z0-9_-]+)", m.get("permalink", "")
        )
        if not match:
            continue
        reels.append({
            "id": m["id"],
            "shortcode": match.group(2),
            "timestamp": m.get("timestamp", ""),
            "permalink": m.get("permalink", ""),
            "thumbnailUrl": m.get("thumbnail_url"),
        })

    # 3. 平行抓流量（IG+FB 合計）
    results = []

    def _fetch(reel: dict) -> dict | None:
        try:
            info = fetch_media_info(reel["shortcode"])
            return {
                "id": reel["id"],
                "shortcode": reel["shortcode"],
                "caption": info.caption,
                "timestamp": reel["timestamp"],
                "permalink": reel["permalink"],
                "thumbnailUrl": reel["thumbnailUrl"],
                "plays": info.views,
                "igViews": info.igViews,
                "fbViews": info.fbViews,
                "likes": info.likes,
                "comments": info.comments,
                "shares": info.shares,
            }
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(_fetch, reel): reel for reel in reels}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # 4. 依時間排序，最新在前
    results.sort(key=lambda x: x["timestamp"], reverse=True)

    return JSONResponse(results)
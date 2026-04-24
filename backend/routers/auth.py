"""Instagram OAuth — 草稿版。

目前狀況：
- 重導到 IG 授權頁 OK
- callback 只換到短期 token（還沒處理長期 token）
- 直接把 token 用 query string 丟回前端（之後要改成 cookie）
- /me, /logout 還沒實作

scope 先用 user_profile 試試看，IG Business 那組之後再換。
"""

from urllib.parse import urlencode

import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse, RedirectResponse

from config import BASE_URL, INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET

router = APIRouter(prefix="/api/auth")

REDIRECT_URI = f"{BASE_URL}/api/auth/callback"


@router.get("/instagram")
def login():
    params = urlencode({
        "client_id": INSTAGRAM_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "user_profile",  # FIXME: 這個 scope 好像是舊版，要查一下新版要用哪個
        "response_type": "code",
    })
    return RedirectResponse(f"https://api.instagram.com/oauth/authorize?{params}")


@router.get("/callback")
def callback(code: str | None = None, error: str | None = None):
    if error or not code:
        return JSONResponse({"error": error or "no code"}, status_code=400)

    # 換短期 token
    with httpx.Client(timeout=15) as client:
        r = client.post(
            "https://api.instagram.com/oauth/access_token",
            data={
                "client_id": INSTAGRAM_APP_ID,
                "client_secret": INSTAGRAM_APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        )
        token_data = r.json()

    if "access_token" not in token_data:
        return JSONResponse({"error": "token exchange failed", "detail": token_data}, status_code=400)

    # TODO: 換長期 token、寫進 cookie
    # 先暫時把 token 拼回首頁的 query string，方便 debug
    return RedirectResponse(f"{BASE_URL}/?token={token_data['access_token']}")

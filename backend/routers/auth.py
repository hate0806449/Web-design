"""Instagram OAuth — IG Business Login + 長期 token + cookie session。

修了 PM 草稿版的問題：
- scope 從舊版 user_profile 換成 instagram_business_basic + insights
- 加了短期 → 長期 token 交換
- token 寫到 httponly cookie，不再用 query string
- 補 /me 跟 /logout
"""

from __future__ import annotations

import json
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

from config import BASE_URL, INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET

router = APIRouter(prefix="/api/auth")

REDIRECT_URI = f"{BASE_URL}/api/auth/callback"
SCOPES = "instagram_business_basic,instagram_business_manage_insights"
COOKIE_MAX_AGE = 60 * 60 * 24 * 60  # 長期 token 60 天有效


@router.get("/instagram")
def login():
    params = urlencode({
        "client_id": INSTAGRAM_APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "response_type": "code",
    })
    return RedirectResponse(
        f"https://www.instagram.com/oauth/authorize?{params}"
    )


@router.get("/callback")
def callback(code: str | None = None, error: str | None = None):
    if error or not code:
        return RedirectResponse(f"{BASE_URL}/?error=ig_auth_failed")

    with httpx.Client(timeout=15) as client:
        # 1. 短期 token
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
            return RedirectResponse(f"{BASE_URL}/?error=token_exchange_failed")

        # 2. 換長期 token（60 天）
        r = client.get(
            "https://graph.instagram.com/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_id": INSTAGRAM_APP_ID,
                "client_secret": INSTAGRAM_APP_SECRET,
                "access_token": token_data["access_token"],
            },
        )
        long_data = r.json()
        access_token = long_data.get("access_token", token_data["access_token"])

        # 3. 拿 user 資訊
        r = client.get(
            "https://graph.instagram.com/me",
            params={"fields": "id,username", "access_token": access_token},
        )
        user_data = r.json()

    user_json = json.dumps({
        "id": user_data.get("id", token_data.get("user_id", "")),
        "username": user_data.get("username", ""),
    })

    response = RedirectResponse(f"{BASE_URL}/")
    # access_token httponly，前端拿不到 → 安全
    response.set_cookie(
        "ig_access_token",
        access_token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
    )
    # user 資訊讓前端讀
    response.set_cookie(
        "ig_user",
        user_json,
        max_age=COOKIE_MAX_AGE,
        httponly=False,
        samesite="lax",
    )
    return response


@router.get("/me")
def me(request: Request):
    raw = request.cookies.get("ig_user")
    if not raw:
        return JSONResponse(None)
    try:
        return JSONResponse(json.loads(raw))
    except Exception:
        return JSONResponse(None)


@router.post("/logout")
def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie("ig_access_token")
    response.delete_cookie("ig_user")
    return response

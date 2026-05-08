"""Videos API — 改成走真實 DB + IG service。

支援：
- GET    /api/videos           列所有追蹤影片（含最新一筆 Snapshot）
- POST   /api/videos           新增追蹤（會立刻打 IG 抓一筆 Snapshot）

DELETE / refresh / 歷史 snapshot 留給穎禾下階段做。
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Snapshot, Video
from services.instagram import (
    extract_shortcode,
    fetch_media_info,
    fetch_media_info_with_token,
)

router = APIRouter(prefix="/api/videos")


def _serialize_snapshot(s: Snapshot) -> dict:
    return {
        "id": s.id,
        "videoId": s.videoId,
        "views": s.views,
        "igViews": s.igViews,
        "fbViews": s.fbViews,
        "likes": s.likes,
        "comments": s.comments,
        "shares": s.shares,
        "scrapedAt": s.scrapedAt.isoformat() if s.scrapedAt else None,
    }


def _serialize_video(v: Video) -> dict:
    latest = v.snapshots[0] if v.snapshots else None
    return {
        "id": v.id,
        "shortcode": v.shortcode,
        "mediaId": v.mediaId,
        "username": v.username,
        "caption": v.caption,
        "uploadedAt": v.uploadedAt.isoformat() if v.uploadedAt else None,
        "createdAt": v.createdAt.isoformat() if v.createdAt else None,
        "latestSnapshot": _serialize_snapshot(latest) if latest else None,
    }


def _pick_fetcher(request: Request):
    """有 OAuth token 用官方 API，沒有就用 session cookie。"""
    access_token = request.cookies.get("ig_access_token")
    if access_token:
        return lambda sc: fetch_media_info_with_token(sc, access_token)
    return fetch_media_info


# ── GET ──────────────────────────────────────────────────────────────────────


@router.get("")
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(Video.createdAt.desc()).all()
    return JSONResponse([_serialize_video(v) for v in videos])


# ── POST ─────────────────────────────────────────────────────────────────────


class AddVideoBody(BaseModel):
    url: str


@router.post("")
def add_video(
    body: AddVideoBody,
    request: Request,
    db: Session = Depends(get_db),
):
    shortcode = extract_shortcode(body.url)
    if not shortcode:
        return JSONResponse({"error": "無效的 Instagram 連結"}, status_code=400)

    existing = db.query(Video).filter(Video.shortcode == shortcode).first()
    if existing:
        return JSONResponse({"error": "此影片已在追蹤清單中"}, status_code=409)

    fetcher = _pick_fetcher(request)
    try:
        info = fetcher(shortcode)
    except Exception as e:
        return JSONResponse({"error": f"IG API 失敗: {e}"}, status_code=502)

    video = Video(
        shortcode=info.shortcode,
        mediaId=info.mediaId,
        username=info.username,
        caption=info.caption,
        uploadedAt=(
            datetime.fromisoformat(info.uploadedAt) if info.uploadedAt else None
        ),
    )
    snapshot = Snapshot(
        views=info.views,
        igViews=info.igViews,
        fbViews=info.fbViews,
        likes=info.likes,
        comments=info.comments,
        shares=info.shares,
    )
    video.snapshots.append(snapshot)
    db.add(video)
    db.commit()
    db.refresh(video)
    return JSONResponse(_serialize_video(video))

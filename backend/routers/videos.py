"""Videos API — CRUD 完整版 + Snapshot 歷史 + CSV 匯出。"""

from __future__ import annotations

import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
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
    access_token = request.cookies.get("ig_access_token")
    if access_token:
        return lambda sc: fetch_media_info_with_token(sc, access_token)
    return fetch_media_info


# ── GET /api/videos ──────────────────────────────────────────────────────────


@router.get("")
def list_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(Video.createdAt.desc()).all()
    return JSONResponse([_serialize_video(v) for v in videos])


# ── POST /api/videos ─────────────────────────────────────────────────────────


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


# ── GET /api/videos/export.csv ───────────────────────────────────────────────
# 注意：放在 /{video_id} 前面，否則會被路徑吃掉


@router.get("/export.csv")
def export_csv(db: Session = Depends(get_db)):
    """匯出所有 Video 的最新 Snapshot 成 CSV。"""
    videos = db.query(Video).order_by(Video.createdAt.desc()).all()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "shortcode", "username", "caption",
        "views", "igViews", "fbViews",
        "likes", "comments", "shares",
        "uploadedAt", "scrapedAt",
    ])

    for v in videos:
        s = v.snapshots[0] if v.snapshots else None
        writer.writerow([
            v.shortcode,
            v.username or "",
            (v.caption or "").replace("\n", " ")[:200],
            s.views if s else "",
            s.igViews if s else "",
            s.fbViews if s else "",
            s.likes if s else "",
            s.comments if s else "",
            s.shares if s else "",
            v.uploadedAt.isoformat() if v.uploadedAt else "",
            s.scrapedAt.isoformat() if s and s.scrapedAt else "",
        ])

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="videos.csv"'},
    )


# ── GET /api/videos/{id} ─────────────────────────────────────────────────────


@router.get("/{video_id}")
def get_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return JSONResponse({"error": "找不到影片"}, status_code=404)

    result = _serialize_video(video)
    # 歷史 snapshot 升序，給趨勢圖用
    result["snapshots"] = [
        _serialize_snapshot(s) for s in reversed(video.snapshots)
    ]
    return JSONResponse(result)


# ── DELETE /api/videos/{id} ──────────────────────────────────────────────────


@router.delete("/{video_id}")
def delete_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return JSONResponse({"error": "找不到影片"}, status_code=404)
    db.delete(video)
    db.commit()
    return JSONResponse({"ok": True})


# ── POST /api/videos/{id}/refresh ────────────────────────────────────────────


@router.post("/{video_id}/refresh")
def refresh_video(
    video_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return JSONResponse({"error": "找不到影片"}, status_code=404)

    fetcher = _pick_fetcher(request)
    try:
        info = fetcher(video.shortcode)
    except Exception as e:
        return JSONResponse({"error": f"IG API 失敗: {e}"}, status_code=502)

    snapshot = Snapshot(
        videoId=video.id,
        views=info.views,
        igViews=info.igViews,
        fbViews=info.fbViews,
        likes=info.likes,
        comments=info.comments,
        shares=info.shares,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return JSONResponse(_serialize_snapshot(snapshot))

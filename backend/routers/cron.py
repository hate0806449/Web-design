import time

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config import CRON_SECRET
from database import get_db
from models import Snapshot, Video
from services.instagram import fetch_media_info

router = APIRouter(prefix="/api")


@router.get("/cron")
def cron_refresh(
    db: Session = Depends(get_db),
    authorization: str = Header(""),
) -> JSONResponse:
    """刷新所有追蹤中的影片的流量資訊，並存成 snapshot。"""
    token = authorization.replace("Bearer ", "")
    if not CRON_SECRET or token != CRON_SECRET:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    videos = db.query(Video).all()
    results = []

    for v in videos:
        try:
            info = fetch_media_info(str(v.shortcode))
            snapshot = Snapshot(
                videoId=v.id,
                views=info.views,
                igViews=info.igViews,
                fbViews=info.fbViews,
                likes=info.likes,
                comments=info.comments,
                shares=info.shares,
            )
            db.add(snapshot)
            db.commit()
            results.append({"shortcode": v.shortcode, "ok": True})
        except Exception as e:
            results.append(
                {
                    "shortcode": v.shortcode,
                    "ok": False,
                    "error": str(e),
                }
            )

        # 防 IG rate limit
        time.sleep(1.5)

    return JSONResponse(
        {
            "refreshed": len([r for r in results if r["ok"]]),
            "results": results,
        }
    )

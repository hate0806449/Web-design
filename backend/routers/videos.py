"""Videos API — 暫時回假資料，等晶晶的 instagram 抓取 service 完成再接真實 DB。"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/videos")


# TODO: 換成從 DB 查
_FAKE_VIDEOS = [
    {
        "id": "fake_1",
        "shortcode": "DABCdEfGhIj",
        "username": "demo_creator",
        "views": 12345,
        "likes": 678,
        "comments": 42,
    },
    {
        "id": "fake_2",
        "shortcode": "DZyxWvUtSrQ",
        "username": "another_user",
        "views": 9876,
        "likes": 321,
        "comments": 15,
    },
    {
        "id": "fake_3",
        "shortcode": "DMnOpQrStUv",
        "username": "demo_creator",
        "views": 54321,
        "likes": 2100,
        "comments": 89,
    },
]


@router.get("")
def list_videos():
    return JSONResponse(_FAKE_VIDEOS)


class AddVideoBody(BaseModel):
    url: str


@router.post("")
def add_video(body: AddVideoBody):
    # TODO: 解析 shortcode、寫進 DB、呼叫 IG API 拿數據
    # 先回一筆假的，前端才有畫面可以測
    fake = {
        "id": f"fake_new_{len(_FAKE_VIDEOS) + 1}",
        "shortcode": "DNEWnewNEW0",
        "username": "you",
        "views": 0,
        "likes": 0,
        "comments": 0,
    }
    _FAKE_VIDEOS.insert(0, fake)
    return JSONResponse(fake)

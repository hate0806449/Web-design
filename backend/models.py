"""暫時用 dataclass，之後再換成 SQLAlchemy ORM + 接 DB。

TODO（晶晶接手）：
- 加 Snapshot 表
- 補 mediaId / caption / uploadedAt 欄位
- 加 SQLAlchemy Base 跟 relationship
"""

from dataclasses import dataclass


@dataclass
class Video:
    id: str
    shortcode: str
    username: str
    views: int
    likes: int

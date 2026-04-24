"""環境變數 — 暫時只放 IG App。DB / cookie 等之後再加。"""

import os
from dotenv import load_dotenv

# 從專案根目錄的 .env 讀
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID", "")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")
BASE_URL = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000")

"""環境變數 — 集中管理。"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ig_tracker",
)

INSTAGRAM_APP_ID = os.getenv("INSTAGRAM_APP_ID", "")
INSTAGRAM_APP_SECRET = os.getenv("INSTAGRAM_APP_SECRET", "")
BASE_URL = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000")

# 非官方 scraping 用 — 從瀏覽器 cookie 拿
IG_SESSION_ID = os.getenv("IG_SESSION_ID", "")
IG_CSRF_TOKEN = os.getenv("IG_CSRF_TOKEN", "")

# 排程用的 Bearer Token，避免被外面亂打
CRON_SECRET = os.getenv("CRON_SECRET", "")

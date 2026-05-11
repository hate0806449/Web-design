# IG Reel Tracker

期末專題：追蹤 Instagram Reels 數據（讚數、留言、播放）的 web app。

## 技術棧

- **前端**：Next.js 16 + React 19（port 3000）
- **後端**：FastAPI (Python)（port 8000）
- **DB**：PostgreSQL 16（Docker Compose）
- **ORM**：SQLAlchemy 2.0
- **抓取**：Instagram Graph API（官方）+ session cookie scraping（合計 IG+FB 流量）

## 啟動方式

### 1. 起資料庫

```bash
docker compose up -d
```

### 2. 後端

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

第一次啟動會自動 `create_all` 把 `Video` / `Snapshot` 表建出來。

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

開瀏覽器 → http://localhost:3000

### 4. 環境變數

```bash
cp .env.example .env
# 填入 INSTAGRAM_APP_ID / SECRET / IG_SESSION_ID / IG_CSRF_TOKEN
```

- IG App：到 [Meta for Developers](https://developers.facebook.com/) 申請
- IG_SESSION_ID / IG_CSRF_TOKEN：瀏覽器登入 IG 後在 DevTools → Application → Cookies 複製

## 目前進度

- [x] 專案骨架、docker-compose
- [x] FastAPI + 雙軌 IG 抓取（session cookie / OAuth token）
- [x] PostgreSQL + Video / Snapshot ORM
- [x] OAuth 登入 + cookie session（instagram_business_basic scope）
- [x] /api/videos GET / POST 接真實 DB
- [x] 前端 StatsGrid 總覽
- [ ] /api/videos DELETE + refresh 端點（穎禾）
- [ ] 影片卡 UI 美化（穎禾）
- [ ] 自動 Reels 清單（紘陞）
- [ ] 排程自動刷新（紘陞）
- [ ] 趨勢折線圖（紘陞）

## 分工

| 階段 | 負責人 | 狀態 |
|------|--------|------|
| 1 | 曹哲維 (PM) | ✅ 骨架 + OAuth 雛形 + 假資料 API |
| 2 | 陳晶晶 | ✅ IG 抓取、DB ORM、auth 補完、StatsGrid |
| 3 | 施穎禾 | 進行中 — CRUD 完整 + UI 美化 |
| 4 | 王紘陞 | 排程 — Reels 自動清單 + cron + 折線圖 |

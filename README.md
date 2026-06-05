# IG Reel Tracker

期末專題：追蹤 Instagram Reels 數據（讚數、留言、播放）的 web app。

## 功能特色

- **Instagram OAuth 登入**：支援使用 IG Business 帳號登入並取得長期 token
- **自動 Reels 清單**：登入後一鍵看到帳號下所有 Reels + 流量
- **跨平台合計播放**：IG 後台只看得到 IG 播放數據，本專案會合計 IG + FB 數據
- **手動追蹤**：貼任意 IG Reels 連結就能加入追蹤清單
- **歷史快照與趨勢圖**：每次刷新會建立一筆快照並且可以透過折線圖看到趨勢
- **CSV 匯出**：一鍵下載所有追蹤影片的數據
- **自動排程**：Vercel Cron 每 6 小時批次刷新


## 技術架構

### 前端
- Next.js 16 (App Router) + React 19
- Tailwind CSS 4 + shadcn/ui (base-nova)
- Recharts 折線圖
- Lucide React icons
- TypeScript 5

### 後端
- FastAPI (Python 3.12+)
- SQLAlchemy 2.0 ORM
- PostgreSQL 16 (Docker Compose)
- httpx + ThreadPoolExecutor 平行抓取數據


## 資料庫設計

```
┌──────────────────┐         ┌──────────────────┐
│      Video       │  1:N    │     Snapshot     │
├──────────────────┤  ────►  ├──────────────────┤
│ id (PK)          │ CASCADE │ id (PK)          │
│ platform "IG"    │         │ videoId (FK)     │
│ shortcode (UQ)   │         │ views (合計)      │
│ mediaId          │         │ igViews / fbViews│
│ username         │         │ likes / comments │
│ caption          │         │ shares           │
│ uploadedAt       │         │ scrapedAt        │
│ createdAt        │         └──────────────────┘
└──────────────────┘
```


## API 端點

| Method | Path | 說明 |
|--------|------|------|
| `GET` | `/api/auth/instagram` | 導向 IG 授權頁面 |
| `GET` | `/api/auth/callback` | OAuth callback，交換長期 oken |
| `GET` | `/api/auth/me` | 取得目前登入用戶 |
| `POST` | `/api/auth/logout` | 登出 |
| `GET` | `/api/videos` | 獲取所有追蹤影片（含最新快照） |
| `POST` | `/api/videos` | 新增追蹤影片（傳入 `{url}`） |
| `GET` | `/api/videos/{id}` | 獲取單一追蹤影片|
| `DELETE` | `/api/videos/{id}` | 取消追蹤影片 |
| `POST` | `/api/videos/{id}/refresh` | 刷新並建立快照 |
| `GET` | `/api/videos/export.csv` | CSV 匯出 |
| `GET` | `/api/reels` | 取得登入用戶的所有 Reels 資訊 |
| `GET` | `/api/cron` | 排程觸發刷新 |

---

## 本地啟動方式

### 1. 環境變數

```bash
cp .env.example .env
# 編輯 .env 填入：
#   INSTAGRAM_APP_ID / SECRET 
#   IG_SESSION_ID / IG_CSRF_TOKEN
#   CRON_SECRET 
```

- IG_APP_ID / SECRET ：到 [Meta for Developers](https://developers.facebook.com/) 申請
- IG_SESSION_ID / IG_CSRF_TOKEN：瀏覽器登入 IG 後開啟 DevTools → Application → Cookies → `instagram.com` 複製 `sessionid` 跟 `csrftoken` 的值



### 2. 啟動後端程式與資料庫

```bash
docker compose up -d
```

第一次啟動會自動把 `Video` / `Snapshot` 表建出來。

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

開瀏覽器 → http://localhost:3000

### 4. OAuth 登入
因為IG OAuth callback 須要一個公開可訪問的 URL，開發時可以使用 [ngrok](https://ngrok.com/) 暴露本地端口：
```bash
ngrok http 3000
```
於Mata for Developers 的 IG App 設定中，將 OAuth callback URL 設為 `https://<ngrok-url>/api/auth/callback`。
修改 `.env` 的 `NEXT_PUBLIC_BASE_URL` 為 ngrok 提供的 URL，
修改 `frontend/next.config.ts` 的 `allowedDevOrigins` 加入 ngrok 提供的 URL，重新啟動前端即可。


## 專案結構

```
Web-design/
├── backend/                       # 後端專案
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # 環境變數管理
│   ├── database.py                # SQLAlchemy engine
│   ├── models.py                  # Video / Snapshot ORM
│   ├── schemas.py                 # Pydantic 回傳格式
│   ├── Dockerfile                 # 後端 Dockerfile
│   ├── routers/
│   │   ├── auth.py                # OAuth 登入流程
│   │   ├── videos.py              # 影片CRUD處理 / 刷新 / CSV匯出
│   │   ├── reels.py               # 自動顯示清單
│   │   └── cron.py                # 排程刷新
│   └── services/
│       └── instagram.py           # IG 資料抓取
│
├── frontend/                      # 前端專案
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx               # 主頁
│   │   └── globals.css            # Tailwind 4
│   ├── components/
│   │   ├── AddVideoForm.tsx       # 新增影片網址表單
│   │   ├── VideoCard.tsx          # 影片資料卡
│   │   ├── StatsGrid.tsx          # 統計資料
│   │   ├── MetricsChart.tsx       # 趨勢折線圖
│   │   ├── ReelsList.tsx          # Reels 清單
│   │   └── ui/                    
│   ├── lib/utils.ts               
│   ├── types/index.ts             
│   ├── next.config.ts             # rewrites /api/* → 8000
│   └── vercel.json                # cron schedule
│
├── docker-compose.yml             
└── .env.example
```

## 分工

| 階段 | 負責人 | 說明 |
|------|--------|------|
| 1 | 曹哲維 (PM) | 專案骨架、OAuth 雛形、假資料 API|
| 2 | 陳晶晶 | SQLAlchemy ORM、IG 資料抓取、OAuth細節、StatsGrid |
| 3 | 施穎禾 | Videos CRUD/refresh/CSV、Tailwind+shadcn整套、VideoCard、RWD |
| 4 | 王翃陞 | Reels 自動清單、cron 排程、MetricsChart 折線圖、整合 README |

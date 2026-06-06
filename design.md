# 系統設計

## 系統目的

追蹤 Instagram Reels 的互動數據，記錄每支影片的基本資料以及每次抓取的快照（觀看數、讚數、留言數等），以便繪製歷史趨勢圖表與彙總統計。

欄位設計包含

- 影片基本資料（shortcode、媒體 ID、發文者、貼文說明、發布時間）
- 互動數據快照（總觀看數、IG 觀看數、FB 觀看數、讚數、留言數、分享數）
- 每次抓取的時間戳記

## 資料庫設計

### 資料表

### videos 資料表

| 欄位名稱 | 資料型態 | 必填 | 鍵 | 說明 |
|---|---|---|---|---|
| id | VARCHAR(25) (CUID) | 是 | 主鍵(PK) | 主鍵，由 SQLAlchemy 以 UUID 產生 |
| shortcode | VARCHAR(50) | 是 | 唯一鍵(UQ) | Instagram 短碼（URL 中提取） |
| media_id | VARCHAR(50) | 是 |  | Instagram 媒體 ID |
| username | VARCHAR(100) | 是 |  | 發文者帳號 |
| caption | TEXT | 否 |  | 貼文說明 |
| views | BIGINT | 是 |  | 總觀看數 |
| ig_views | BIGINT | 是 |  | Instagram 觀看數 |
| fb_views | BIGINT | 是 |  | Facebook 觀看數 |
| likes | BIGINT | 是 |  | 按讚數 |
| comments | BIGINT | 是 |  | 留言數 |
| shares | BIGINT | 是 |  | 分享數 |
| scraped_at | DATETIME | 是 |  | 資料抓取時間 |
| uploaded_at | DATETIME | 是 |  | 影片在 IG 上的發布時間 |
| created_at | DATETIME | 是 |  | 加入追蹤的時間 |

例如

| id | shortcode | username | views | ig_views | fb_views | likes | scraped_at | uploaded_at |
|---|---|---|---|---|---|---|---|---|
| cuid_a | DLxAbCdEf | bob | 1500 | 1000 | 500 | 80 | 2026-05-26 06:00 | 2026-05-25 12:00 |
| cuid_b | DLxAbCdEf | alice | 1850 | 1200 | 650 | 95 | 2026-05-26 12:00 | 2026-05-25 12:00 |
| cuid_c | DLyZyXwVu | bob | 3200 | 2200 | 1000 | 210 | 2026-05-26 12:00 | 2026-05-24 09:00 |

嘗試正規化資料表

- 1NF: 每個欄位是不可再分的單一值（沒有違反）
- 2NF: 所有非主鍵都必須相依整個主鍵（沒有違反）
- 3NF: 所有非主鍵不能相依其它非主鍵（**違反**）
  - `shortcode`、`media_id`、`username`、`caption`、`uploaded_at` 屬於影片本體資料，不會隨時間改變，但每次抓取快照都必須重複寫入一份
  - 這些欄位都相依於 `shortcode`（同一支影片永遠對應同一個 `media_id`、`username`、`uploaded_at`），而非相依於主鍵 `id`
  - 同時 `views` 本質上是 `ig_views + fb_views` 的衍生欄位，因此可由其它非主鍵計算而來

因此將原本的單一資料表拆成兩張，分離「影片本體」與「每次抓取的快照」：

### videos 資料表

| 欄位名稱 | 資料型態 | 必填 | 鍵 | 說明 |
|---|---|---|---|---|
| id | VARCHAR(25) (CUID) | 是 | 主鍵(PK) | 主鍵，由 SQLAlchemy 以 UUID 產生 |
| shortcode | VARCHAR(50) | 是 | 唯一鍵(UQ) | Instagram 短碼（URL 中提取） |
| media_id | VARCHAR(50) | 是 |  | Instagram 媒體 ID |
| username | VARCHAR(100) | 是 |  | 發文者帳號 |
| caption | TEXT | 否 |  | 貼文說明 |
| uploaded_at | DATETIME | 是 |  | 影片在 IG 上的發布時間 |
| created_at | DATETIME | 是 |  | 加入追蹤的時間 |

### snapshots 資料表

| 欄位名稱 | 資料型態 | 必填 | 鍵 | 說明 |
|---|---|---|---|---|
| id | VARCHAR(25) (CUID) | 是 | 主鍵(PK) | 主鍵，由 SQLAlchemy 以 UUID 產生 |
| video_id | VARCHAR(25) | 是 | 外鍵(videos.id) | 對應的影片（CASCADE） |
| views | BIGINT | 是 |  | 總觀看數 |
| ig_views | BIGINT | 是 |  | Instagram 觀看數 |
| fb_views | BIGINT | 是 |  | Facebook 觀看數 |
| likes | BIGINT | 是 |  | 讚數 |
| comments | BIGINT | 是 |  | 留言數 |
| shares | BIGINT | 是 |  | 分享數 |
| scraped_at | DATETIME | 是 |  | 資料抓取時間 |

例如

#### videos

| id | shortcode | media_id | username | uploaded_at |
|---|---|---|---|---|
| cuid_v1 | DLxAbCdEf | 3567890... | bob | 2026-05-25 12:00 |
| cuid_v2 | DLyZyXwVu | 3567891... | alice | 2026-05-24 09:00 |

#### snapshots

| id | video_id | views | ig_views | fb_views | likes | scraped_at |
|---|---|---|---|---|---|---|
| cuid_s1 | cuid_v1 | 1500 | 1000 | 500 | 80 | 2026-05-26 06:00 |
| cuid_s2 | cuid_v1 | 1850 | 1200 | 650 | 95 | 2026-05-26 12:00 |
| cuid_s3 | cuid_v2 | 3200 | 2200 | 1000 | 210 | 2026-05-26 12:00 |

## 關聯說明

- 一支 `video` 對應多筆 `snapshot`（1:N）
- 刪除 `video` 時，所屬的 `snapshot` 透過 `ON DELETE CASCADE` 一併刪除
- 取得單支影片的歷史趨勢時，以 `video_id` 查詢 `snapshots` 並依 `scraped_at` 排序

# API設計

### 認證管理

#### 1. 導向至 Instagram 登入

- 端點: `GET /api/auth/instagram`
- 參數: N/A (伺服器帶固定的認證參數)
- 狀態碼: 307 Temporary Redirect
- 回應: 重新導向至 `https://www.instagram.com/oauth/authorize?{params}`

#### 2. OAuth callback

- 端點: `GET /api/auth/callback`
- 參數:
  - `code: str (Query，由 Instagram 帶入)`
  - `error: str (Query，選填，授權失敗時由 Instagram 帶入)`
- 狀態碼: 307 Temporary Redirect
- 回應:
  - 成功時設定兩個 Cookie 並重新導向至首頁 `/`
    - `ig_access_token`：HTTP-only，有效期 60 天
    - `ig_user`：公開 Cookie，
  - 失敗時重新導向至 `/?error=ig_auth_failed` 或 `/?error=token_exchange_failed`
  - 回應範例（`ig_access_token` Cookie內容）
    ```json
    {
      "access_token": "IGQVJ...ZDZD",
    }
    ```
  - 回應範例（`ig_user`Cookie內容）
    ```json
    {
      "id": "17841400000000000",
      "username": "example_user"
    }
    ```

#### 3. 取得目前登入的使用者資訊

- 端點: `GET /api/auth/me`
- 參數: N/A
- 狀態碼: 200 OK
- 回應: `IgUser | null`
  - IgUser 物件欄位
    - `id: str`
    - `username: str`
  - 回應範例
    ```json
    {
      "id": "17841400000000000",
      "username": "example_user"
    }
    ```

#### 4. 登出

- 端點: `POST /api/auth/logout`
- 參數: N/A
- 狀態碼: 200 OK
- 回應: 清除 `ig_access_token` 及 `ig_user` Cookie
  - 回應範例
    ```json
    {
      "ok": true
    }
    ```

### 影片管理

#### 1. 列出所有追蹤影片

- 端點: `GET /api/videos`
- 參數: N/A
- 狀態碼: 200 OK
- 回應: `VideoOut`
  - VideoOut 物件欄位
    - `id: str`
    - `shortcode: str`
    - `mediaId: str | null`
    - `username: str | null`
    - `caption: str | null`
    - `uploadedAt: str | null`
    - `createdAt: str | null`
    - `latestSnapshot: SnapshotOut | null`
  - 回應範例
    ```json
    [
      {
        "id": "clx1234567890abcdef",
        "shortcode": "DLxAbCdEfGh",
        "mediaId": "3567890123456789",
        "username": "example_user",
        "caption": "這是一支測試 Reel #reels",
        "uploadedAt": "2026-05-25T12:00:00",
        "createdAt": "2026-05-26T06:00:00",
        "latestSnapshot": {
          "id": "clx0987654321zyxwvu",
          "videoId": "clx1234567890abcdef",
          "views": 1500,
          "igViews": 1000,
          "fbViews": 500,
          "likes": 80,
          "comments": 12,
          "shares": 5,
          "scrapedAt": "2026-05-26T06:00:00"
        }
      }
    ]
    ```

#### 2. 新增追蹤影片

- 端點: `POST /api/videos`
- 參數:
  - Request Body (JSON)
    - `url: str (必填)`
- 狀態碼:
  - 200 OK
  - 400 Bad Request：無效的 Instagram 連結
  - 409 Conflict：此影片已在追蹤清單中
  - 502 Bad Gateway：無法從 Instagram 抓取影片資訊
- 回應: `VideoOut`
  - VideoOut 物件欄位
    - `id: str`
    - `shortcode: str`
    - `mediaId: str | null`
    - `username: str | null`
    - `caption: str | null`
    - `uploadedAt: str | null`
    - `createdAt: str | null`
    - `latestSnapshot: SnapshotOut | null`
  - 回應範例
    ```json
    {
      "id": "clx1234567890abcdef",
      "shortcode": "DLxAbCdEfGh",
      "mediaId": "3567890123456789",
      "username": "example_user",
      "caption": "這是一支測試 Reel #reels",
      "uploadedAt": "2026-05-25T12:00:00",
      "createdAt": "2026-05-26T06:00:00",
      "latestSnapshot": {
        "id": "clx0987654321zyxwvu",
        "videoId": "clx1234567890abcdef",
        "views": 1500,
        "igViews": 1000,
        "fbViews": 500,
        "likes": 80,
        "comments": 12,
        "shares": 5,
        "scrapedAt": "2026-05-26T06:00:00"
      }
    }
    ```

#### 3. 匯出所有影片 CSV

- 端點: `GET /api/videos/export.csv`
- 參數: N/A
- 狀態碼: 200 OK
- 回應: 下載 `videos.csv` 檔案，Content-Type: text/csv
  - CSV 欄位依序為：`shortcode`, `username`, `caption`, `views`, `igViews`, `fbViews`, `likes`, `comments`, `shares`, `uploadedAt`, `scrapedAt`
  - 每列為對應影片的最新一筆快照數據

#### 4. 取得單一影片（含完整快照歷史）

- 端點: `GET /api/videos/{video_id}`
- 參數:
  - `video_id: str (Path，必填)`
- 狀態碼:
  - 200 OK
  - 404 Not Found
- 回應: `VideoOut`
  - VideoOut 物件欄位
    - `id: str`
    - `shortcode: str`
    - `mediaId: str | null`
    - `username: str | null`
    - `caption: str | null`
    - `uploadedAt: str | null`
    - `createdAt: str | null`
    - `latestSnapshot: SnapshotOut | null`
  - 回應範例
    ```json
    {
      "id": "clx1234567890abcdef",
      "shortcode": "DLxAbCdEfGh",
      "mediaId": "3567890123456789",
      "username": "example_user",
      "caption": "這是一支測試 Reel #reels",
      "uploadedAt": "2026-05-25T12:00:00",
      "createdAt": "2026-05-26T06:00:00",
      "latestSnapshot": {
        "id": "clx0987654321zyxwvu",
        "videoId": "clx1234567890abcdef",
        "views": 1850,
        "igViews": 1200,
        "fbViews": 650,
        "likes": 95,
        "comments": 15,
        "shares": 7,
        "scrapedAt": "2026-05-26T12:00:00"
      },
      "snapshots": [
        {
          "id": "clx0000000000000001",
          "videoId": "clx1234567890abcdef",
          "views": 1500,
          "igViews": 1000,
          "fbViews": 500,
          "likes": 80,
          "comments": 12,
          "shares": 5,
          "scrapedAt": "2026-05-26T06:00:00"
        },
        {
          "id": "clx0987654321zyxwvu",
          "videoId": "clx1234567890abcdef",
          "views": 1850,
          "igViews": 1200,
          "fbViews": 650,
          "likes": 95,
          "comments": 15,
          "shares": 7,
          "scrapedAt": "2026-05-26T12:00:00"
        }
      ]
    }
    ```

#### 5. 刪除追蹤影片

- 端點: `DELETE /api/videos/{video_id}`
- 參數:
  - `video_id: str (Path，必填)`
- 狀態碼:
  - 200 OK
  - 404 Not Found
- 回應:
  - 回應範例
    ```json
    { "ok": true }
    ```

#### 6. 手動刷新影片快照

- 端點: `POST /api/videos/{video_id}/refresh`
- 參數:
  - `video_id: str (Path，必填)`
- 狀態碼:
  - 200 OK
  - 404 Not Found
  - 502 Bad Gateway
- 回應: `SnapshotOut`
  - SnapshotOut 物件欄位
    - `id: str`
    - `videoId: str`
    - `views: number | null`
    - `igViews: number | null`
    - `fbViews: number | null`
    - `likes: number | null`
    - `comments: number | null`
    - `shares: number | null`
    - `scrapedAt: str`
  - 回應範例
    ```json
    {
      "id": "clx1111111111111111",
      "videoId": "clx1234567890abcdef",
      "views": 2100,
      "igViews": 1400,
      "fbViews": 700,
      "likes": 110,
      "comments": 18,
      "shares": 9,
      "scrapedAt": "2026-05-27T06:00:00"
    }
    ```

### Reels 列表

#### 1. 取得目前登入使用者的 Reels

- 端點: `GET /api/reels`
- 參數:
  - Cookie `ig_access_token`（必填，由登入流程自動設定）
- 狀態碼:
  - 200 OK：查詢成功
  - 401 Unauthorized：尚未登入
  - 400 Bad Request：存取 Token 無效或已過期
- 回應: `ReelOut`
  - ReelOut 物件欄位
    - `id: str`
    - `shortcode: str`
    - `caption: str | null`
    - `timestamp: str`
    - `permalink: str`
    - `thumbnailUrl: str | null`
    - `plays: number | null`）
    - `igViews: number | null`
    - `fbViews: number | null`
    - `likes: number | null`
    - `comments: number | null`
    - `shares: number | null`
  - 回應範例
    ```json
    [
      {
        "id": "3567890123456789",
        "shortcode": "DLxAbCdEfGh",
        "caption": "這是一支測試 Reel #reels",
        "timestamp": "2026-05-25T12:00:00+0000",
        "permalink": "https://www.instagram.com/reel/DLxAbCdEfGh/",
        "thumbnailUrl": "https://example.com/thumbnail.jpg",
        "plays": 1500,
        "igViews": 1000,
        "fbViews": 500,
        "likes": 80,
        "comments": 12,
        "shares": 5
      }
    ]
    ```

### 排程更新

#### 1. 刷新所有追蹤影片（Cron Job）

- 端點: `GET /api/cron`
- 參數:
  - Header `Authorization: Bearer <CRON_SECRET>` (必填)
- 狀態碼:
  - 200 OK
  - 401 Unauthorized
- 回應:
  - `refreshed: number`
  - `results: Array<{shortcode, ok, error?}>`
  - 回應範例
    ```json
    {
      "refreshed": 2,
      "results": [
        { "shortcode": "DLxAbCdEfGh", "ok": true },
        { "shortcode": "DLyZyXwVuTs", "ok": true }
      ]
    }
    ```
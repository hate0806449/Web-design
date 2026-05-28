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

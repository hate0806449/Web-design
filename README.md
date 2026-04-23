# IG Reel Tracker

期末專題：追蹤 Instagram Reels 數據（讚數、留言、播放）的小型 web app。

## 技術棧（暫定）

- 前端：Next.js + React
- 後端：FastAPI (Python)
- DB：PostgreSQL（docker compose）
- 抓取：Instagram Graph API + 自己刻 scraping

## TODO

- [ ] IG OAuth 登入流程跑通
- [ ] DB schema 確定
- [ ] 真的把 IG 數據抓下來（先 hardcode 假資料 demo）
- [ ] UI 美化 + RWD
- [ ] 自動排程刷新

## 分工

| 階段 | 負責人 | 主題 |
|------|--------|------|
| 1 | 曹哲維 (PM) | 專案骨架、OAuth 雛形、假資料 API |
| 2 | 陳晶晶 | IG 抓取服務、DB 串接 |
| 3 | 施穎禾 | 影片管理 CRUD、UI 美化 |
| 4 | 王紘陞 | Reels 自動列表、排程、整合 |

---

更詳細的啟動方式之後補。

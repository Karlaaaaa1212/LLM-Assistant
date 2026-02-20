# AI Personal Assistant Telegram Bot

這是一個結合 OpenAI API 與 Google Workspace (Gmail & Calendar) 的 Telegram 個人助理機器人。本專案旨在自動化日常資訊處理，除了提供文本的摘要、改寫與翻譯功能外，亦能串接使用者的信箱與行事曆，透過 AI 進行語意分析，生成結構化的每日信件重點與每週行程摘要。

## 核心功能

* **文本處理 (Text Processing)**
  * 摘要 (Summarize)：將長篇文字濃縮成 3 句話內的重點與結論。
  * 改寫 (Rewrite)：將輸入的文字改寫為學術期刊論文的正式風格，並保持語法自然流暢。
  * 翻譯 (Translate)：將外文精準翻譯為正式風格的繁體中文。

* **Gmail 智慧摘要 (Gmail Integration)**
  * 自動抓取過去 24 小時（若無則自動往前回溯 7 天）的最新信件。
  * 透過 OpenAI 分析信件脈絡，輸出 JSON 格式的結構化資料，包含：重點脈絡摘要、最重要信件標記、需回覆清單、待辦事項 (Task, Who, Urgency) 以及潛在風險提醒。

* **Calendar 行程助理 (Calendar Integration)**
  * 自動抓取未來 7 天的 Google Calendar 行程。
  * 透過 OpenAI 分析行程安排，統整出：本週主題與壓力點摘要、Top 3 關鍵事件、行程衝突與緊湊度警告、每日專注重點，以及具體的行前準備建議。

## 技術棧 (Tech Stack)

* **開發語言**：Python 3
* **機器人介面**：Telegram Bot API (`python-telegram-bot`)
* **AI 語言模型**：OpenAI API (`gpt-4o-mini`)
* **第三方 API 整合**：Google Gmail API, Google Calendar API (`google-api-python-client`)

## 快速開始 (Getting Started)

### 1. 系統需求與套件安裝
請確認開發環境已安裝 Python 3，並於終端機執行以下指令安裝所需套件：

```bash
pip install python-telegram-bot openai google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv

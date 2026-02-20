# AI Personal Assistant Telegram Bot 

這是一個結合 OpenAI API 與 Google Workspace (Gmail & Calendar) 的 Telegram 個人助理機器人。它可以幫助使用者快速處理日常文本（摘要、改寫、翻譯），並能自動讀取使用者的信箱與行事曆，透過 AI 生成專屬的每日信件重點與每週行程摘要。

##  核心功能 

* ** 文本處理 (Text Processing)**
  * 摘要 (Summarize)：將長篇文字濃縮成 3 句話內的重點與結論。
  * 改寫 (Rewrite)：將輸入的文字改寫為「學術期刊論文」的正式風格，並保持語氣自然。
  * 翻譯 (Translate)：將外文精準翻譯為正式風格的繁體中文。
* ** Gmail 智慧摘要 (Gmail Integration)**
  * 自動抓取過去 24 小時（或 7 天）內的最新信件。
  * 透過 OpenAI 分析信件脈絡，統整出：重點脈絡摘要、最重要信件、需回覆清單、待辦事項 (Task, Who, Urgency)，以及潛在風險提醒。
* ** Calendar 行程助理 (Calendar Integration)**
  * 自動抓取未來 7 天的 Google Calendar 行程。
  * 透過 OpenAI 分析行程，統整出：本週主題與壓力點摘要、Top 3 重要事件、行程衝突/太趕的警告、每日專注重點，以及具體的行前準備建議。

##  技術棧 (Tech Stack)

* **語言**：Python 3
* **介面**：Telegram Bot API (`python-telegram-bot`)
* **AI 引擎**：OpenAI API (`gpt-4o-mini`)
* **第三方服務整合**：Google Gmail API, Google Calendar API (`google-api-python-client`)

##  快速開始 (Getting Started)

### 1. 系統需求與套件安裝
請確認你的環境已安裝 Python，並執行以下指令安裝所需套件：
```bash
pip install python-telegram-bot openai google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv

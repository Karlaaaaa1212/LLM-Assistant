from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI
from utils import summarize, rewrite, translate
import json

from utils import get_google_service
from utils import fetch_emails, build_email_pack, summarize_gmail
from utils import fetch_event, build_event_pack, summarize_calendar

BTN_SUM = "摘要"
BTN_REWRITE = "改寫"
BTN_TRANS = "翻譯"    
BTN_GMAIL = "Gmail 摘要"
BTN_CAL   = "Calendar 摘要"

keyboard = ReplyKeyboardMarkup(
    [
        [BTN_SUM, BTN_REWRITE, BTN_TRANS],
        [BTN_GMAIL, BTN_CAL]
    ], 
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_action"]= None
    await update.message.reply_text("選一個功能開始吧！", reply_markup=keyboard)




TG_BOT_TOKEN = "請填入你的_Telegram_Bot_Token"
OPENAI_API_KEY = "請填入你的_OpenAI_API_Key"  
client = OpenAI(api_key= OPENAI_API_KEY)

CREDENTIALS = "credentials.json"
GMAIL_TOKEN = "token_gmail.json"
CAL_TOKEN   = "token_calendar.json"   
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CAL_SCOPES   = ["https://www.googleapis.com/auth/calendar.readonly"]

gmail = get_google_service("gmail", "v1", GMAIL_SCOPES, credentials_path=CREDENTIALS, token_path=GMAIL_TOKEN)
cal   = get_google_service("calendar", "v3", CAL_SCOPES, credentials_path=CREDENTIALS, token_path=CAL_TOKEN)

async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == BTN_SUM:
        context.user_data["waiting_action"]= "summarize"
        await update.message.reply_text("好，請貼上你想摘要的文字")
        return 
    if choice == BTN_REWRITE:
        context.user_data["waiting_action"]= "rewrite"
        await update.message.reply_text("好，請貼上你想改寫的文字", reply_markup= keyboard)
        return          
    if choice == BTN_TRANS:
        context.user_data["waiting_action"]= "translate"
        await update.message.reply_text("好，請貼上你想翻譯的文字", reply_markup= keyboard)
        return 
    context.user_data["waiting_action"]= None
    if choice == BTN_GMAIL:
        await update.message.reply_text("收到，正在幫你整理 Gmail 信件...")
        my_query = "newer_than:1d"
        emails = fetch_emails(gmail, my_query, 10)
    
        if not emails:
            await update.message.reply_text("這個query抓不到信，先改用newer_than:7d測試")
            emails = fetch_emails(gmail,"newer_than:7d", 10)   

        email_pack = build_email_pack(emails)
        gmail_json_str = summarize_gmail(client, email_pack)    
        gmail_data = json.loads(gmail_json_str)
        await update.message.reply_text(gmail_data['summary'])
        return
    if choice == BTN_CAL:
        await update.message.reply_text("收到，正在幫你整理 Google Calendar 事件...")
        events = fetch_event(cal, days=7, max_results=20)
        if not events:
            await update.message.reply_text("這個query抓不到事件，請確認你的行事曆裡有未來一週的事件")   
            return

        event_pack = build_event_pack(events)
        cal_digest_json = summarize_calendar(client, event_pack)
        cal_data = json.loads(cal_digest_json)    
        await update.message.reply_text(cal_data["week_summary"])
        return



async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    action = context.user_data.get("waiting_action")
    if not action:
        await update.message.reply_text("請先輸入 /summarize /rewrite /translate")
        return

    text = update.message.text
    if action == "summarize":
        result = summarize(client= client, text=text)
    elif action == "rewrite":
        result = rewrite(client= client, text=text)
    elif action == "translate":
        result = translate(client= client, text=text)
    else:
        result = "我不認得這個指令，請重新輸入 /summarize /rewrite /translate"
    await update.message.reply_text(result)
    context.user_data["waiting_action"] = None





def main():
    app = ApplicationBuilder().token(TG_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler( 
            filters.Regex(f"^{BTN_SUM}|{BTN_REWRITE}|{BTN_TRANS}|{BTN_GMAIL}|{BTN_CAL}$"),    
            choose_mode
        )
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
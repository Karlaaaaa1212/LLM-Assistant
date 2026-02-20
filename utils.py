def summarize(client, text, max_sentences=3):
    prompt = f"""用{max_sentences}句話摘要以下文字，把重點放在內容＆結論 \n
                --- \n 
                {text}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    summarized_text = response.choices[0].message.content
    return summarized_text

def rewrite(client, text, style="學術期刊論文", max_sentences = 5):
    prompt = f"""請改寫以下文字，保持原本意思不變。
                 改寫風格為「{style}」，請用 {max_sentences} 句話改寫
                 請注意要讓寫出來的句子自然，不要像是 AI 寫的
                --- \n 
                {text}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    rewritten_text = response.choices[0].message.content
    return rewritten_text

def translate(client, text, language='英文', style="正式"):
    prompt = f"""請翻把以下文字翻譯為{language}，翻譯風格為「{style}」
                翻譯時請保持原意，語氣自然、注意文法，並符合一般書面使用情境
                --- \n 
                {text}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    translated_text = response.choices[0].message.content
    return translated_text

from typing import List, Dict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

def get_google_service(
    api_name: str,
    api_version: str,
    scopes: List[str],
    credentials_path: str = "credentials.json",
    token_path: str = "token.json"
):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    service = build(api_name, api_version, credentials=creds)
    return service

def list_messages(
    service,
    query: str,
    max_results: int = 10
) -> List[str]:
    resp = service.users().messages().list(
        userId = "me",
        q=query,
        maxResults=max_results
    ).execute()

    # {
    #     "messages": [
    #         {"id": "...", "threadId": "..."}
    #     ]
    # }
    return [m["id"] for m in resp.get("messages", [])]

def get_messages_brief(
    service, 
    msg_id: str,
) -> Dict:
    msg = service.users().messages().get(
        userId="me",
        id=msg_id,
        format="metadata",
        metadataHeaders=["From", "Subject", "Date"]
    ).execute()

    headers = {h["name"]: h["value"] 
               for h in msg.get("payload", {}).get("headers", [])} #msg["payload"]["headers"]
    # {
    # "From": "...",
    # "Subject": "..."
    # }
    snippet = msg.get("snippet", "")

    return {
        "id": msg_id,
        "from": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "snippet": snippet
    }

def fetch_emails(
    service,
    query: str,
    max_results: int = 10
) -> List[Dict]:
    
    ids = list_messages(service, query, max_results)
    return [get_messages_brief(service, mid) for mid in ids]

from datetime import datetime, timezone, timedelta

def fetch_event(
    service, 
    days: int = 7,
    max_results: int = 20,
    calendar_id: str = "primary"
) -> List[Dict[str, str]]:
    
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=days)).isoformat()

    resp = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime",
        maxResults=max_results
    ).execute()

    events = []
    for e in resp.get("items", []):
        start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date", "")
        end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date", "")

        events.append({
            "id": e.get("id", ""),
            "title": e.get("summary", ""),
            "start": start,
            "end": end,
            "location": e.get("location", ""),
            "description": e.get("description", ""),
        }) 
    return events

from openai import OpenAI

def build_email_pack(
    emails: List[Dict[str, str]],
    max_emails: int = 8
) -> str:
    emails = emails[:max_emails]
    blocks = []

    for i, e in enumerate(emails, 1):
        blocks.append(
            f"""[Email {i}] (id={e.get('id', '')})
            From: {e.get('from', '')}
            Subject: {e.get('subject', '')}
            Date: {e.get('date', '')}
            Snippet: {e.get('snippet', '')}
            """
        )
    return "\n".join(blocks)

def summarize_gmail(
    client: OpenAI,
    email_pack: str
) -> str:
    
    prompt = f"""
    你是工作助理，請把以下 Gmail 信件整理成 JSON（繁體中文）：

    JSON 欄位：
    - summary: 5~8 行，整理今天的主要訊息脈絡（不要逐封照抄）
    - important: 最重要的 1~3 封信（用 "Email 1" 這種編號）
    - need_reply: 需要回覆的信（用 Email 編號陣列）
    - todo: 待辦事項陣列，每個 item 包含：
        - task: 要做什麼
        - who: 跟誰有關（寄件者或對象）
        - urgency: low/medium/high
    - risks: 你覺得可能會出事或需要注意的點（陣列，可空）

    信件如下：
    ---
    {email_pack}
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    return resp.choices[0].message.content
    
def build_event_pack(
    events: List[Dict[str, str]],
    max_events: int = 20
) -> str:
    events = events[:max_events]
    blocks = []

    for i, ev in enumerate(events, 1):
        blocks.append(
            f"""[Event {i}] (id={ev.get('id','')})
            Title: {ev.get('title','')}
            Time: {ev.get('start','')} ~ {ev.get('end','')}
            Location: {ev.get('location','')}
            Desc: {ev.get('description','')}
            """
        )
    return "\n".join(blocks)

def summarize_calendar(
    client: OpenAI,
    event_pack: str    
) -> str:
    prompt = f"""
    你是行程助理，請把以下行程整理成 JSON（繁體中文）：

    JSON 欄位：
    - week_summary: 5~10 行摘要（重點是本週主題與壓力點）
    - top3: 最重要的三個事件（用 Event 編號陣列）
    - conflicts: 可能衝突/太趕的地方（陣列，可空）
    - daily_focus: 以 Mon~Sun 為 key 的 dict，每天一句提醒
    - prep_tips: 行前準備建議（陣列，具體一點）

    行程如下：
    ---
    {event_pack}
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    return resp.choices[0].message.content


    








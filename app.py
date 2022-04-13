import os
import uvicorn

from fastapi import FastAPI, Request, Header, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage


app = FastAPI()

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


@app.get('/')
def index():
    return {'line': os.getenv('LINE_BOT_BASIC_ID')}


@app.post('/webhook')
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print('text-event', event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='กรุณาอัพโหลดรูป')
    )


@handler.add(MessageEvent, message=ImageMessage)
def message_text(event):
    print('image-event', event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='อัพโหลดรูปสำเร็จ')
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
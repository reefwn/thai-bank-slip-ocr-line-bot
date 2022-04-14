import os
import pickle
import uvicorn
import numpy as np
import tensorflow as tf

from PIL import Image
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from fastapi import FastAPI, Request, Header, HTTPException
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage


app = FastAPI()

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
s3_public = os.getenv('AWS_S3_PUBLIC_PATH')

classification_model = tf.keras.models.load_model('./models/bank_classification_model.h5')
classification_labels = pickle.loads(open('./models/bank_classification_labels.pickle', 'rb').read())


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

    # save image to file
    message_content = line_bot_api.get_message_content(event.message.id)
    with open('./image.png', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # load image
    img = Image.open('./image.png').resize((180, 180))
    img = np.array(img)

    # predict bank
    pred = classification_model.predict(img[None, :, :])
    pred_prob = tf.nn.softmax(pred).numpy()

    messages = []
    messages.append('bank = {}'.format(classification_labels[np.argmax(pred_prob)]))
    messages.append('probability = {}'.format(np.max(pred_prob)))

    raw_output = {}
    for c in range(len(classification_labels)):
        raw_output[classification_labels[c]] = pred_prob[0][c]
    messages.append('raw = {}'.format(raw_output))

    for i in range(len(messages)):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=messages[i])
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
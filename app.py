import os
import cv2
import pickle
import uvicorn
import pytesseract
import numpy as np
import tensorflow as tf

from fn import get_ocr_locations
from PIL import Image
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from fastapi import FastAPI, Request, Header, HTTPException
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage


app = FastAPI()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

classification_model = tf.keras.models.load_model("./models/bank_classification_model.h5")
classification_labels = pickle.loads(open("./models/bank_classification_labels.pickle", "rb").read())


@app.get("/")
def index():
    return {"line": os.getenv("LINE_BOT_BASIC_ID")}


@app.post("/webhook")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print("text-event", event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="กรุณาอัพโหลดรูป")
    )


@handler.add(MessageEvent, message=ImageMessage)
def message_text(event):
    print("image-event", event)

    # save image to file
    message_content = line_bot_api.get_message_content(event.message.id)
    with open("./image.png", "wb") as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    # load image for classification
    img = Image.open("./image.png").resize((180, 180))
    img = np.array(img)

    # predict bank
    pred = classification_model.predict(img[None, :, :])
    pred_prob = tf.nn.softmax(pred).numpy()

    bank_class = classification_labels[np.argmax(pred_prob)] if np.max(pred_prob) > 0.21 else "OTHER"
    if bank_class == "OTHER":
        msg = TextSendMessage(text="กรุณาอัพโหลดรูปสลิป")
        line_bot_api.reply_message(event.reply_token, msg)
    else:
        # load image for ocr
        img = cv2.imread("./image.png")
        ocr_locations = get_ocr_locations(bank_class)
        messages = ""

        for i in range(len(ocr_locations)):
            (x, y, w, h) = ocr_locations[i].bbox
            print("bbox", ocr_locations[i].bbox)

            roi = img[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, lang="tha+eng")

            messages += "{} = {}\n".format(str(ocr_locations[i].id), text.strip())

        for i in range(len(messages)):
            msg = TextSendMessage(text=messages[i])
            if i == 0:
                line_bot_api.reply_message(event.reply_token, msg)
            else:
                line_bot_api.push_message(event.source.user_id, msg)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
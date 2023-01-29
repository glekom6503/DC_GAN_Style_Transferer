import telebot
from telegram import Update as update
import os
import subprocess
import time
from PIL import Image
# from onnx_model import run_model

from PIL import Image
from numpy import asarray
import numpy as np
import onnx
import onnxruntime

from flask import Flask
from flask import request
from flask import Response

from flask_sslify import SSLify

app = Flask(__name__)
sslify = SSLify(app)

def run_model():
    image = Image.open(r'/home/glebkomaroff/testbot/original.jpg')
    newsize = (256, 256)
    image = image.resize(newsize)
    x = asarray(image).astype(np.float32)
    x = np.swapaxes(x, 0, 2)
    x = np.expand_dims(x, axis=0)

    torch_out = x

    onnx_model = onnx.load(r"/home/glebkomaroff/testbot/G_B.onnx")
    onnx.checker.check_model(onnx_model)

    ort_session = onnxruntime.InferenceSession(r"/home/glebkomaroff/testbot/G_B.onnx")

    ort_inputs = {ort_session.get_inputs()[0].name: x}
    ort_outs = ort_session.run(None, ort_inputs)

    ort_inputs = {ort_session.get_inputs()[0].name: x}

    ort_outs = ort_session.run(None, ort_inputs)
    img = ort_outs[0]
    min = np.min(img)
    max = np.max(img)
    img = np.transpose((((img - min) * 255) / (max - min)),axes = [0, 3, 2, 1]).astype(np.uint8)
    im = Image.fromarray(img[0])
    newsize = (720, 720)
    im = im.resize(newsize)
    im.save(r"/home/glebkomaroff/testbot/res.jpg")

with open('/home/glebkomaroff/testbot/token.txt') as f:
    token = f.readlines()[0]
bot = telebot.TeleBot(token, parse_mode=None) 

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Здравствуйте! Пришлите картинку для переноса стиля из аниме 'Унесённые призраками' Хаяо Миядзаки.")

@bot.message_handler(content_types=['photo'])
def handle_docs_document(message):
    
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = r"/home/glebkomaroff/testbot/original.jpg"
    with open(src, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, 'Фото добавлено. Обработка...')
    # print(message)
    run_model()
    src_res = r'/home/glebkomaroff/testbot/res.jpg'
    
    res_img = open(src_res, 'rb')
    bot.send_photo(message.chat.id, res_img)

bot.infinity_polling()
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message, ContentTypes
import subprocess
import os
import time
import requests

ADMINS = ['YOUR ADMIN TG ID']

TEMPLATE_1 = 'sh1.png'
TEMPLATE_2 = 'sh2.png'
TEMPLATE_3 = 'sh3.png'

SET_TEMPLATE = TEMPLATE_1

BUTTON_FIRST_TEMPLATE_NAME = '!Шаблон-1'
BUTTON_SECOND_TEMPLATE_NAME = '!Шаблон-2'
BUTTON_THIRD_TEMPLATE_NAME = '!Шаблон-3'

button_template_1 = KeyboardButton(BUTTON_FIRST_TEMPLATE_NAME)
button_template_2 = KeyboardButton(BUTTON_SECOND_TEMPLATE_NAME)
button_template_3 = KeyboardButton(BUTTON_THIRD_TEMPLATE_NAME)

keyboard_admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)

remove_keyboard = ReplyKeyboardRemove()

keyboard_admin_menu.add(button_template_1,
                        button_template_2,
                        button_template_3)


token = "YOUR BOT TOKEN" 

bot = Bot(token=token)
dp = Dispatcher(bot=bot)

def apply_an_effect(input_video_file, input_picture_file, output_file):
    ffprobe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', input_video_file]
    ffprobe_output = subprocess.check_output(ffprobe_cmd).decode('utf-8').strip().split(',')
    width, height = int(ffprobe_output[0]), int(ffprobe_output[1])
    ffmpeg_cmd = ['ffmpeg', '-i', input_picture_file, '-vf', f'scale={width}:{height}', '-y', 'template.png']
    subprocess.run(ffmpeg_cmd)
    ffmpeg_cmd = ['ffmpeg', '-i', input_video_file, '-i', 'template.png', '-filter_complex', "[1:v]format=rgba,colorchannelmixer=aa=0.5 [image]; [0:v][image]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2 [out]", '-map', '0:a', '-map', "[out]", output_file]
    subprocess.run(ffmpeg_cmd)


def resize_video(input_file, output_file, width, height):
    ffmpeg_cmd = ['ffmpeg', '-i', input_file, '-vf', f'scale={width}:{height}', '-c:a', 'copy', output_file]
    subprocess.run(ffmpeg_cmd)

def convert_to_square(input_file, output_file):
    
    ffprobe_cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', input_file]
    ffprobe_output = subprocess.check_output(ffprobe_cmd).decode('utf-8').strip().split(',')
    width, height = int(ffprobe_output[0]), int(ffprobe_output[1])
    
    target_size = min(width, height)
    
    offset_x = (width - target_size) // 2
    offset_y = (height - target_size) // 2
    
    ffmpeg_cmd = ['ffmpeg', '-i', input_file, '-vf', f'crop={target_size}:{target_size}:{offset_x}:{offset_y}', '-c:a', 'copy', output_file]
    subprocess.run(ffmpeg_cmd)

def send_file_to_telegram(chat_id, file_path, caption=None, parse_mode=None):
    convert_to_square(file_path, str(chat_id)+"2"+".mp4")
    resize_video(str(chat_id)+"2"+".mp4", str(chat_id)+"3"+".mp4", 320, 320)
    apply_an_effect(str(chat_id)+"2"+".mp4", SET_TEMPLATE, str(chat_id)+"4"+".mp4")
    url = f'https://api.telegram.org/bot{token}/sendVideoNote'
    data = {
        'chat_id': chat_id,
        "lenght": 320 
    }
    files = {
        'video_note': open(str(chat_id)+"4"+".mp4", 'rb')
    }
    response = requests.post(url, data=data, files=files)
    
    print(response.json())
    
# @dp.message_handler(commands="start")
# async def start_func(msg: Message):
#     await msg.answer("Привет! Отправь мне видео в квадратном формате, а я тебе отправлю кружок")

@dp.message_handler(content_types=ContentTypes.VIDEO)
async def send_videonote(msg: Message):
    await msg.answer("Скачиваем видео")
    chat_id = msg.from_user.id
    file_id = msg.video.file_id 
    file = await bot.get_file(file_id) 
    await bot.download_file(file.file_path, f"{msg.from_user.id}.mp4")
    await msg.answer("Видео скачано! Попало в обработку")
    send_file_to_telegram(chat_id=msg.from_user.id, file_path=f"{msg.from_user.id}.mp4")
    os.remove(str(chat_id)+"2"+".mp4")
    time.sleep(2)
    os.remove(str(chat_id)+"3"+".mp4")
    time.sleep(2)
    os.remove(str(chat_id)+"4"+".mp4")
    time.sleep(2)
    os.remove(str(chat_id)+".mp4")

@dp.message_handler(content_types=ContentTypes.VIDEO_NOTE)
async def get_videonote(msg: Message):
    print(msg)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    remove_keyboard
    if str(message.from_user.id) in ADMINS:
        await message.answer("Привет! Отправь мне видео в квадратном формате, а я тебе отправлю кружок, но сначала выбери шаблон для плашки. По умолчанию установлен первый шаблон.")
        await message.answer("Выбери шаблон для плашки:") 
    else:
        await message.reply("Шла Саша по шоссе и сосала сушку...")

@dp.message_handler(regexp=r'!Шаблон-1')
async def send_message_to_channel(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        global SET_TEMPLATE
        SET_TEMPLATE = TEMPLATE_1
        await message.answer("Выбран шаблон 1")

@dp.message_handler(regexp=r'!Шаблон-2')
async def send_message_to_channel(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        global SET_TEMPLATE
        SET_TEMPLATE = TEMPLATE_2
        await message.answer("Выбран шаблон 2")
        

@dp.message_handler(regexp=r'!Шаблон-3')
async def send_message_to_channel(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        global SET_TEMPLATE
        SET_TEMPLATE = TEMPLATE_3
        await message.answer("Выбран шаблон 3")
        

executor.start_polling(dp)
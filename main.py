import logging
import os
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F

import asyncio
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверяем наличие токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables.")

# Инициализация бота и диспетчера
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

# Логирование
logging.basicConfig(level=logging.INFO)

def download_video(url: str, audio_only: bool = False) -> str:
    """Скачивает видео или аудио с YouTube в формате MP4 и возвращает путь к файлу."""
    output_format = "m4a" if audio_only else "mp4"
    output_template = f"%(title)s.%(ext)s"

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        filename = f"{info_dict['title']}.{output_format}"
        
        if audio_only:
            os.rename(ydl.prepare_filename(info_dict), filename)

        return filename

# Команда старт
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Отправьте ссылку на YouTube-видео, и я скачаю его для вас! Используйте /audio [ссылка] для загрузки только аудио.")

# Обработчик видео
@dp.message(F.text.startswith("http"))
async def handle_video_request(message: types.Message):
    await message.answer("⏳ Загрузка видео... Пожалуйста, подождите.")

    file_path = download_video(message.text)
    
    if file_path:
        await message.answer("📤 Отправка файла...")
        await message.answer_document(FSInputFile(file_path))
        os.remove(file_path)  # Удаляем файл после отправки
    else:
        await message.answer("❌ Ошибка загрузки видео. Проверьте ссылку и попробуйте снова.")

# Обработчик аудио
@dp.message(Command("audio"))
async def handle_audio_request(message: types.Message):
    url = message.text.split(" ", 1)[1] if len(message.text.split(" ")) > 1 else None
    if not url:
        await message.answer("❌ Пожалуйста, укажите ссылку на YouTube после команды.")
        return
    
    await message.answer("⏳ Загрузка аудио... Пожалуйста, подождите.")
    file_path = download_video(url, audio_only=True)

    if file_path:
        await message.answer("📤 Отправка файла...")
        await message.answer_document(FSInputFile(file_path))
        os.remove(file_path)
    else:
        await message.answer("❌ Ошибка загрузки аудио. Проверьте ссылку и попробуйте снова.")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

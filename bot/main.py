import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
TRANSLATION_SERVICE_URL = os.getenv('TRANSLATION_SERVICE_URL')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для перевода слов или текста на любой язык. Напиши текст, которое хочешь перевести, и язык (например, 'Привет en' для перевода на английский).")

@dp.message()
async def process_translation(message: types.Message):
    # Разделяем текст на оригинальный текст и целевой язык
    parts = message.text.split(' ', 1)
    
    if len(parts) < 2:
        await message.answer("Пожалуйста, укажите слово и язык перевода. Пример: 'привет en'")
        return

    original_text, target_language = parts

    # Отправка запроса к микросервису
    try:
        response = requests.post(TRANSLATION_SERVICE_URL, json={
            "text": original_text,
            "target_language": target_language
        })

        if response.status_code == 200:
            translated_text = response.json().get('translated_text')
            await message.answer(f"Перевод: {translated_text}")
        else:
            error_message = response.json().get('error', 'Произошла ошибка при переводе.')
            await message.answer(f"Ошибка: {error_message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к сервису перевода: {e}")
        await message.answer("Не удалось подключиться к сервису перевода. Попробуйте позже.")

async def main():
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

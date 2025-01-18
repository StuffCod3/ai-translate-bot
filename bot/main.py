import logging
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm import State, StatesGroup
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

# Определение состояний
class TranslationStates(StatesGroup):
    waiting_for_language = State()
    waiting_for_text = State()

@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для перевода. На какой язык вы хотите перевести? (например, 'en' для английского)")
    await TranslationStates.waiting_for_language.set()

@dp.message(TranslationStates.waiting_for_language)
async def process_language(message: types.Message, state: TranslationStates):
    target_language = message.text.strip()
    await state.update_data(target_language=target_language)  # Сохраняем язык
    await message.answer(f"Вы выбрали язык: {target_language}. Теперь напишите текст, который хотите перевести.")
    await TranslationStates.waiting_for_text.set()

@dp.message(TranslationStates.waiting_for_text)
async def process_translation(message: types.Message, state: TranslationStates):
    user_data = await state.get_data()
    target_language = user_data.get('target_language')
    original_text = message.text.strip()

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

    # Завершаем состояние
    await state.finish()

async def main():
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

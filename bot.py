import asyncio
import logging
import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8895792522:AAG-wVs_i7A6LuIskVBbNf_aFZEdjeKToIk"
ANTHROPIC_API_KEY = "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"

SYSTEM_PROMPT = """Sen aqlli va samimiy shaxsiy AI yordamchisisan.

Qoidalar:
- Har qanday savolga o'zbek tilida javob ber
- Qisqa, aniq va foydali javob ber
- Doim xushmuomala bo'l
- Kerak bo'lsa rus yoki ingliz tilida ham javob bera olasan
"""

logging.basicConfig(level=logging.INFO)
conversations = {}
MAX_HISTORY = 20

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def ask_claude(user_id: int, user_message: str) -> str:
    if user_id not in conversations:
        conversations[user_id] = []
    conversations[user_id].append({"role": "user", "content": user_message})
    if len(conversations[user_id]) > MAX_HISTORY:
        conversations[user_id] = conversations[user_id][-MAX_HISTORY:]
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 1024,
                    "system": SYSTEM_PROMPT,
                    "messages": conversations[user_id],
                }
            )
            data = response.json()
            reply = data["content"][0]["text"]
            conversations[user_id].append({"role": "assistant", "content": reply})
            return reply
    except Exception as e:
        print(f"Claude API xato: {e}")
        return "Uzr, hozir javob bera olmayapman. Biroz kutib qayta yozing."

@dp.message(CommandStart())
async def cmd_start(message: Message):
    conversations[message.from_user.id] = []
    await message.answer("Salom! 👋 Men sizning shaxsiy AI yordamchingizman.\n\nSavol bering, yordam beraman! 😊")

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    conversations[message.from_user.id] = []
    await message.answer("✅ Suhbat tarixi tozalandi!")

@dp.message(F.text)
async def handle_message(message: Message):
    await bot.send_chat_action(message.chat.id, "typing")
    reply = await ask_claude(message.from_user.id, message.text)
    await message.answer(reply)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

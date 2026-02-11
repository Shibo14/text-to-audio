import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from gtts import gTTS

# Bot tokeningizni kiriting
TOKEN = '8328976039:AAEOhU5Q9fhQZA6w3jhieodQjxbALiOxGL0'

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salom! Menga biron bir matn yuboring, men uni ovozli xabarga aylantirib beraman. 🎙")


@dp.message(F.text)
async def text_to_speech(message: types.Message):
    text = message.text
    # Yuklanish jarayoni haqida xabar
    status_msg = await message.answer("Ovozga aylantirilyapti... ⏳")

    try:
        # Fayl nomi
        file_path = f"downloads/voice_{message.from_user.id}.mp3"

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Matnni ovozga aylantirish (lang='uz' - o'zbek tili uchun)
        # Agar inglizcha kerak bo'lsa 'en', ruscha uchun 'ru' qiling
        tts = gTTS(text=text, lang='uz')
        tts.save(file_path)

        # Ovozli xabar (Voice message) sifatida yuborish
        voice = types.FSInputFile(file_path)
        await message.answer_voice(voice, caption="Tayyor! ✅")

        # Xabarni o'chirish va faylni tozalash
        await status_msg.delete()
        os.remove(file_path)

    except Exception as e:
        await status_msg.edit_text(f"Xatolik yuz berdi: {str(e)}")


async def main():
    print("TTS bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
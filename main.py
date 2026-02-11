import os
import asyncio
import edge_tts
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from langdetect import detect


TOKEN = '8328976039:AAEOhU5Q9fhQZA6w3jhieodQjxbALiOxGL0'
bot = Bot(token=TOKEN)
dp = Dispatcher()


VOICES = {
    "uz": {"female": "uz-UZ-MadinaNeural", "male": "uz-UZ-SardorNeural"},
    "ru": {"female": "ru-RU-SvetlanaNeural", "male": "ru-RU-DmitryNeural"},
    "en": {"female": "en-US-AvaNeural", "male": "en-US-AndrewNeural"}
}


pending_texts = {}


@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Menga matn yuboring, men uni ovozga aylantirib beraman. 🎙")


@dp.message(F.text)
async def handle_text(m: types.Message):
    text_content = m.text
    try:
      
        lang = detect(text_content)

        
        uzbek_letters = "o'g'shch"
        if any(char in text_content.lower() for char in uzbek_letters) and lang != 'uz':
            lang = 'uz'

        
        if lang not in VOICES:
            lang = "uz"
    except:
        lang = "uz"

    pending_texts[m.from_user.id] = {"text": text_content, "lang": lang}

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="👩 Ayol", callback_data="gender_female"),
        types.InlineKeyboardButton(text="👨 Erkak", callback_data="gender_male")
    )

    await m.answer(f"Matn tili: {lang.upper()}. Ovoz jinsini tanlang:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("gender_"))
async def process_tts(call: types.CallbackQuery):
    user_id = call.from_user.id
    gender = call.data.split("_")[1]

    if user_id not in pending_texts:
        await call.answer("Xatolik: Matn topilmadi. Qaytadan yuboring.", show_alert=True)
        return

    data = pending_texts[user_id]
    text = data["text"]
    lang = data["lang"]

   
    voice = VOICES[lang][gender]
    path = f"v_{user_id}.mp3"

    await call.message.edit_text("Ovoz tayyorlanmoqda... ⏳")

    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)

        audio = types.FSInputFile(path)
        await call.message.answer_voice(audio, caption=f"✅ Til: {lang.upper()} | Ovoz: {gender}")
        await call.message.delete()

        if os.path.exists(path):
            os.remove(path)
        del pending_texts[user_id] 

    except Exception as e:
        await call.message.edit_text(f"Xatolik yuz berdi: {str(e)}")



async def start_bot():
    print(">>> Bot ishlamoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print(">>> Bot to'xtatildi.")

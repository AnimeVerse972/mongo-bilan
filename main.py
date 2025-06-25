from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
import os
import logging
import json
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from keep_alive import keep_alive

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")  # Obuna uchun kanal
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

keep_alive()

# ✅ Adminlar
ADMINS = [6486825926, 7575041003]

# ✅ Kodlar JSON fayl orqali
def load_codes():
    try:
        with open("anime_posts.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_codes(data):
    with open("anime_posts.json", "w") as f:
        json.dump(data, f, indent=4)

# ✅ Obuna tekshirish
async def is_user_subscribed(user_id: int):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# 🚀 /start
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    if await is_user_subscribed(message.from_user.id):
        buttons = [[KeyboardButton(text="📢 Reklama"), KeyboardButton(text="💼 Homiylik")]]
        if message.from_user.id in ADMINS:
            buttons.append([KeyboardButton(text="🛠 Admin panel")])
        markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer("✅ Obuna bor. Kodni yuboring:", reply_markup=markup)
    else:
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Kanal", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"),
            InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")
        )
        await message.answer("❗ Iltimos, kanalga obuna bo‘ling:", reply_markup=markup)

# 🔄 Obuna tekshirish tugmasi
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_subscription(callback_query: types.CallbackQuery):
    if await is_user_subscribed(callback_query.from_user.id):
        await callback_query.message.edit_text("✅ Obuna tekshirildi. Kod yuboring.")
    else:
        await callback_query.answer("❗ Hali ham obuna emassiz!", show_alert=True)

# 💬 Kod yuborilganida
@dp.message_handler(lambda msg: msg.text.strip().isdigit())
async def handle_code(message: types.Message):
    if not await is_user_subscribed(message.from_user.id):
        return await message.answer("❗ Koddan foydalanish uchun avval kanalga obuna bo‘ling.")

    code = message.text.strip()
    anime_posts = load_codes()

    if code in anime_posts:
        data = anime_posts[code]
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=data['channel'],
            message_id=data['message_id'],
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("📥 Yuklab olish", url=f"https://t.me/{data['channel'].strip('@')}/{data['message_id']}")
            )
        )
    else:
        await message.answer("❌ Bunday kod topilmadi. Iltimos, to‘g‘ri kod yuboring.")

# 📢 Reklama
@dp.message_handler(lambda m: m.text == "📢 Reklama")
async def reklama_handler(message: types.Message):
    await message.answer("Reklama uchun: @DiyorbekPTMA")

# 💼 Homiylik
@dp.message_handler(lambda m: m.text == "💼 Homiylik")
async def homiy_handler(message: types.Message):
    await message.answer("Homiylik uchun karta: `8800904257677885`")

# 🛠 Admin panel
@dp.message_handler(lambda m: m.text == "🛠 Admin panel")
async def admin_panel(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer("👮‍♂️ Admin paneliga xush kelibsiz!")
    else:
        await message.answer("⛔ Siz admin emassiz!")

# 👤 Foydalanuvchilar soni
@dp.message_handler(commands=["users"])
async def users_count(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Siz admin emassiz!")

    data = await bot.get_chat_member_count(CHANNEL_USERNAME)
    await message.answer(f"👥 Obunachilar soni: {data}")

# ➕ Kod qo‘shish: /add <kod> <message_id>
@dp.message_handler(commands=["add"])
async def add_code_command(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Siz admin emassiz!")

    parts = message.text.split()
    if len(parts) != 3:
        return await message.answer("❗ To‘g‘ri format: `/add <kod> <message_id>`")

    code, msg_id = parts[1], parts[2]
    if not code.isdigit() or not msg_id.isdigit():
        return await message.answer("❗ Kod va ID raqam bo‘lishi kerak!")

    anime_posts = load_codes()
    anime_posts[code] = {"channel": CHANNEL_USERNAME, "message_id": int(msg_id)}
    save_codes(anime_posts)
    await message.answer(f"✅ Kod {code} saqlandi.")

# ❌ Kod o‘chirish: /remove <kod>
@dp.message_handler(commands=["remove"])
async def remove_code_command(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Siz admin emassiz!")

    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("❗ Format: `/remove <kod>`")

    code = parts[1]
    anime_posts = load_codes()

    if code in anime_posts:
        del anime_posts[code]
        save_codes(anime_posts)
        await message.answer(f"🗑 Kod {code} o‘chirildi.")
    else:
        await message.answer("❌ Bunday kod topilmadi.")

# 📋 Barcha kodlar: /list
@dp.message_handler(commands=["list"])
async def list_codes_command(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Siz admin emassiz!")

    anime_posts = load_codes()
    if not anime_posts:
        return await message.answer("📭 Hech qanday kod yo‘q.")

    text = "📄 Kodlar ro‘yxati:\n"
    for code, data in sorted(anime_posts.items(), key=lambda x: int(x[0])):
        text += f"🔢 {code} — ID: {data['message_id']}\n"

    await message.answer(text)

# 🟢 Botni ishga tushirish
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

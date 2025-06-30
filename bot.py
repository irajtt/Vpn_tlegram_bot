from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging

API_TOKEN = "7976551263:AAH91j86mISkd2U8alw3hJYKRtgXjrWFGWo"
ADMINS = [7346491945]  # آیدی عددی ادمین‌ها

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# کیبورد انتخاب دستگاه
device_kb = ReplyKeyboardMarkup(resize_keyboard=True)
device_kb.add(KeyboardButton("اندروید"), KeyboardButton("iOS"))

# کیبورد انتخاب اپراتور
operator_kb = ReplyKeyboardMarkup(resize_keyboard=True)
operator_kb.add(
    KeyboardButton("همراه اول"),
    KeyboardButton("ایرانسل"),
    KeyboardButton("شاتل"),
    KeyboardButton("مخابرات")
)

user_data = {}

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    user_data[msg.from_user.id] = {}
    await msg.answer("سلام 👋\nبرای دریافت فیلترشکن لطفاً نوع دستگاه رو انتخاب کن:", reply_markup=device_kb)

@dp.message_handler(lambda m: m.text in ["اندروید", "iOS"])
async def get_device(msg: types.Message):
    user_data[msg.from_user.id]['device'] = msg.text
    await msg.answer("اپراتور سیم‌کارتت رو انتخاب کن:", reply_markup=operator_kb)

@dp.message_handler(lambda m: m.text in ["همراه اول", "ایرانسل", "شاتل", "مخابرات"])
async def get_operator(msg: types.Message):
    user_data[msg.from_user.id]['operator'] = msg.text
    await msg.answer("لطفاً مبلغ را به شماره کارت زیر واریز کن و رسید را ارسال کن:\n\n💳 6219 8619 1104 1041 به نام فلانی")

@dp.message_handler(content_types=types.ContentType.ANY)
async def receive_payment(msg: types.Message):
    if msg.from_user.id not in user_data:
        await msg.answer("لطفاً اول با /start شروع کن.")
        return

    order = user_data[msg.from_user.id]
    text = (
        f"📥 سفارش جدید\n"
        f"👤 کاربر: @{msg.from_user.username or 'ندارد'}\n"
        f"🆔 آیدی: {msg.from_user.id}\n"
        f"📱 دستگاه: {order.get('device')}\n"
        f"📡 اپراتور: {order.get('operator')}\n"
    )

    for admin_id in ADMINS:
        try:
            if msg.photo:
                await bot.send_photo(admin_id, msg.photo[-1].file_id, caption=text)
            elif msg.document:
                await bot.send_document(admin_id, msg.document.file_id, caption=text)
            else:
                await bot.send_message(admin_id, text + f"\n🧾 رسید:\n{msg.text}")
        except:
            pass

    await msg.answer("رسیدت دریافت شد ✅\nبعد از تأیید، لینک اتصال برات ارسال می‌شه.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

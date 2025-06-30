import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

SELECT_VPN, WAIT_RECEIPT, SUPPORT = range(3)
vpn_options = [["🛡️ V2Ray","🌐 OpenVPN"],["🔐 IKEv2","🚀 WireGuard"]]

user_services = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["🛒 خرید سرویس"],["📦 سرویس‌های من"],["💬 پشتیبانی"]]
    await update.message.reply_text("سلام! من ربات فیلترشکن هستم.👇", 
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def handle_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    uid = update.message.from_user.id
    if txt=="🛒 خرید سرویس":
        await update.message.reply_text("نوع سرویس رو انتخاب کن:", 
            reply_markup=ReplyKeyboardMarkup(vpn_options, resize_keyboard=True))
        return SELECT_VPN
    if txt=="📦 سرویس‌های من":
        cnt = user_services.get(uid,0)
        await update.message.reply_text(f"شما {cnt} سرویس خریدی.")
    if txt=="💬 پشتیبانی":
        await update.message.reply_text("پیامت رو بفرست تا پشتیبانی دریافت کنه.")
        return SUPPORT
    return ConversationHandler.END

async def choose_vpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vpn"] = update.message.text
    await update.message.reply_text("لطفاً به کارت 6037991712345678 پول واریز کن و رسید را ارسال کن.")
    return WAIT_RECEIPT

async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if update.message.photo:
        file = update.message.photo[-1]
        await context.bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=file.file_id,
            caption=f"رسید از {uid}. سرویس: {context.user_data.get('vpn')}"
        )
        user_services[uid] = user_services.get(uid,0)+1
        await update.message.reply_text("رسید دریافت شد ✅ منتظر تایید ادمین باش.")
    else:
        await update.message.reply_text("لطفاً عکس رسید ارسال کن.")
    return ConversationHandler.END

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"پیام پشتیبانی از {uid}: {update.message.text}"
    )
    await update.message.reply_text("پیام فرستاده شد ✅")
    return ConversationHandler.END

if __name__=="__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.TEXT, handle_main)],
        states={
            SELECT_VPN: [MessageHandler(filters.TEXT, choose_vpn)],
            WAIT_RECEIPT: [MessageHandler(filters.PHOTO, receive_receipt)],
            SUPPORT: [MessageHandler(filters.TEXT, support)],
        },
        fallbacks=[],
    )
    app.add_handler(conv)
    app.run_polling()
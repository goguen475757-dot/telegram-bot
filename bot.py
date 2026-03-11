import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8676398540:AAGMJw_3yDSocYp-PajdBnJQAGGqF4OUEtc"

user_links = {}
user_time = {}

def is_tiktok_url(url):
    return "tiktok.com" in url

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت تحميل تيك توك\n\n"
        "✨ المميزات:\n"
        "🎬 تحميل فيديو بدون علامة\n"
        "🎧 تحميل الصوت\n"
        "🖼 تحميل الصور\n\n"
        "📥 أرسل رابط من تيك توك للبدء."
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.chat_id
    now = time.time()

    if user_id in user_time and now - user_time[user_id] < 5:
        await update.message.reply_text("⏳ انتظر قليلاً قبل إرسال رابط آخر")
        return

    user_time[user_id] = now

    url = update.message.text

    if not is_tiktok_url(url):
        await update.message.reply_text("❌ هذا ليس رابط تيك توك صحيح")
        return

    api = f"https://tikwm.com/api/?url={url}"
    r = requests.get(api).json()

    title = r["data"]["title"]
    author = r["data"]["author"]["nickname"]

    user_links[user_id] = url

    keyboard = [
        [InlineKeyboardButton("🎬 تحميل الفيديو", callback_data="video")],
        [InlineKeyboardButton("🎧 تحميل الصوت", callback_data="audio")],
        [InlineKeyboardButton("🖼 تحميل الصور", callback_data="images")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📌 العنوان: {title}\n"
        f"👤 الحساب: {author}\n\n"
        "اختر نوع التحميل:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.message.chat_id
    url = user_links.get(user_id)

    api = f"https://tikwm.com/api/?url={url}"
    r = requests.get(api).json()

    if query.data == "video":
        video = r["data"]["play"]
        await query.message.reply_video(video, caption="✅ تم تحميل الفيديو")

    elif query.data == "audio":
        audio = r["data"]["music"]
        await query.message.reply_audio(audio, caption="✅ تم تحميل الصوت")

    elif query.data == "images":

        images = r["data"].get("images")

        if images:
            for img in images:
                await query.message.reply_photo(img)
        else:
            await query.message.reply_text("❌ لا توجد صور في هذا المنشور")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
app.add_handler(CallbackQueryHandler(button))

print("البوت يعمل الآن")

app.run_polling()

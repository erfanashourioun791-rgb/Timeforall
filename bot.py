from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

from datetime import datetime
import pytz

# مراحل گفتگو
TIME, COUNTRY = range(2)

# timezone ها
countries = {
    "iran": "Asia/Tehran",
    "germany": "Europe/Berlin",
    "armenia": "Asia/Yerevan",
    "ireland": "Europe/Dublin",
    "netherlands": "Europe/Amsterdam"
}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام!\nساعت جلسه رو وارد کن (مثلاً 15:30):"
    )
    return TIME


# ---------- GET TIME ----------
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # امنیت در برابر ورودی خراب
    try:
        hour, minute = map(int, text.split(":"))
    except:
        await update.message.reply_text("❌ فرمت اشتباهه. مثل 15:30 بزن")
        return TIME

    context.user_data["hour"] = hour
    context.user_data["minute"] = minute

    await update.message.reply_text(
        "🌍 کشور مبدا رو بنویس:\n"
        "iran / germany / armenia / ireland / netherlands"
    )

    return COUNTRY


# ---------- CONVERT ----------
def convert_time(hour, minute, source_tz):
    source = pytz.timezone(source_tz)

    now = datetime.now(source).replace(
        hour=hour,
        minute=minute,
        second=0,
        microsecond=0
    )

    result = {}

    for name, tz in countries.items():
        target = pytz.timezone(tz)
        converted = now.astimezone(target)
        result[name] = converted.strftime("%H:%M")

    return result


# ---------- GET COUNTRY ----------
async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country = update.message.text.strip().lower()

    if country not in countries:
        await update.message.reply_text("❌ کشور اشتباهه. دوباره امتحان کن.")
        return COUNTRY

    hour = context.user_data.get("hour")
    minute = context.user_data.get("minute")

    result = convert_time(hour, minute, countries[country])

    msg = "🕒 زمان جلسه در کشورها:\n\n"
    for k, v in result.items():
        msg += f"{k.title()}: {v}\n"

    await update.message.reply_text(msg)

    return ConversationHandler.END


# ---------- CANCEL ----------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد.")
    return ConversationHandler.END


# ---------- MAIN ----------
def main():
    TOKEN = "8839003248:AAFH6HxzRAgv8smN6Bl5nqcbhPHPYBM_5gA"  # ← توکن واقعی اینجا

    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            TIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)
            ],
            COUNTRY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],

        # 🔥 این مهمه برای جلوگیری از هنگ در گروه
        per_message=False
    )

    app.add_handler(conv)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

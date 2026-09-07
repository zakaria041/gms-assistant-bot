import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 الوثائق والنماذج", callback_data="documents")],
        [InlineKeyboardButton("🧾 الفواتير وعروض الأسعار", callback_data="invoices")],
        [InlineKeyboardButton("✍️ الكتابة والصياغة", callback_data="writing")],
        [InlineKeyboardButton("🤖 خدمات الذكاء الاصطناعي", callback_data="ai")],
        [InlineKeyboardButton("📚 الملفات والقوالب", callback_data="files")],
        [InlineKeyboardButton("⭐ الخدمات المدفوعة", callback_data="stars")],
        [InlineKeyboardButton("📞 الدعم", callback_data="support")]
    ]

    await update.message.reply_text(
        "👋 مرحبًا بك في GMS Assistant Pro\n\n"
        "🤖 مساعدك الرقمي للخدمات الإدارية والرقمية.\n\n"
        "اختر الخدمة التي تريدها 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    messages = {
        "documents": "📄 قسم الوثائق والنماذج\n\nسيتم إضافة النماذج قريبًا.",
        "invoices": "🧾 قسم الفواتير وعروض الأسعار\n\nسيتم إضافة الخدمات قريبًا.",
        "writing": "✍️ قسم الكتابة والصياغة\n\nسيتم إضافة الخدمات قريبًا.",
        "ai": "🤖 خدمات الذكاء الاصطناعي\n\nسيتم إضافة الخدمات قريبًا.",
        "files": "📚 الملفات والقوالب\n\nسيتم إضافة الملفات قريبًا.",
        "stars": "⭐ الخدمات المدفوعة\n\nسيتم تفعيل الدفع بالنجوم بعد تشغيل النسخة الأساسية.",
        "support": "📞 الدعم\n\nتواصل معنا للحصول على المساعدة."
    }

    await query.edit_message_text(
        messages.get(query.data, "اختر خدمة من القائمة.")
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not configured")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("GMS Assistant Pro is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

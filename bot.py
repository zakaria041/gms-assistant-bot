import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")


# الخدمات والأسعار بالـ Telegram Stars
SERVICES = {
    "documents": {
        "name": "📄 الوثائق والنماذج",
        "description": "إنشاء أو تجهيز وثيقة أو نموذج إداري حسب طلبك.",
        "price": 50,
    },
    "invoices": {
        "name": "🧾 الفواتير وعروض الأسعار",
        "description": "إعداد فاتورة أو عرض سعر احترافي.",
        "price": 50,
    },
    "writing": {
        "name": "✍️ الكتابة والصياغة",
        "description": "صياغة رسالة أو طلب أو إعلان بشكل احترافي.",
        "price": 30,
    },
    "ai": {
        "name": "🤖 خدمات الذكاء الاصطناعي",
        "description": "خدمة رقمية بالذكاء الاصطناعي حسب الطلب.",
        "price": 50,
    },
    "files": {
        "name": "📚 الملفات والقوالب",
        "description": "الحصول على ملف أو قالب رقمي جاهز.",
        "price": 30,
    },
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 الوثائق والنماذج", callback_data="documents")],
        [InlineKeyboardButton("🧾 الفواتير وعروض الأسعار", callback_data="invoices")],
        [InlineKeyboardButton("✍️ الكتابة والصياغة", callback_data="writing")],
        [InlineKeyboardButton("🤖 خدمات الذكاء الاصطناعي", callback_data="ai")],
        [InlineKeyboardButton("📚 الملفات والقوالب", callback_data="files")],
        [InlineKeyboardButton("⭐ الخدمات المدفوعة", callback_data="paid")],
        [InlineKeyboardButton("📞 الدعم", callback_data="support")],
    ]

    await update.message.reply_text(
        "👋 مرحبًا بك في GMS Assistant Pro\n\n"
        "🤖 مساعدك الرقمي للخدمات الإدارية والرقمية.\n\n"
        "اختر الخدمة التي تريدها 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "paid":
        keyboard = []

        for key, service in SERVICES.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{service['name']} — ⭐ {service['price']}",
                    callback_data=f"buy:{key}",
                )
            ])

        keyboard.append([
            InlineKeyboardButton("⬅️ رجوع", callback_data="back")
        ])

        await query.edit_message_text(
            "⭐ الخدمات المدفوعة\n\n"
            "اختر الخدمة التي تريد شراءها:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if query.data == "back":
        await start(update, context)
        return

    if query.data == "support":
        await query.edit_message_text(
            "📞 الدعم\n\n"
            "للدعم أو الاستفسار حول الطلبات والمدفوعات، أرسل رسالتك هنا."
        )
        return

    if query.data.startswith("buy:"):
        service_key = query.data.split(":", 1)[1]
        service = SERVICES.get(service_key)

        if not service:
            await query.edit_message_text("❌ الخدمة غير موجودة.")
            return

        await query.edit_message_text(
            f"{service['name']}\n\n"
            f"{service['description']}\n\n"
            f"السعر: ⭐ {service['price']}\n\n"
            "اضغط على زر الدفع لإتمام الطلب."
        )

        await context.bot.send_invoice(
            chat_id=query.from_user.id,
            title=service["name"],
            description=service["description"],
            payload=f"service:{service_key}",
            currency="XTR",
            prices=[
                LabeledPrice(
                    label=service["name"],
                    amount=service["price"],
                )
            ],
            provider_token="",
        )
        return

    if query.data in SERVICES:
        service = SERVICES[query.data]

        await query.edit_message_text(
            f"{service['name']}\n\n"
            f"{service['description']}\n\n"
            f"السعر: ⭐ {service['price']}\n\n"
            "لشراء هذه الخدمة، ادخل إلى ⭐ الخدمات المدفوعة."
        )


async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query

    if not query.invoice_payload.startswith("service:"):
        await query.answer(
            ok=False,
            error_message="❌ الطلب غير صالح.",
        )
        return

    await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment

    payload = payment.invoice_payload

    if payload.startswith("service:"):
        service_key = payload.split(":", 1)[1]
        service = SERVICES.get(service_key)

        if service:
            await update.message.reply_text(
                "✅ تم استلام الدفع بنجاح!\n\n"
                f"الخدمة: {service['name']}\n"
                f"المبلغ: ⭐ {payment.total_amount}\n\n"
                "🎉 شكرًا لك.\n"
                "أرسل الآن تفاصيل طلبك في رسالة واحدة، وسنبدأ في تجهيز الخدمة."
            )
        else:
            await update.message.reply_text(
                "✅ تم استلام الدفع بنجاح.\n"
                "أرسل تفاصيل طلبك للمتابعة."
            )


async def paysupport(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 دعم المدفوعات\n\n"
        "إذا واجهت مشكلة في عملية الدفع أو الطلب، "
        "أرسل تفاصيل المشكلة هنا."
    )


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not configured")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("paysupport", paysupport))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(
        MessageHandler(
            filters.SUCCESSFUL_PAYMENT,
            successful_payment,
        )
    )

    print("GMS Assistant Pro with Telegram Stars is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

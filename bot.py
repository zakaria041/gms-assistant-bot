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
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

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
        "description": "تجهيز ملفات وقوالب رقمية حسب الطلب.",
        "price": 30,
    },
}


def main_menu():
    keyboard = [
        [InlineKeyboardButton("📄 الوثائق والنماذج", callback_data="documents")],
        [InlineKeyboardButton("🧾 الفواتير وعروض الأسعار", callback_data="invoices")],
        [InlineKeyboardButton("✍️ الكتابة والصياغة", callback_data="writing")],
        [InlineKeyboardButton("🤖 خدمات الذكاء الاصطناعي", callback_data="ai")],
        [InlineKeyboardButton("📚 الملفات والقوالب", callback_data="files")],
        [InlineKeyboardButton("⭐ الخدمات المدفوعة", callback_data="paid")],
        [InlineKeyboardButton("📞 الدعم", callback_data="support")],
    ]
    return InlineKeyboardMarkup(keyboard)


def paid_menu():
    keyboard = []

    for key, service in SERVICES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{service['name']} — ⭐ {service['price']}",
                callback_data=f"buy:{key}",
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="home")
    ])

    return InlineKeyboardMarkup(keyboard)


def service_menu(key):
    service = SERVICES[key]
    keyboard = [
        [
            InlineKeyboardButton(
                f"⭐ ادفع {service['price']} Stars",
                callback_data=f"buy:{key}",
            )
        ],
        [
            InlineKeyboardButton("🔙 الخدمات", callback_data="paid"),
            InlineKeyboardButton("🏠 الرئيسية", callback_data="home"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def send_invoice(query, key):
    """إرسال فاتورة Telegram Stars للخدمة المحددة."""
    service = SERVICES.get(key)

    if not service:
        await query.message.reply_text("❌ الخدمة غير موجودة.")
        return

    prices = [
        LabeledPrice(
            label=service["name"],
            amount=service["price"],
        )
    ]

    await query.message.reply_invoice(
        title=service["name"],
        description=service["description"],
        payload=f"service:{key}",
        currency="XTR",
        prices=prices,
        provider_token="",
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("awaiting_details", None)

    text = (
        "👋 أهلاً بك في GMS Assistant Pro\n\n"
        "🔑 مساعدك الرقمي للخدمات الإدارية والرقمية.\n\n"
        "اختر الخدمة التي تريدها من القائمة:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "home":
        await query.edit_message_text(
            "🔑 GMS Assistant Pro\n\nاختر الخدمة التي تريدها:",
            reply_markup=main_menu(),
        )
        return

    if data == "paid":
        await query.edit_message_text(
            "⭐ الخدمات المدفوعة\n\n"
            "اختر الخدمة التي تريد شراءها:\n\n"
            "سيتم عرض السعر بالـ Telegram Stars.",
            reply_markup=paid_menu(),
        )
        return

    if data == "support":
        await query.edit_message_text(
            "📞 الدعم\n\n"
            "للدعم أو الاستفسار، أرسل رسالتك هنا وسنتابع معك."
        )
        return

    # الدفع من قائمة الخدمات المدفوعة
    if data.startswith("buy:"):
        key = data.split(":", 1)[1]

        if key not in SERVICES:
            await query.message.reply_text("❌ الخدمة غير موجودة.")
            return

        await send_invoice(query, key)
        return

    # عرض تفاصيل الخدمة + زر الدفع المباشر
    if data in SERVICES:
        service = SERVICES[data]

        await query.edit_message_text(
            f"{service['name']}\n\n"
            f"{service['description']}\n\n"
            f"💰 السعر: ⭐ {service['price']}\n\n"
            "اضغط الزر أدناه لإتمام الدفع مباشرة عبر Telegram Stars:",
            reply_markup=service_menu(data),
        )
        return


async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query

    if not query.invoice_payload.startswith("service:"):
        await query.answer(
            ok=False,
            error_message="❌ طلب دفع غير صالح."
        )
        return

    key = query.invoice_payload.split(":", 1)[1]

    if key not in SERVICES:
        await query.answer(
            ok=False,
            error_message="❌ الخدمة غير موجودة."
        )
        return

    await query.answer(ok=True)


async def successful_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    payment = update.message.successful_payment
    payload = payment.invoice_payload

    if not payload.startswith("service:"):
        await update.message.reply_text("✅ تم استلام الدفع.")
        return

    key = payload.split(":", 1)[1]

    if key not in SERVICES:
        await update.message.reply_text("✅ تم استلام الدفع.")
        return

    service = SERVICES[key]

    context.user_data["awaiting_details"] = key

    await update.message.reply_text(
        "✅ تم استلام الدفع بنجاح!\n\n"
        f"الخدمة: {service['name']}\n"
        f"المبلغ: ⭐ {service['price']}\n\n"
        "📝 الآن أرسل لي تفاصيل طلبك كاملة.\n\n"
        "مثال:\n"
        "• نوع الوثيقة المطلوبة\n"
        "• المعلومات التي تريد إدخالها\n"
        "• أي ملاحظات أو شروط خاصة\n\n"
        "📌 يمكنك أيضًا إرسال صورة أو ملف إذا كان ضروريًا للطلب.\n\n"
        "بعد إرسال التفاصيل، سيتم تحويل طلبك إلى الإدارة."
    )


async def receive_order_details(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not context.user_data.get("awaiting_details"):
        return

    key = context.user_data["awaiting_details"]
    service = SERVICES.get(key)

    if not service:
        context.user_data.pop("awaiting_details", None)
        return

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else "لا يوجد Username"
    )

    user_name = user.full_name or "بدون اسم"

    details = update.message.text or "تم إرسال ملف/صورة"

    admin_text = (
        "🔔 طلب جديد مدفوع ⭐\n\n"
        f"🛎 الخدمة: {service['name']}\n"
        f"💰 السعر: ⭐ {service['price']}\n\n"
        "👤 بيانات العميل:\n"
        f"الاسم: {user_name}\n"
        f"Username: {username}\n"
        f"Telegram ID: {user.id}\n\n"
        "📝 تفاصيل الطلب:\n"
        f"{details}"
    )

    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text,
            )

            if update.message.photo:
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=update.message.photo[-1].file_id,
                    caption="📎 صورة مرفقة من العميل."
                )

            elif update.message.document:
                await context.bot.send_document(
                    chat_id=ADMIN_ID,
                    document=update.message.document.file_id,
                    caption="📎 ملف مرفق من العميل."
                )

        except Exception as e:
            print(f"ADMIN NOTIFICATION ERROR: {e}")

    context.user_data.pop("awaiting_details", None)

    await update.message.reply_text(
        "✅ تم استلام تفاصيل طلبك بنجاح.\n\n"
        "📩 تم إرسال الطلب إلى الإدارة.\n"
        "سيتم العمل على طلبك في أقرب وقت ممكن.\n\n"
        "شكراً لاستخدامك GMS Assistant Pro ⭐"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("awaiting_details", None)

    await update.message.reply_text(
        "❌ تم إلغاء إدخال الطلب.\n\n"
        "يمكنك البدء من جديد في أي وقت عبر /start."
    )


async def pay_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⭐ دعم المدفوعات\n\n"
        "إذا واجهت مشكلة في عملية الدفع، أرسل لنا تفاصيل المشكلة."
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود في Railway Variables")

    if not ADMIN_ID:
        raise RuntimeError("ADMIN_ID غير موجود في Railway Variables")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("paysupport", pay_support))

    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(PreCheckoutQueryHandler(precheckout))

    app.add_handler(
        MessageHandler(
            filters.SUCCESSFUL_PAYMENT,
            successful_payment,
        )
    )

    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.PHOTO | filters.Document.ALL)
            & ~filters.COMMAND,
            receive_order_details,
        )
    )

    print("GMS Assistant Pro with Telegram Stars is running...")

    app.run_polling()


if __name__ == "__main__":
    main()

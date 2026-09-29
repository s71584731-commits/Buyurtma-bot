import asyncio
import logging
import os
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# =========================================================
# SOZLAMALAR
# =========================================================

BOT_TOKEN = "8645669204:AAHv6MwGaCywujcgRdIWXhpIjp7_-JY8_DU"
ADMIN_ID = 847270792   # O'Z TELEGRAM ID'ingizni yozing

# =========================================================
# HOLATLAR
# =========================================================

(
    CHOOSE_TYPE,
    NAME,
    CONTACT,
    DESCRIPTION,
    DEADLINE,
    CONFIRM,
) = range(6)


# =========================================================
# /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()

    keyboard = [
        [
            InlineKeyboardButton(
                "🌐 Sayt yaratish",
                callback_data="type_site"
            )
        ],
        [
            InlineKeyboardButton(
                "🤖 Telegram bot yaratish",
                callback_data="type_bot"
            )
        ],
    ]

    await update.message.reply_text(
        f"👋 Assalomu alaykum, {user.first_name}!\n\n"
        "🚀 Sizga qanday loyiha kerak?\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHOOSE_TYPE


# =========================================================
# LOYIHA TURINI TANLASH
# =========================================================

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "type_site":
        context.user_data["project_type"] = "🌐 Sayt yaratish"
    elif query.data == "type_bot":
        context.user_data["project_type"] = "🤖 Telegram bot yaratish"

    await query.edit_message_text(
        "👤 Ism va familiyangizni kiriting:\n\n"
        "Masalan: Akbar Saidov"
    )

    return NAME


# =========================================================
# ISM FAMILIYA
# =========================================================

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()

    keyboard = [
        [
            KeyboardButton(
                "📱 Telefon raqamni yuborish",
                request_contact=True
            )
        ]
    ]

    await update.message.reply_text(
        "📱 Telefon raqamingizni yuboring.\n\n"
        "Pastdagi tugmani bosishingiz mumkin:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return CONTACT


# =========================================================
# TELEFON
# =========================================================

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()

    context.user_data["phone"] = phone

    await update.message.reply_text(
        "📝 Endi loyihangizni batafsil tushuntiring.\n\n"
        "Masalan:\n"
        "Sayt qanday bo'lishi kerak?\n"
        "Qanday funksiyalar bo'lishi kerak?\n"
        "Qanday dizayn xohlaysiz?"
    )

    return DESCRIPTION


# =========================================================
# LOYIHA TAVSIFI
# =========================================================

async def get_description(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["description"] = update.message.text.strip()

    await update.message.reply_text(
        "⏰ Loyihani qaysi muddatgacha tayyor bo'lishini xohlaysiz?\n\n"
        "Masalan:\n"
        "• 3 kun\n"
        "• 1 hafta\n"
        "• 15 kun\n"
        "• 1 oy\n"
        "• o'ziz hohlagan muddat kiritsangiz bo'ladi"
    )

    return DEADLINE


# =========================================================
# MUDDAT
# =========================================================

async def get_deadline(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    context.user_data["deadline"] = update.message.text.strip()

    user = update.effective_user
    context.user_data["telegram_id"] = user.id
    context.user_data["username"] = (
        f"@{user.username}"
        if user.username
        else "Username mavjud emas"
    )

    data = context.user_data

    text = (
        "📋 BUYURTMA MA'LUMOTLARI\n\n"
        f"📌 Turi: {data['project_type']}\n"
        f"👤 Ism: {data['name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"🆔 Telegram ID: {data['telegram_id']}\n"
        f"🔗 Username: {data['username']}\n\n"
        f"📝 Loyiha:\n{data['description']}\n\n"
        f"⏰ Muddat: {data['deadline']}\n"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Buyurtmani yuborish",
                callback_data="confirm_order"
            )
        ],
        [
            InlineKeyboardButton(
                "🔄 Ma'lumotlarni qaytadan kiritish",
                callback_data="restart_order"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Bekor qilish",
                callback_data="cancel_order"
            )
        ],
    ]

    await update.message.reply_text(
        text + "\nMa'lumotlar to'g'rimi?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CONFIRM


# =========================================================
# BUYURTMANI YUBORISH / QAYTADAN BOSHLASH / BEKOR QILISH
# =========================================================

async def confirm_order(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_order":
        await query.edit_message_text(
            "❌ Buyurtma bekor qilindi.\n\n"
            "Qaytadan boshlash uchun /start bosing."
        )
        return ConversationHandler.END

    elif query.data == "restart_order":
        project_type = context.user_data.get("project_type", "🌐 Sayt yaratish")
        context.user_data.clear()
        context.user_data["project_type"] = project_type

        await query.edit_message_text(
            "🔄 Ma'lumotlarni qaytadan kiritamiz.\n\n"
            "👤 Ism va familiyangizni kiriting:\n\n"
            "Masalan: Akbar Saidov"
        )
        return NAME

    data = context.user_data

    order_id = (
            datetime.now().strftime("%Y%m%d%H%M%S")
            + str(data["telegram_id"])[-4:]
    )

    context.user_data["order_id"] = order_id

    admin_text = (
        "🚨 YANGI BUYURTMA!\n\n"
        f"🆔 Buyurtma: #{order_id}\n\n"
        f"📌 Turi: {data['project_type']}\n"
        f"👤 Ism: {data['name']}\n"
        f"📱 Telefon: {data['phone']}\n"
        f"🆔 Telegram ID: {data['telegram_id']}\n"
        f"🔗 Username: {data['username']}\n\n"
        f"📝 Buyurtma:\n{data['description']}\n\n"
        f"⏰ Muddat: {data['deadline']}\n\n"
        "👇 BUYURTMA HOLATI:\n\n"
        "🟢 STATUS: QABUL QILINDI"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Qabul qilish",
                callback_data=f"accept_{order_id}_{data['telegram_id']}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔨 Buyurtmangiz tez orada tayyor buladi",
                callback_data=f"working_{order_id}_{data['telegram_id']}"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Buyurtma tayyor bo'ldi",
                callback_data=f"ready_{order_id}_{data['telegram_id']}"
            )
        ],
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await query.edit_message_text(
        "✅ Buyurtmangiz muvaffaqiyatli yuborildi!\n\n"
        f"🆔 Buyurtma raqami: #{order_id}\n\n"
        "Buyurtmangiz holati o'zgarganda Telegram orqali "
        "sizga avtomatik xabar yuboramiz."
    )

    return ConversationHandler.END


# =========================================================
# ADMIN BUYURTMANI BOSHQARADI
# =========================================================

async def admin_action(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer(
            "⛔ Siz admin emassiz!",
            show_alert=True
        )
        return

    parts = query.data.split("_")
    action = parts[0]
    order_id = parts[1]
    user_id = int(parts[2])

    current_text = query.message.text

    # -----------------------------------------
    # QABUL QILINDI
    # -----------------------------------------
    if action == "accept":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ Buyurtmangiz qabul qilindi!\n\n"
                f"🆔 Buyurtma: #{order_id}\n\n"
                "Buyurtmangiz tez orada ishlashga olinadi."
            )
        )

        if "🟢 STATUS:" in current_text or "🟡 STATUS:" in current_text or "✅ STATUS:" in current_text:
            updated_text = current_text.split("👇 BUYURTMA HOLATI:")[
                               0] + "👇 BUYURTMA HOLATI:\n\n🟢 STATUS: QABUL QILINDI"
        else:
            updated_text = current_text + "\n\n🟢 STATUS: QABUL QILINDI"

        await query.edit_message_text(
            text=updated_text,
            reply_markup=query.message.reply_markup
        )

    # -----------------------------------------
    # ISHLANMOQDA
    # -----------------------------------------
    elif action == "working":
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🔨 Buyurtmangiz tez orada tayyor buladi!\n\n"
                f"🆔 Buyurtma: #{order_id}\n\n"
                "Loyihangiz ustida ish boshlandi."
            )
        )

        if "🟢 STATUS:" in current_text or "🟡 STATUS:" in current_text or "✅ STATUS:" in current_text:
            updated_text = current_text.split("👇 BUYURTMA HOLATI:")[0] + "👇 BUYURTMA HOLATI:\n\n🟡 STATUS: ISHLANMOQDA"
        else:
            updated_text = current_text + "\n\n🟡 STATUS: ISHLANMOQDA"

        await query.edit_message_text(
            text=updated_text,
            reply_markup=query.message.reply_markup
        )

    # -----------------------------------------
    # TAYYOR BO'LDI (ADMIN USERNAME'INI AVTO OLISH)
    # -----------------------------------------
    elif action == "ready":
        # Adminning o'zining telegram username'ini avtomatik aniqlaymiz
        admin_username = f"@{query.from_user.username}" if query.from_user.username else "Username mavjud emas"

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Buyurtmangiz tayyor bo'ldi!\n\n"
                f"🆔 Buyurtma: #{order_id}\n\n"
                f"Loyihangiz to'liq tayyorlandi. Ma'lumotlarni olish uchun adminga murojaat qiling: {admin_username}"
            )
        )

        if "🟢 STATUS:" in current_text or "🟡 STATUS:" in current_text or "✅ STATUS:" in current_text:
            updated_text = current_text.split("👇 BUYURTMA HOLATI:")[
                               0] + "👇 BUYURTMA HOLATI:\n\n✅ STATUS: TAYYOR BO'LDI"
        else:
            updated_text = current_text + "\n\n✅ STATUS: TAYYOR BO'LDI"

        await query.edit_message_text(
            text=updated_text,
            reply_markup=None
        )


# =========================================================
# CANCEL
# =========================================================

async def cancel(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Jarayon bekor qilindi.\n\n"
        "Qaytadan boshlash uchun /start bosing."
    )

    return ConversationHandler.END


# =========================================================
# BOTNI ISHGA TUSHIRISH
# =========================================================

def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    app = Application.builder().token(BOT_TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("start", start)
        ],
        states={
            CHOOSE_TYPE: [
                CallbackQueryHandler(
                    choose_type,
                    pattern="^type_(site|bot)$"
                )
            ],
            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name
                )
            ],
            CONTACT: [
                MessageHandler(
                    filters.CONTACT | (
                            filters.TEXT & ~filters.COMMAND
                    ),
                    get_contact
                )
            ],
            DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_description
                )
            ],
            DEADLINE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_deadline
                )
            ],
            CONFIRM: [
                CallbackQueryHandler(
                    confirm_order,
                    pattern="^(confirm_order|restart_order|cancel_order)$"
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
    )

    app.add_handler(conversation)

    app.add_handler(
        CallbackQueryHandler(
            admin_action,
            pattern="^(accept|working|ready)_"
        )
    )

    print("🤖 Bot ishga tushdi...")

    app.run_polling()


if __name__ == "__main__":
  main()
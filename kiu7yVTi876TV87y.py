import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен твоего бота (получи у @BotFather)
BOT_TOKEN = "8718931468:AAEyAvX2nn4SSTKuwEsW2ZRAKU6_Ln7WJbw"

# Ссылка на твой сайт/платежную систему (куда будут уходить заказы)
PAYMENT_LINK = "https://www.tinkoff.ru/rm/r_aPzBhxwbFY.bSkZijSGWg/GnwaK14997"  # Замени на свою ссылку

# ID или юзернейм админа (для поддержки)
ADMIN_USERNAME = "@kolianchic2"

# Канал с отзывами
CHANNEL_LINK = "https://t.me/kolianchic_shop"  # Можно и просто @kolianchic_shop, но ссылка надежнее


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    # Текст приветствия (фото заменишь потом на File ID или свой URL)
    welcome_text = (
        "🌟 Добро пожаловать в магазин звезд!\n\n"
        "Здесь ты можешь приобрести звезды по низким ценам."
    )

    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton("💫 Купить звезды", callback_data="show_prices")],
        [InlineKeyboardButton("📢 Канал с отзывами", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🆘 Поддержка", callback_data="support")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с "фото" (вместо photo_id вставь свой)
    # Пока используем заглушку "Test", как ты просил
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup
    )
    # Если хочешь именно фото с подписью, раскомментируй следующую строку и убери предыдущую
    # await update.message.reply_photo(photo="Test", caption=welcome_text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    await query.answer()  # Обязательно подтверждаем нажатие

    if query.data == "show_prices":
        # Текст с прайс-листом
        prices_text = (
            "💰 <b>Наши цены:</b>\n\n"
            "50 ⭐️ — 80 руб\n"
            "75 ⭐️ — 120 руб\n"
            "100 ⭐️ — 160 руб\n"
            "150 ⭐️ — 240 руб\n"
            "200 ⭐️ — 310 руб <i>(-10 руб)</i>\n"
            "250 ⭐️ — 385 руб <i>(-15 руб)</i>\n"
            "300 ⭐️ — 460 руб <i>(-20 руб)</i>\n\n"
            
        )

        # Кнопка для перехода на сайт
        keyboard = [
            [InlineKeyboardButton("✅ Купить", url=PAYMENT_LINK)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Редактируем текущее сообщение или отправляем новое?
        # Лучше отправить новое, чтобы сохранить главное меню нетронутым
        await query.message.reply_text(
            text=prices_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    elif query.data == "support":
        # Просим пользователя написать сообщение
        await query.message.reply_text(
            "📝 Напиши сюда свой вопрос, и я перешлю его администратору."
        )
        # Устанавливаем флаг, что следующий текст от пользователя - обращение в поддержку
        context.user_data['waiting_for_support'] = True


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений (для поддержки)"""
    # Проверяем, ждем ли мы сообщение для поддержки
    if context.user_data.get('waiting_for_support'):
        user = update.effective_user
        text = update.message.text

        # Формируем сообщение для админа
        forward_text = (
            f"📨 <b>Обращение в поддержку</b>\n"
            f"От: {user.full_name} (@{user.username})\n"
            f"ID: {user.id}\n\n"
            f"<b>Сообщение:</b>\n{text}"
        )

        try:
            # Отправляем админу (нужно знать его chat_id или юзернейм)
            # Если используешь username, убедись, что админ начал диалог с ботом
            await context.bot.send_message(
                chat_id=ADMIN_USERNAME,  # Можно использовать @username
                text=forward_text,
                parse_mode='HTML'
            )
            await update.message.reply_text("✅ Твое сообщение отправлено администратору. Ожидай ответа в ближайшее время!")
        except Exception as e:
            logger.error(f"Ошибка при отправке админу: {e}")
            await update.message.reply_text("❌ Не удалось отправить сообщение. Попробуй позже или напиши напрямую: " + ADMIN_USERNAME)

        # Сбрасываем флаг
        context.user_data['waiting_for_support'] = False
    else:
        # Если не ждем поддержку, можно просто игнорировать или ответить заглушкой
        # Но лучше не спамить, поэтому ничего не делаем
        pass


def main():
    """Главная функция запуска бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
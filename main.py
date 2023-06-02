import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler, ConversationHandler, \
    MessageHandler, Filters
from functools import wraps

# Константы для состояний разговора
CHOOSE_KITCHEN, CHOOSE_MATERIAL, CHOOSE_QUALITY, CHOOSE_TIMING, CHOOSE_BUDGET, CHOOSE_CONTACT, GET_PHONE, GET_NAME = range(
    8)

# Константы для кнопок
START, HELP, ABOUT, PORTFOLIO, CONTACT = range(5)

# Декоратор для проверки доступа к командам администратора
def admin_required(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if str(user_id) == '5921904761':  # Замените ADMIN_ID на id администратора
            return func(update, context)
        else:
            update.message.reply_text("У вас нет прав для пользования данной командой")

    return wrapper


# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user = cursor.fetchone()

    if user:
        name = user[1]
        update.message.reply_text(f"Привет, {name}!")
    else:
        update.message.reply_text("Добро пожаловать! Пожалуйста, пройдите регистрацию.\nВведите ваше имя:")
        return GET_NAME


# Обработчик ввода имени при регистрации
def get_name(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    name = update.message.text.strip()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id, name) VALUES (?, ?)', (user_id, name))
    conn.commit()

    update.message.reply_text(f"Привет, {name}!")
    return ConversationHandler.END


# Обработчик команды /hiadmin
@admin_required
def admin_menu(update: Update, context: CallbackContext):
    update.message.reply_text("Приветствую тебя, хозяин")
    return ConversationHandler.END


# Обработчик команды /allmsg
@admin_required
def send_message_to_all(update: Update, context: CallbackContext):
    message = ' '.join(context.args)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()

    for user in users:
        context.bot.send_message(chat_id=user[0], text=message)

    update.message.reply_text("Рассылка успешно закончена")


# Обработчик нажатия на кнопку "Помощь"
def help_button(update: Update, context: CallbackContext):
    update.message.reply_text("Список доступных команд:\n"
                              "/start - Начать диалог\n"
                              "/help - Помощь\n"
                              "/about - О нас\n"
                              "/portfolio - Примеры работ\n"
                              "/contact - Позвонить нам")


# Обработчик нажатия на кнопку "О нас"
def about_button(update: Update, context: CallbackContext):
    update.message.reply_text("Мы - компания XYZ. Мы занимаемся производством и установкой кухонь.")


# Обработчик нажатия на кнопку "Позвонить нам"
def contact_button(update: Update, context: CallbackContext):
    update.message.reply_text("Вы можете связаться с нами по телефону +123456789\n"
                              "Мы также доступны в следующих социальных сетях:\n"
                              "Viber: @xyz_viber\n"
                              "WhatsApp: @xyz_whatsapp\n"
                              "Telegram: @xyz_telegram\n"
                              "VK: @xyz_vk")


# Обработчик нажатия на кнопку "Рассчитать стоимость"
def calculate_price_button(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Прямая", callback_data=str(0))],
        [InlineKeyboardButton("П-Образная", callback_data=str(1))],
        [InlineKeyboardButton("С островом", callback_data=str(2))],
        [InlineKeyboardButton("Угловая", callback_data=str(3))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите форму кухни:", reply_markup=reply_markup)
    return CHOOSE_KITCHEN


# Обработчик выбора формы кухни
def choose_kitchen(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['kitchen'] = query.data

    keyboard = [
        [InlineKeyboardButton("МДФ Матовые", callback_data=str(0))],
        [InlineKeyboardButton("Пластик", callback_data=str(1))],
        [InlineKeyboardButton("Металл", callback_data=str(2))],
        [InlineKeyboardButton("МДФ карбонат", callback_data=str(3))],
        [InlineKeyboardButton("Дерево", callback_data=str(4))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query.message.text != "Выберите материал:" or query.message.reply_markup != reply_markup:
        query.message.edit_text(text="Выберите материал:", reply_markup=reply_markup)
    else:
        query.answer()

    return CHOOSE_MATERIAL


# Обработчик выбора материала
def choose_material(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['material'] = query.data

    keyboard = [
        [InlineKeyboardButton("VIP", callback_data=str(0))],
        [InlineKeyboardButton("Среднее", callback_data=str(1))],
        [InlineKeyboardButton("Эконом", callback_data=str(2))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(text="Выберите качество:", reply_markup=reply_markup)
    return CHOOSE_QUALITY


# Обработчик выбора качества
def choose_quality(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['quality'] = query.data

    keyboard = [
        [InlineKeyboardButton("В течение месяца", callback_data=str(0))],
        [InlineKeyboardButton("В течение 3 месяцев", callback_data=str(1))],
        [InlineKeyboardButton("В течение 6 месяцев", callback_data=str(2))],
        [InlineKeyboardButton("В течение года", callback_data=str(3))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(text="Когда планируете заказ?", reply_markup=reply_markup)
    return CHOOSE_TIMING


# Обработчик выбора сроков заказа
def choose_timing(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['timing'] = query.data

    keyboard = [
        [InlineKeyboardButton("50-100 тыс", callback_data=str(0))],
        [InlineKeyboardButton("100-130 тыс", callback_data=str(1))],
        [InlineKeyboardButton("130-150 тыс", callback_data=str(2))],
        [InlineKeyboardButton("150-200 тыс", callback_data=str(3))],
        [InlineKeyboardButton("200 тыс и более", callback_data=str(4))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(text="Выберите бюджет:", reply_markup=reply_markup)
    return CHOOSE_BUDGET


# Обработчик выбора бюджета
def choose_budget(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['budget'] = query.data

    keyboard = [
        [InlineKeyboardButton("Viber", callback_data=str(0))],
        [InlineKeyboardButton("WhatsApp", callback_data=str(1))],
        [InlineKeyboardButton("Telegram", callback_data=str(2))],
        [InlineKeyboardButton("VK", callback_data=str(3))],
        [InlineKeyboardButton("По телефону", callback_data=str(4))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.edit_text(text="Выберите удобный вариант обратной связи:", reply_markup=reply_markup)
    return CHOOSE_CONTACT


# Обработчик выбора способа обратной связи
def choose_contact(update: Update, context: CallbackContext):
    query = update.callback_query
    context.user_data['contact'] = query.data

    query.edit_message_text(text="Введите свой телефон для связи:")
    return GET_PHONE


# Обработчик получения номера телефона
def get_phone(update: Update, context: CallbackContext):
    phone = update.message.text.strip()
    context.user_data['phone'] = phone

    update.message.reply_text("Спасибо за ваше доверие, менеджер скоро с вами свяжется!")

    # Отправка информации администратору
    admin_message = f"Пользователь: {update.effective_user.first_name} {update.effective_user.last_name}\n" \
                    f"Форма кухни: {context.user_data['kitchen']}\n" \
                    f"Материал: {context.user_data['material']}\n" \
                    f"Качество: {context.user_data['quality']}\n" \
                    f"Сроки: {context.user_data['timing']}\n" \
                    f"Бюджет: {context.user_data['budget']}\n" \
                    f"Контакт: {context.user_data['contact']}\n" \
                    f"Телефон: {context.user_data['phone']}"

    context.bot.send_message(chat_id='5921904761', text=admin_message)  # Замените ADMIN_CHAT_ID на id администратора

    return ConversationHandler.END


# Обработчик команды /about
def about(update: Update, context: CallbackContext):
    update.message.reply_text("Мы - компания XYZ. Мы занимаемся производством и установкой кухонь.")


# Обработчик команды /portfolio
def portfolio(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Предыдущий пример", callback_data="prev")],
        [InlineKeyboardButton("Следующий пример", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    example_url = "example.com"  # Замените на ссылку на пример работы
    context.user_data['example_url'] = example_url
    update.message.reply_text(f"Ссылка на пример работы: {example_url}", reply_markup=reply_markup)


# Обработчик нажатия на кнопки предыдущего и следующего примеров
def portfolio_button(update: Update, context: CallbackContext):
    query = update.callback_query
    if query is None:
        return
    example_url = context.user_data.get('example_url')
    if query.data == "prev":
        example_url = "previous_example.com"  # Замените на ссылку на предыдущий пример работы
    elif query.data == "next":
        example_url = "next_example.com"  # Замените на ссылку на следующий пример работы

    keyboard = [
        [InlineKeyboardButton("Предыдущий пример", callback_data="prev")],
        [InlineKeyboardButton("Следующий пример", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['example_url'] = example_url
    query.edit_message_text(text=f"Ссылка на пример работы: {example_url}", reply_markup=reply_markup)


def main():
    # Создание базы данных, если она не существует
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT
        )
    ''')
    conn.commit()

    # Инициализация бота
    updater = Updater("YOUR_BOT_TOKEN")  # Замените YOUR_BOT_TOKEN на токен вашего бота

    # Регистрация обработчиков
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            CHOOSE_KITCHEN: [
                CallbackQueryHandler(choose_kitchen, pattern='^[0-3]$'),
                CallbackQueryHandler(choose_material, pattern='^cancel$')  # Добавлен обработчик отмены выбора кухни
            ],
            CHOOSE_MATERIAL: [
                CallbackQueryHandler(choose_material, pattern='^[0-4]$'),
                CallbackQueryHandler(choose_quality, pattern='^cancel$')  # Добавлен обработчик отмены выбора материала
            ],
            CHOOSE_QUALITY: [
                CallbackQueryHandler(choose_quality, pattern='^[0-2]$'),
                CallbackQueryHandler(choose_timing, pattern='^cancel$')  # Добавлен обработчик отмены выбора качества
            ],
            CHOOSE_TIMING: [
                CallbackQueryHandler(choose_timing, pattern='^[0-3]$'),
                CallbackQueryHandler(choose_budget, pattern='^cancel$')  # Добавлен обработчик отмены выбора сроков заказа
            ],
            CHOOSE_BUDGET: [
                CallbackQueryHandler(choose_budget, pattern='^[0-4]$'),
                CallbackQueryHandler(choose_contact, pattern='^cancel$')  # Добавлен обработчик отмены выбора бюджета
            ],
            CHOOSE_CONTACT: [
                CallbackQueryHandler(choose_contact, pattern='^[0-4]$'),
                MessageHandler(Filters.text & ~Filters.command, get_phone)
            ],
            GET_PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('hiadmin', admin_menu))
    dp.add_handler(CommandHandler('allmsg', send_message_to_all))

    dp.add_handler(CommandHandler('help', help_button))
    dp.add_handler(CommandHandler('about', about_button))
    dp.add_handler(CommandHandler('contact', contact_button))
    dp.add_handler(CommandHandler('portfolio', portfolio_button))

    dp.add_handler(CommandHandler('start', start))  # Добавлен обработчик команды /start
    dp.add_handler(CommandHandler('portfolio', portfolio))  # Добавлен обработчик команды /portfolio
    dp.add_handler(CommandHandler('calculate', calculate_price_button))  # Добавлен обработчик команды /calculate

    dp.add_handler(CallbackQueryHandler(choose_kitchen, pattern='^[0-3]$'))
    dp.add_handler(CallbackQueryHandler(choose_material, pattern='^[0-4]$'))
    dp.add_handler(CallbackQueryHandler(choose_quality, pattern='^[0-2]$'))
    dp.add_handler(CallbackQueryHandler(choose_timing, pattern='^[0-3]$'))
    dp.add_handler(CallbackQueryHandler(choose_budget, pattern='^[0-4]$'))
    dp.add_handler(CallbackQueryHandler(choose_contact, pattern='^[0-4]$'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, get_phone))

    dp.add_handler(CommandHandler('about', about))
    dp.add_handler(CommandHandler('portfolio', portfolio))
    dp.add_handler(CommandHandler('contact', contact))

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

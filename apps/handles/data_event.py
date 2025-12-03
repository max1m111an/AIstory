from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from assets.Text import getMainMenu, getTrainingMenu, getEventDataMenu, getMainMenu_1
from handles.db_handles import get_events_name_date
from main import MAIN_MENU, TRAINING, START_TEST, test_manager
from utils.generate_answers import generate_answers


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало работы с ботом"""
    keyboard = [
        [InlineKeyboardButton("🎯 Тренировка", callback_data='training')],
        [InlineKeyboardButton("⚡ Интенсив", callback_data='intensive')],
        [InlineKeyboardButton("🏃 Марафон", callback_data='marathon')],
        [InlineKeyboardButton("🔥 Держи стрик", callback_data='streak')],
        [InlineKeyboardButton("📊 Моя статистика", callback_data='stats')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(getMainMenu(), reply_markup=reply_markup)
    return MAIN_MENU


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка главного меню"""
    query = update.callback_query
    await query.answer()

    if query.data == 'training':
        main_keyboard = [
            [InlineKeyboardButton("Хронология", callback_data='chronology')],
            [InlineKeyboardButton("Дата - Событие", callback_data='date_event')],
            [InlineKeyboardButton("Событие - Дата", callback_data='event_date')],
            [InlineKeyboardButton("Вернуться в главное меню", callback_data='back_main')],
        ]
        reply_markup = InlineKeyboardMarkup(main_keyboard)
        await query.edit_message_text(getTrainingMenu(), reply_markup=reply_markup)
        return TRAINING

    elif query.data == 'back_main':
        keyboard = [
            [InlineKeyboardButton("🎯 Тренировка", callback_data='training')],
            [InlineKeyboardButton("⚡ Интенсив", callback_data='intensive')],
            [InlineKeyboardButton("🏃 Марафон", callback_data='marathon')],
            [InlineKeyboardButton("🔥 Держи стрик", callback_data='streak')],
            [InlineKeyboardButton("📊 Моя статистика", callback_data='stats')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(getMainMenu(), reply_markup=reply_markup)
        return MAIN_MENU

    return MAIN_MENU


async def training_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка меню тренировки"""
    query = update.callback_query
    await query.answer()

    if query.data == 'chronology':
        chronology_keyboard = [
            [InlineKeyboardButton("Гоу решать", callback_data='start_chronology')],
            [InlineKeyboardButton("Назад", callback_data='back_training')],
        ]
        reply_markup = InlineKeyboardMarkup(chronology_keyboard)
        await query.edit_message_text("Режим Хронология - расставьте события в правильном порядке",
                                      reply_markup=reply_markup)
        return TRAINING

    elif query.data == 'event_date':
        date_event_keyboard = [
            [InlineKeyboardButton("Гоу решать", callback_data='start_test')],
            [InlineKeyboardButton("Назад", callback_data='back_training')],
        ]
        reply_markup = InlineKeyboardMarkup(date_event_keyboard)
        await query.edit_message_text(getEventDataMenu(), reply_markup=reply_markup)
        return START_TEST

    elif query.data == 'back_training':
        main_keyboard = [
            [InlineKeyboardButton("Хронология", callback_data='chronology')],
            [InlineKeyboardButton("Дата - Событие", callback_data='date_event')],
            [InlineKeyboardButton("Событие - Дата", callback_data='event_date')],
            [InlineKeyboardButton("Вернуться в главное меню", callback_data='back_main')],
        ]
        reply_markup = InlineKeyboardMarkup(main_keyboard)
        await query.edit_message_text(getTrainingMenu(), reply_markup=reply_markup)
        return TRAINING

    return TRAINING

async def show_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает следующий вопрос теста"""
    current_question = test_manager.get_current_question()

    if not current_question:
        await finish_test(update, context)
        return

    all_questions = await get_events_name_date()
    answers = await generate_answers(current_question, all_questions)

    context.user_data['current_answers'] = answers
    context.user_data['correct_answer'] = current_question['date']

    keyboard = []
    for i, answer in enumerate(answers, 1):
        keyboard.append([InlineKeyboardButton(answer, callback_data=f'answer_{i}')])

    keyboard.append([InlineKeyboardButton("❌ Завершить тест", callback_data='cancel_test')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (f"📝 Вопрос {test_manager.get_progress()}\n\n"
            f"Событие: {current_question['name']}\n\n"
            f"Выберите правильную дату:")

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def start_test_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало тестирования"""
    query = update.callback_query
    await query.answer()

    if query.data == 'start_test':
        await test_manager.start_new_test(5)
        await show_next_question(update, context)
        return START_TEST

    elif query.data == 'cancel_test':
        await cancel_test(update, context)
        return MAIN_MENU

    return START_TEST


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ответа пользователя"""
    query = update.callback_query
    await query.answer()

    answer_num = int(query.data.split('_')[1])

    answers = context.user_data.get('current_answers', [])
    correct_answer = context.user_data.get('correct_answer', '')

    if answer_num <= len(answers):
        selected_answer = answers[answer_num - 1]

        is_correct = test_manager.check_answer(selected_answer)

        result_text = "✅ Правильно!" if is_correct else "❌ Неправильно!"
        explanation = f"\n\nПравильный ответ: {correct_answer}"

        keyboard = []
        for i, answer in enumerate(answers, 1):
            if answer == correct_answer:
                button_text = f"✅ {answer}"
            elif i == answer_num and not is_correct:
                button_text = f"❌ {answer}"
            else:
                button_text = answer
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'disabled_{i}')])

        keyboard.append([InlineKeyboardButton("➡️ Следующий вопрос", callback_data='next_question')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"{result_text}{explanation}",
            reply_markup=reply_markup
        )

    return START_TEST


async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Переход к следующему вопросу"""
    query = update.callback_query
    await query.answer()

    if test_manager.next_question():
        await show_next_question(update, context)
    else:
        await finish_test(update, context)

    return START_TEST


async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение теста и показ результатов"""
    results = test_manager.get_results()

    keyboard = [
        [InlineKeyboardButton("🔄 Начать заново", callback_data='start_test')],
        [InlineKeyboardButton("📊 Главное меню", callback_data='back_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (f"🎉 Тест завершен!\n\n"
            f"Ваш результат: {results['score']}/{results['total']}\n"
            f"Процент правильных ответов: {results['percentage']:.1f}%\n\n")

    if results['percentage'] >= 90:
        text += "🏅 Отлично! Вы настоящий историк!"
    elif results['percentage'] >= 70:
        text += "👍 Хорошо! Продолжайте в том же духе!"
    elif results['percentage'] >= 50:
        text += "📚 Неплохо, но есть куда расти!"
    else:
        text += "💪 Не отчаивайтесь! Практика делает мастера!"

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def cancel_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена теста"""
    query = update.callback_query
    await query.answer()

    test_manager.questions = []
    test_manager.current_index = 0
    test_manager.score = 0

    keyboard = [
        [InlineKeyboardButton("🎯 Тренировка", callback_data='training')],
        [InlineKeyboardButton("⚡ Интенсив", callback_data='intensive')],
        [InlineKeyboardButton("🏃 Марафон", callback_data='marathon')],
        [InlineKeyboardButton("🔥 Держи стрик", callback_data='streak')],
        [InlineKeyboardButton("📊 Моя статистика", callback_data='stats')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "Тест отменен. Возвращаемся в главное меню.",
        reply_markup=reply_markup
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена диалога"""
    await update.message.reply_text(getMainMenu_1())
    return ConversationHandler.END
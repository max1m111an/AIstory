from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import random


from assets import getMainMenu, getTrainingMenu, getEventDataMenu, getDifficultyMenu
from constants import MAIN_MENU, TRAINING, START_TEST, SETTING_TEST
from utils import generate_smart_answers, normalize_date_format
from .db_handles import get_eras_name, get_events_with_filters


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    query = update.callback_query
    await query.answer()

    if query.data == 'training':
        main_keyboard = [
            [InlineKeyboardButton("Хронология", callback_data='chronology')],
            [InlineKeyboardButton("Дата - Событие", callback_data='date_event')],
            [InlineKeyboardButton("Событие - Дата", callback_data='event_date')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_main')],
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
    query = update.callback_query
    await query.answer()

    difficulty_id = context.user_data.get("difficulty")
    era_id = context.user_data.get("era_id")

    difficulty_name = ""
    if difficulty_id == 1:
        difficulty_name = "Легкая"
    elif difficulty_id == 2:
        difficulty_name = "Средняя"
    elif difficulty_id == 3:
        difficulty_name = "Сложная"
    elif difficulty_id == -1:
        difficulty_name = "Любая"
    else:
        difficulty_name = "Не выбрана"

    era_name = ""
    if era_id == -1:
        era_name = "Любая"
    elif era_id:
        eras = await get_eras_name()
        for era in eras:
            if era['id'] == era_id:
                era_name = era['name']
                break
    else:
        era_name = "Не выбрана"

    if query.data == 'event_date':
        has_difficulty = difficulty_id is not None
        has_era = era_id is not None

        date_event_keyboard = [
            [InlineKeyboardButton("🏺 Эпоха", callback_data='era')],
            [InlineKeyboardButton("🎚 Сложность", callback_data='difficulty')],
        ]

        if has_difficulty and has_era:
            date_event_keyboard.append(
                [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
            )

        date_event_keyboard.extend([
            [InlineKeyboardButton("🔕 Уведомления", callback_data='notifications')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_training')],
        ])

        reply_markup = InlineKeyboardMarkup(date_event_keyboard)
        await query.edit_message_text(getEventDataMenu(difficulty_name, era_name), reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == 'back_training':
        main_keyboard = [
            [InlineKeyboardButton("Хронология", callback_data='chronology')],
            [InlineKeyboardButton("Дата - Событие", callback_data='date_event')],
            [InlineKeyboardButton("Событие - Дата", callback_data='event_date')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_main')],
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

    return TRAINING


async def event_data_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "difficulty":
        saved_difficulty_id = context.user_data.get("difficulty")

        difficulty_keyboard = []

        difficulties = [
            (-1, "Любая"),
            (1, "Легкая"),
            (2, "Средняя"),
            (3, "Сложная")
        ]

        for difficulty_id, difficulty_name in difficulties:
            if saved_difficulty_id == difficulty_id:
                button_text = f"✅ {difficulty_name}"
            else:
                button_text = difficulty_name

            difficulty_keyboard.append(
                [InlineKeyboardButton(button_text, callback_data=f'diff_{difficulty_id}')]
            )

        difficulty_keyboard.append(
            [InlineKeyboardButton("⬅️ Назад", callback_data='event_date')]
        )

        reply_markup = InlineKeyboardMarkup(difficulty_keyboard)
        await query.edit_message_text(getDifficultyMenu(), reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == "era":
        saved_era_id = context.user_data.get("era_id")
        eras = await get_eras_name()

        era_keyboard = []

        if saved_era_id == -1:
            button_text = f"✅ Любая"
        else:
            button_text = "Любая"
        era_keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=f'era_{-1}')]
        )

        for era in eras:
            era_id = era['id']
            era_name = era['name']

            if saved_era_id == era_id:
                button_text = f"✅ {era_name}"
            else:
                button_text = era_name

            era_keyboard.append(
                [InlineKeyboardButton(button_text, callback_data=f'era_{era_id}')]
            )

        era_keyboard.append(
            [InlineKeyboardButton("⬅️ Назад", callback_data='event_date')]
        )

        reply_markup = InlineKeyboardMarkup(era_keyboard)
        await query.edit_message_text("Выберите эпоху:", reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == "event_date":
        difficulty_id = context.user_data.get("difficulty")
        era_id = context.user_data.get("era_id")

        difficulty_name = ""
        if difficulty_id == 1:
            difficulty_name = "Легкая"
        elif difficulty_id == 2:
            difficulty_name = "Средняя"
        elif difficulty_id == 3:
            difficulty_name = "Сложная"
        elif difficulty_id == -1:
            difficulty_name = "Любая"
        else:
            difficulty_name = "Не выбрана"

        era_name = ""
        if era_id == -1:
            era_name = "Любая"
        elif era_id:
            eras = await get_eras_name()
            for era in eras:
                if era['id'] == era_id:
                    era_name = era['name']
                    break
        else:
            era_name = "Не выбрана"

        has_difficulty = difficulty_id is not None
        has_era = era_id is not None

        date_event_keyboard = [
            [InlineKeyboardButton("🏺 Эпоха", callback_data='era')],
            [InlineKeyboardButton("🎚 Сложность", callback_data='difficulty')],
        ]

        if has_difficulty and has_era:
            date_event_keyboard.append(
                [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
            )

        date_event_keyboard.extend([
            [InlineKeyboardButton("🔕 Уведомления", callback_data='notifications')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_training')],
        ])

        reply_markup = InlineKeyboardMarkup(date_event_keyboard)
        await query.edit_message_text(getEventDataMenu(difficulty_name, era_name), reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == "back_training":
        main_keyboard = [
            [InlineKeyboardButton("Хронология", callback_data='chronology')],
            [InlineKeyboardButton("Дата - Событие", callback_data='date_event')],
            [InlineKeyboardButton("Событие - Дата", callback_data='event_date')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_main')],
        ]
        reply_markup = InlineKeyboardMarkup(main_keyboard)
        await query.edit_message_text(getTrainingMenu(), reply_markup=reply_markup)
        return TRAINING

    elif query.data == "start_test":
        difficulty_id = context.user_data.get("difficulty")
        era_id = context.user_data.get("era_id")

        if difficulty_id is None or era_id is None:
            await query.answer("Сначала выберите сложность и эпоху!", show_alert=True)
            return SETTING_TEST

        await start_test_with_all_questions(update, context)
        return START_TEST

    return SETTING_TEST


async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'event_date':
        difficulty_id = context.user_data.get("difficulty")
        era_id = context.user_data.get("era_id")

        if difficulty_id == 1:
            difficulty_name = "Легкая"
        elif difficulty_id == 2:
            difficulty_name = "Средняя"
        elif difficulty_id == 3:
            difficulty_name = "Сложная"
        elif difficulty_id == -1:
            difficulty_name = "Любая"
        else:
            difficulty_name = "Не выбрана"

        era_name = ""
        if era_id == -1:
            era_name = "Любая"
        elif era_id:
            eras = await get_eras_name()
            for era in eras:
                if era['id'] == era_id:
                    era_name = era['name']
                    break
        else:
            era_name = "Не выбрана"

        has_difficulty = difficulty_id is not None
        has_era = era_id is not None

        date_event_keyboard = [
            [InlineKeyboardButton("🏺 Эпоха", callback_data='era')],
            [InlineKeyboardButton("🎚 Сложность", callback_data='difficulty')],
        ]

        if has_difficulty and has_era:
            date_event_keyboard.append(
                [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
            )

        date_event_keyboard.extend([
            [InlineKeyboardButton("🔕 Уведомления", callback_data='notifications')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='back_training')],
        ])

        reply_markup = InlineKeyboardMarkup(date_event_keyboard)
        await query.edit_message_text(getEventDataMenu(difficulty_name, era_name), reply_markup=reply_markup)
        return SETTING_TEST

    parts = data.split("_")

    if len(parts) >= 2:
        sett = parts[0]
        try:
            id_value = int(parts[1])
        except ValueError:
            id_value = None

        if sett == "diff" and id_value is not None:
            context.user_data["difficulty"] = id_value

            difficulty_keyboard = []

            difficulties = [
                (-1, "Любая"),
                (1, "Легкая"),
                (2, "Средняя"),
                (3, "Сложная")
            ]

            for difficulty_id, difficulty_name in difficulties:
                if id_value == difficulty_id:
                    button_text = f"✅ {difficulty_name}"
                else:
                    button_text = difficulty_name

                difficulty_keyboard.append(
                    [InlineKeyboardButton(button_text, callback_data=f'diff_{difficulty_id}')]
                )

            difficulty_keyboard.append(
                [InlineKeyboardButton("⬅️ Назад", callback_data='event_date')]
            )

            reply_markup = InlineKeyboardMarkup(difficulty_keyboard)
            await query.edit_message_text(getDifficultyMenu(), reply_markup=reply_markup)
            return SETTING_TEST

        elif sett == "era" and id_value is not None:
            context.user_data["era_id"] = id_value

            era_keyboard = []
            eras = await get_eras_name()

            if id_value == -1:
                button_text = f"✅ Любая"
            else:
                button_text = "Любая"
            era_keyboard.append(
                [InlineKeyboardButton(button_text, callback_data=f'era_{-1}')]
            )

            for era in eras:
                era_id = era['id']
                era_name = era['name']
                if id_value == era_id:
                    button_text = f"✅ {era_name}"
                else:
                    button_text = era_name

                era_keyboard.append(
                    [InlineKeyboardButton(button_text, callback_data=f'era_{era_id}')]
                )

            era_keyboard.append(
                [InlineKeyboardButton("⬅️ Назад", callback_data='event_date')]
            )

            reply_markup = InlineKeyboardMarkup(era_keyboard)
            await query.edit_message_text("Выберите эпоху:", reply_markup=reply_markup)
            return SETTING_TEST

    difficulty_id = context.user_data.get("difficulty")
    era_id = context.user_data.get("era_id")

    if difficulty_id == 1:
        difficulty_name = "Легкая"
    elif difficulty_id == 2:
        difficulty_name = "Средняя"
    elif difficulty_id == 3:
        difficulty_name = "Сложная"
    elif difficulty_id == -1:
        difficulty_name = "Любая"
    else:
        difficulty_name = "Не выбрана"

    era_name = ""
    if era_id == -1:
        era_name = "Любая"
    elif era_id:
        eras = await get_eras_name()
        for era in eras:
            if era['id'] == era_id:
                era_name = era['name']
                break
    else:
        era_name = "Не выбрана"

    has_difficulty = difficulty_id is not None
    has_era = era_id is not None

    date_event_keyboard = [
        [InlineKeyboardButton("🏺 Эпоха", callback_data='era')],
        [InlineKeyboardButton("🎚 Сложность", callback_data='difficulty')],
    ]

    if has_difficulty and has_era:
        date_event_keyboard.append(
            [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
        )

    date_event_keyboard.extend([
        [InlineKeyboardButton("🔕 Уведомления", callback_data='notifications')],
        [InlineKeyboardButton("⬅️ Назад", callback_data='back_training')],
    ])

    reply_markup = InlineKeyboardMarkup(date_event_keyboard)
    await query.edit_message_text(getEventDataMenu(difficulty_name, era_name), reply_markup=reply_markup)
    return SETTING_TEST


async def start_test_with_all_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    difficulty_id = context.user_data.get("difficulty")
    era_id = context.user_data.get("era_id")

    context.user_data['test_questions'] = []
    context.user_data['test_current_index'] = 0
    context.user_data['test_score'] = 0
    context.user_data['test_difficulty'] = difficulty_id
    context.user_data['test_era'] = era_id

    questions = await get_events_with_filters(difficulty_id if difficulty_id != -1 else None,
                                              era_id if era_id != -1 else None)

    if not questions:
        await query.edit_message_text(
            "❌ Не удалось найти вопросы с выбранными параметрами.\n"
            "Попробуйте изменить настройки."
        )
        return SETTING_TEST

    random.shuffle(questions)
    context.user_data['test_questions'] = questions
    context.user_data['test_total_questions'] = len(questions)
    context.user_data['test_answered_questions'] = set()

    await show_next_question_all(update, context)
    return START_TEST


async def show_next_question_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = context.user_data.get('test_questions', [])
    total_questions = context.user_data.get('test_total_questions', 0)
    answered_questions = context.user_data.get('test_answered_questions', set())

    if len(answered_questions) >= total_questions:
        await show_final_results(update, context)
        return

    current_index = context.user_data.get('test_current_index', 0)
    current_question = None

    while current_index < total_questions:
        if current_index not in answered_questions:
            current_question = questions[current_index]
            context.user_data['test_current_index'] = current_index
            break
        current_index += 1

    if current_question is None:
        await show_final_results(update, context)
        return

    all_questions = await get_events_with_filters(
        context.user_data.get('test_difficulty') if context.user_data.get('test_difficulty') != -1 else None,
        context.user_data.get('test_era') if context.user_data.get('test_era') != -1 else None
    )

    answers = await generate_smart_answers(current_question, all_questions)

    context.user_data['current_answers'] = answers
    context.user_data['current_question'] = current_question
    context.user_data['correct_answer'] = current_question['date']

    keyboard = []
    for i, answer in enumerate(answers, 1):
        keyboard.append([InlineKeyboardButton(answer, callback_data=f'answer_{i}')])

    keyboard.append([InlineKeyboardButton("❌ Завершить тест", callback_data='cancel_test')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (f"📝 Вопрос {len(answered_questions) + 1}/{total_questions}\n\n"
            f"Событие: {current_question['name']}\n\n"
            f"Выберите правильную дату:")

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def handle_answer_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    answer_num = int(query.data.split('_')[1])

    answers = context.user_data.get('current_answers', [])
    correct_answer = context.user_data.get('correct_answer', '')
    current_question = context.user_data.get('current_question', {})
    current_index = context.user_data.get('test_current_index', 0)
    answered_questions = context.user_data.get('test_answered_questions', set())

    if answer_num <= len(answers):
        selected_answer = answers[answer_num - 1]

        try:
            normalized_selected = normalize_date_format(selected_answer)
            normalized_correct = normalize_date_format(correct_answer)

            is_correct = normalized_selected == normalized_correct
        except Exception:
            is_correct = selected_answer == correct_answer

        if is_correct:
            context.user_data['test_score'] = context.user_data.get('test_score', 0) + 1

        answered_questions.add(current_index)
        context.user_data['test_answered_questions'] = answered_questions

        result_text = "✅ Правильно!" if is_correct else "❌ Неправильно!"
        try:
            explanation = f"\n\nПравильный ответ: {normalize_date_format(correct_answer)}"
        except Exception:
            explanation = f"\n\nПравильный ответ: {correct_answer}"

        keyboard = []
        for i, answer in enumerate(answers, 1):
            try:
                normalized_answer = normalize_date_format(answer)
                normalized_correct = normalize_date_format(correct_answer)
                if normalized_answer == normalized_correct:
                    button_text = f"✅ {answer}"
                elif i == answer_num and not is_correct:
                    button_text = f"❌ {answer}"
                else:
                    button_text = answer
            except Exception:
                if answer == correct_answer:
                    button_text = f"✅ {answer}"
                elif i == answer_num and not is_correct:
                    button_text = f"❌ {answer}"
                else:
                    button_text = answer

            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'disabled_{i}')])

        keyboard.append([InlineKeyboardButton("➡️ Следующий вопрос", callback_data='next_question')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        text = (f"📝 Вопрос {len(answered_questions)}/{context.user_data.get('test_total_questions', 0)}\n\n"
                f"Событие: {current_question.get('name', '')}\n\n"
                f"{result_text}{explanation}")

        await query.edit_message_text(text, reply_markup=reply_markup)

    return START_TEST


async def next_question_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    total_questions = context.user_data.get('test_total_questions', 0)
    answered_questions = context.user_data.get('test_answered_questions', set())

    if len(answered_questions) >= total_questions:
        await show_final_results(update, context)
        return START_TEST

    current_index = context.user_data.get('test_current_index', 0)
    context.user_data['test_current_index'] = current_index + 1

    await show_next_question_all(update, context)
    return START_TEST


async def show_final_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = context.user_data.get('test_score', 0)
    answered = len(context.user_data.get('test_answered_questions', set()))
    total = context.user_data.get('test_total_questions', 0)

    if answered == 0:
        percentage = 0
    else:
        percentage = (score / answered) * 100

    difficulty_id = context.user_data.get('test_difficulty')
    era_id = context.user_data.get('test_era')

    difficulty_name = ""
    if difficulty_id == 1:
        difficulty_name = "Легкая"
    elif difficulty_id == 2:
        difficulty_name = "Средняя"
    elif difficulty_id == 3:
        difficulty_name = "Сложная"
    elif difficulty_id == -1:
        difficulty_name = "Любая"

    era_name = ""
    if era_id == -1:
        era_name = "Любая"
    elif era_id:
        eras = await get_eras_name()
        for era in eras:
            if era['id'] == era_id:
                era_name = era['name']
                break

    keyboard = [
        [InlineKeyboardButton("🔄 Начать заново", callback_data='event_date')],
        [InlineKeyboardButton("📊 Главное меню", callback_data='back_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (f"🎉 Тест завершен!\n\n"
            f"Настройки теста:\n"
            f"• Сложность: {difficulty_name}\n"
            f"• Эпоха: {era_name}\n\n"
            f"Всего вопросов: {total}\n"
            f"Отвечено: {answered}\n"
            f"Правильных ответов: {score}\n"
            f"Процент правильных: {percentage:.1f}%\n\n")

    if answered == 0:
        text += "Вы не ответили ни на один вопрос."
    elif percentage >= 90:
        text += "🏅 Отлично! Вы настоящий историк!"
    elif percentage >= 70:
        text += "👍 Хорошо! Продолжайте в том же духе!"
    elif percentage >= 50:
        text += "📚 Неплохо, но есть куда расти!"
    else:
        text += "💪 Не отчаивайтесь! Практика делает мастера!"

    for key in ['test_questions', 'test_current_index', 'test_score',
                'test_total_questions', 'test_difficulty', 'test_era', 'test_answered_questions']:
        if key in context.user_data:
            del context.user_data[key]

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def start_test_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel_test':
        await show_final_results(update, context)
        return MAIN_MENU

    return START_TEST


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer_all(update, context)


async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await next_question_all(update, context)


async def finish_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await show_final_results(update, context)


async def cancel_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await show_final_results(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(getMainMenu())
    return ConversationHandler.END
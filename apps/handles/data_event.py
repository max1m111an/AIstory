from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import random

from assets import getMainMenu, getTrainingOptionalMenu, getStartTestMenu, getDifficultyMenu, choose_train_menu, main_menu_keybord, era_diff_keyboard, notification_and_back_keyboard
from constants import MAIN_MENU, TRAINING, START_TEST, SETTING_TEST
from utils import generate_smart_answers_event_date, generate_smart_answers_date_event, normalize_date_format
from .db_handles import get_eras_name, get_events_with_filters


difficulty_id_to_name = {
    -1: "Любая",
    1: "Легкая",
    2: "Средняя",
    3: "Сложная",
}

train_type_to_str = {
    'training': 'тренировки 🎯',
    'marathon': 'марафона 🏃',
    'intensive': 'интенсива ⚡️',
}


async def get_era_name_by_id(era_id):
    if era_id == -1:
        return "Любая"
    elif era_id:
        eras = await get_eras_name()
        for era in eras:
            if era['id'] == era_id:
                return era['name']
    else:
        return "Не выбрана"


def get_callback_type_training(cont):
    if cont == 'name':
        return 'event_date'
    return 'date_event'


async def training_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    difficulty_id = context.user_data.get("difficulty")
    era_id = context.user_data.get("era_id")
    difficulty_name = difficulty_id_to_name[difficulty_id] if difficulty_id else "Не выбрана"

    era_name = await get_era_name_by_id(era_id)
    
    if query.data in ('event_date', 'date_event'):
        context.user_data["test_type"] = ('name', 'date') if query.data == 'event_date' else ('date', 'name')

        has_difficulty = difficulty_id is not None
        has_era = era_id is not None
        train_type = context.user_data.get('train_type', 'training')

        date_event_keyboard = era_diff_keyboard.copy()

        # Для марафона скрываем выбор эпохи
        if train_type == 'marathon':
            # Удаляем кнопку выбора эпохи для марафона
            date_event_keyboard = [btn for btn in date_event_keyboard if btn[0].callback_data != "era"]
            
        # Показываем кнопку "Начать тест" когда все условия выполнены
        if (train_type == 'marathon' and has_difficulty) or (train_type != 'marathon' and has_difficulty and has_era):
            date_event_keyboard.append(
                [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
            )

        date_event_keyboard.extend(notification_and_back_keyboard)

        reply_markup = InlineKeyboardMarkup(date_event_keyboard)
        
        # Для марафона меняем текст меню
        if train_type == 'marathon':
            menu_text = f"🏃 Марафон\n\nВыберите сложность:\n• {difficulty_name}\n\nНачните тест, чтобы пройти все эпохи подряд!"
        else:
            menu_text = getStartTestMenu(difficulty_name, era_name)
            
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == 'back_training':
        reply_markup = InlineKeyboardMarkup(choose_train_menu)
        await query.edit_message_text(getTrainingOptionalMenu(train_type_to_str[context.user_data.get('train_type')]), reply_markup=reply_markup)
        return TRAINING

    elif query.data == 'back_main':
        reply_markup = InlineKeyboardMarkup(main_menu_keybord)
        await query.edit_message_text(getMainMenu(), reply_markup=reply_markup)
        return MAIN_MENU

    return TRAINING


async def era_diff_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    train_type = context.user_data.get('train_type', 'training')
    
    if query.data == "difficulty":
        saved_difficulty_id = context.user_data.get("difficulty")

        difficulty_keyboard = []

        for difficulty_id, difficulty_name in difficulty_id_to_name.items():
            if saved_difficulty_id == difficulty_id:
                button_text = f"✅ {difficulty_name}"
            else:
                button_text = difficulty_name

            difficulty_keyboard.append(
                [InlineKeyboardButton(button_text, callback_data=f'diff_{difficulty_id}')]
            )

        difficulty_keyboard.append(
            [InlineKeyboardButton("⬅️ Назад", callback_data=get_callback_type_training(context.user_data.get("test_type")[0]))]
        )

        reply_markup = InlineKeyboardMarkup(difficulty_keyboard)
        await query.edit_message_text(getDifficultyMenu(), reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == "era" and train_type != 'marathon':
        # Для режима марафон скрываем выбор эпохи
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
            [InlineKeyboardButton("⬅️ Назад", callback_data=get_callback_type_training(context.user_data.get("test_type")[0]))]
        )

        reply_markup = InlineKeyboardMarkup(era_keyboard)
        await query.edit_message_text("Выберите эпоху:", reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == "event_date" or query.data == "date_event":
        context.user_data["test_type"] = ('name', 'date') if query.data == 'event_date' else ('date', 'name')

        difficulty_id = context.user_data.get("difficulty")
        era_id = context.user_data.get("era_id")
        difficulty_name = difficulty_id_to_name[difficulty_id] if difficulty_id else "Не выбрана"

        era_name = await get_era_name_by_id(era_id)
        train_type = context.user_data.get('train_type', 'training')

        has_difficulty = difficulty_id is not None
        has_era = era_id is not None

        date_event_keyboard = era_diff_keyboard.copy()
        
        # Для марафона скрываем кнопку выбора эпохи
        if train_type == 'marathon':
            date_event_keyboard = [btn for btn in date_event_keyboard if btn[0].callback_data != "era"]

        # Условия для отображения кнопки "Начать тест"
        if (train_type == 'marathon' and has_difficulty) or (train_type != 'marathon' and has_difficulty and has_era):
            date_event_keyboard.append(
                [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
            )

        date_event_keyboard.extend(notification_and_back_keyboard)

        reply_markup = InlineKeyboardMarkup(date_event_keyboard)
        
        # Меняем текст в зависимости от типа тренировки
        if train_type == 'marathon':
            menu_text = f"🏃 Марафон\n\nВыберите сложность:\n• {difficulty_name}\n\nНачните тест, чтобы пройти все эпохи подряд!"
        else:
            menu_text = getStartTestMenu(difficulty_name, era_name)
            
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
        return SETTING_TEST

    elif query.data == "back_training":
        reply_markup = InlineKeyboardMarkup(choose_train_menu)
        await query.edit_message_text(getTrainingOptionalMenu(train_type_to_str[context.user_data.get('train_type')]), reply_markup=reply_markup)
        return TRAINING

    elif query.data == "start_test":
        difficulty_id = context.user_data.get("difficulty")
        era_id = context.user_data.get("era_id")
        train_type = context.user_data.get('train_type', 'training')

        if train_type == 'marathon':
            # Для марафона проверяем только сложность
            if difficulty_id is None:
                await query.answer("Сначала выберите сложность!", show_alert=True)
                return SETTING_TEST
        else:
            # Для других режимов проверяем и сложность и эпоху
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

    current_difficulty = context.user_data.get("difficulty")
    current_era = context.user_data.get("era_id")
    train_type = context.user_data.get('train_type', 'training')
    
    if data in ('event_date', 'date_event'):
        context.user_data["test_type"] = ('name', 'date') if data == 'event_date' else ('date', 'name')
        
        if current_difficulty is None:
            difficulty_keyboard = []
            for difficulty_id, difficulty_name in difficulty_id_to_name.items():
                button_text = f"✅ {difficulty_name}" if current_difficulty == difficulty_id else difficulty_name
                difficulty_keyboard.append(
                    [InlineKeyboardButton(button_text, callback_data=f'diff_{difficulty_id}')]
                )
            
            reply_markup = InlineKeyboardMarkup(difficulty_keyboard)
            await query.edit_message_text(getDifficultyMenu(), reply_markup=reply_markup)
            return SETTING_TEST
        else:
            difficulty_name = difficulty_id_to_name[current_difficulty] if current_difficulty else "Не выбрана"
            era_name = await get_era_name_by_id(current_era)
            
            final_keyboard = era_diff_keyboard.copy()
            
            # Для марафона скрываем кнопку выбора эпохи
            if train_type == 'marathon':
                final_keyboard = [btn for btn in final_keyboard if btn[0].callback_data != "era"]
            
            # Условия для отображения кнопки "Начать тест"
            if (train_type == 'marathon' and current_difficulty is not None) or (train_type != 'marathon' and current_difficulty is not None and current_era is not None):
                final_keyboard.append(
                    [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
                )
            
            final_keyboard.extend(notification_and_back_keyboard)
            
            reply_markup = InlineKeyboardMarkup(final_keyboard)
            
            # Меняем текст в зависимости от типа тренировки
            if train_type == 'marathon':
                menu_text = f"🏃 Марафон\n\nВыберите сложность:\n• {difficulty_name}\n\nНачните тест, чтобы пройти все эпохи подряд!"
            else:
                menu_text = getStartTestMenu(difficulty_name, era_name)
                
            await query.edit_message_text(menu_text, reply_markup=reply_markup)
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
            
            if train_type == 'marathon':
                # Для марафона сразу показываем меню с кнопкой "Начать тест"
                difficulty_name = difficulty_id_to_name[id_value] if id_value else "Не выбрана"
                
                final_keyboard = era_diff_keyboard.copy()
                final_keyboard = [btn for btn in final_keyboard if btn[0].callback_data != "era"]
                final_keyboard.append(
                    [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
                )
                final_keyboard.extend(notification_and_back_keyboard)
                
                reply_markup = InlineKeyboardMarkup(final_keyboard)
                menu_text = f"🏃 Марафон\n\nВыберите сложность:\n• {difficulty_name}\n\nНачните тест, чтобы пройти все эпохи подряд!"
                await query.edit_message_text(menu_text, reply_markup=reply_markup)
                return SETTING_TEST
            elif current_era is None:
                era_keyboard = []
                eras = await get_eras_name()
                
                button_text = f"✅ Любая" if current_era == -1 else "Любая"
                era_keyboard.append(
                    [InlineKeyboardButton(button_text, callback_data=f'era_{-1}')]
                )
                
                for era in eras:
                    era_id = era['id']
                    era_name = era['name']
                    button_text = f"✅ {era_name}" if current_era == era_id else era_name
                    era_keyboard.append(
                        [InlineKeyboardButton(button_text, callback_data=f'era_{era_id}')]
                    )
                
                reply_markup = InlineKeyboardMarkup(era_keyboard)
                await query.edit_message_text("Выберите эпоху:", reply_markup=reply_markup)
                return SETTING_TEST
            else:
                difficulty_name = difficulty_id_to_name[id_value] if id_value else "Не выбрана"
                era_name = await get_era_name_by_id(current_era)
                
                final_keyboard = era_diff_keyboard.copy()
                
                if train_type != 'marathon' and id_value is not None and current_era is not None:
                    final_keyboard.append(
                        [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
                    )
                
                final_keyboard.extend(notification_and_back_keyboard)
                
                reply_markup = InlineKeyboardMarkup(final_keyboard)
                menu_text = getStartTestMenu(difficulty_name, era_name)
                await query.edit_message_text(menu_text, reply_markup=reply_markup)
                return SETTING_TEST

        elif sett == "era" and id_value is not None and train_type != 'marathon':
            context.user_data["era_id"] = id_value
            
            if current_difficulty is None:
                difficulty_keyboard = []
                for difficulty_id, difficulty_name in difficulty_id_to_name.items():
                    button_text = f"✅ {difficulty_name}" if current_difficulty == difficulty_id else difficulty_name
                    difficulty_keyboard.append(
                        [InlineKeyboardButton(button_text, callback_data=f'diff_{difficulty_id}')]
                    )
                
                reply_markup = InlineKeyboardMarkup(difficulty_keyboard)
                await query.edit_message_text(getDifficultyMenu(), reply_markup=reply_markup)
                return SETTING_TEST
            else:
                difficulty_name = difficulty_id_to_name[current_difficulty] if current_difficulty else "Не выбрана"
                era_name = await get_era_name_by_id(id_value)
                
                final_keyboard = era_diff_keyboard.copy()
                
                if train_type != 'marathon' and current_difficulty is not None and id_value is not None:
                    final_keyboard.append(
                        [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
                    )
                
                final_keyboard.extend(notification_and_back_keyboard)
                
                reply_markup = InlineKeyboardMarkup(final_keyboard)
                menu_text = getStartTestMenu(difficulty_name, era_name)
                await query.edit_message_text(menu_text, reply_markup=reply_markup)
                return SETTING_TEST
    
    elif current_difficulty is None:
        difficulty_keyboard = []
        for difficulty_id, difficulty_name in difficulty_id_to_name.items():
            button_text = f"✅ {difficulty_name}" if current_difficulty == difficulty_id else difficulty_name
            difficulty_keyboard.append(
                [InlineKeyboardButton(button_text, callback_data=f'diff_{difficulty_id}')]
            )
        
        reply_markup = InlineKeyboardMarkup(difficulty_keyboard)
        await query.edit_message_text(getDifficultyMenu(), reply_markup=reply_markup)
        return SETTING_TEST
    
    elif current_era is None and train_type != 'marathon':
        era_keyboard = []
        eras = await get_eras_name()
        
        button_text = f"✅ Любая" if current_era == -1 else "Любая"
        era_keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=f'era_{-1}')]
        )
        
        for era in eras:
            era_id = era['id']
            era_name = era['name']
            button_text = f"✅ {era_name}" if current_era == era_id else era_name
            era_keyboard.append(
                [InlineKeyboardButton(button_text, callback_data=f'era_{era_id}')]
            )
        
        reply_markup = InlineKeyboardMarkup(era_keyboard)
        await query.edit_message_text("Выберите эпоху:", reply_markup=reply_markup)
        return SETTING_TEST
    
    else:
        difficulty_name = difficulty_id_to_name[current_difficulty] if current_difficulty else "Не выбрана"
        era_name = await get_era_name_by_id(current_era)
        
        final_keyboard = era_diff_keyboard.copy()
        
        # Для марафона скрываем кнопку выбора эпохи
        if train_type == 'marathon':
            final_keyboard = [btn for btn in final_keyboard if btn[0].callback_data != "era"]
        
        # Условия для отображения кнопки "Начать тест"
        if (train_type == 'marathon' and current_difficulty is not None) or (train_type != 'marathon' and current_difficulty is not None and current_era is not None):
            final_keyboard.append(
                [InlineKeyboardButton("✅ Начать тест", callback_data='start_test')]
            )
        
        final_keyboard.extend(notification_and_back_keyboard)
        
        reply_markup = InlineKeyboardMarkup(final_keyboard)
        
        # Меняем текст в зависимости от типа тренировки
        if train_type == 'marathon':
            menu_text = f"🏃 Марафон\n\nВыберите сложность:\n• {difficulty_name}\n\nНачните тест, чтобы пройти все эпохи подряд!"
        else:
            menu_text = getStartTestMenu(difficulty_name, era_name)
            
        await query.edit_message_text(menu_text, reply_markup=reply_markup)
        return SETTING_TEST


async def start_test_with_all_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    difficulty_id = context.user_data.get("difficulty")
    era_id = context.user_data.get("era_id")
    train_type = context.user_data.get('train_type', 'training')

    context.user_data['test_questions'] = []
    context.user_data['test_current_index'] = 0
    context.user_data['test_score'] = 0
    context.user_data['test_difficulty'] = difficulty_id
    context.user_data['test_era'] = -1 if train_type == 'marathon' else era_id
    context.user_data['test_train_type'] = train_type

    if train_type == 'marathon':
        # РЕЖИМ МАРАФОН: собираем вопросы по всем эпохам
        questions = []
        
        # Получаем все эпохи
        eras = await get_eras_name()
        
        # Для каждой эпохи получаем события
        for era in eras:
            era_id = era['id']
            era_questions = await get_events_with_filters(
                difficulty_id if difficulty_id != -1 else None,
                era_id
            )
            
            if era_questions:
                # Перемешиваем события внутри каждой эпохи
                random.shuffle(era_questions)
                # Добавляем метаданные эпохи к каждому вопросу
                for question in era_questions:
                    question['era_id'] = era_id
                    question['era_name'] = era['name']
                questions.extend(era_questions)
        
        # Если не найдено ни одного вопроса (например, выбранная сложность пуста во всех эпохах)
        # Пробуем получить все события без фильтрации по эпохам
        if not questions and difficulty_id != -1:
            questions = await get_events_with_filters(
                difficulty_id,
                None  # Все эпохи
            )
            # Добавляем информацию об эпохе как "Неизвестно"
            for question in questions:
                question['era_id'] = -1
                question['era_name'] = "Неизвестно"
                
    else:
        # Обычный режим: получаем вопросы по фильтрам
        questions = await get_events_with_filters(
            difficulty_id if difficulty_id != -1 else None,
            era_id if era_id != -1 else None
        )

    if not questions:
        await query.edit_message_text(
            "❌ Не удалось найти вопросы с выбранными параметрами.\n"
            "Попробуйте изменить настройки."
        )
        return SETTING_TEST

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

    # Получаем все вопросы для генерации ответов
    all_questions = questions  # Используем уже загруженные вопросы

    # Определяем, какой тип теста: от события к дате или от даты к событию
    test_type = context.user_data.get('test_type', ('name', 'date'))
    
    if test_type[0] == 'name':
        answers = await generate_smart_answers_event_date(current_question, all_questions)
    else:
        answers = await generate_smart_answers_date_event(current_question, all_questions)

    context.user_data['current_answers'] = answers
    context.user_data['current_question'] = current_question
    context.user_data['correct_answer'] = current_question[test_type[1]]
    
    # Добавляем информацию об эпохе для режима марафон
    era_info = ""
    train_type = context.user_data.get('test_train_type', 'training')
    if train_type == 'marathon' and 'era_name' in current_question:
        era_info = f"\n🏛 Эпоха: {current_question['era_name']}"

    keyboard = []
    for i, answer in enumerate(answers, 1):
        keyboard.append([InlineKeyboardButton(answer, callback_data=f'answer_{i}')])

    keyboard.append([InlineKeyboardButton("❌ Завершить тест", callback_data='cancel_test')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if test_type[0] == 'name':
        name_1, name_2 = 'Событие', 'правильную дату'
    else:
        name_1, name_2 = 'Дата', 'правильное событие'
        
    text = (f"📝 Вопрос {len(answered_questions) + 1}/{total_questions}\n"
            f"🎚 Сложность: {difficulty_id_to_name.get(context.user_data.get('test_difficulty'), 'Любая')}"
            f"{era_info}\n\n"
            f"{name_1}: {current_question[test_type[0]]}\n\n"
            f"Выберите {name_2}:")

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
    test_type = context.user_data.get('test_type', ('name', 'date'))

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
        
        # Добавляем информацию об эпохе для режима марафон
        era_info = ""
        train_type = context.user_data.get('test_train_type', 'training')
        if train_type == 'marathon' and 'era_name' in current_question:
            era_info = f"\n🏛 Эпоха: {current_question['era_name']}"
            
        name_ = 'Событие' if test_type[0] == 'name' else 'Дата'
        text = (f"📝 Вопрос {len(answered_questions)}/{context.user_data.get('test_total_questions', 0)}\n"
                f"🎚 Сложность: {difficulty_id_to_name.get(context.user_data.get('test_difficulty'), 'Любая')}"
                f"{era_info}\n\n"
                f"{name_}: {current_question.get(test_type[0], '')}\n\n"
                f"{result_text}{explanation}")

        await query.edit_message_text(text, reply_markup=reply_markup)

    return START_TEST


async def show_final_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = context.user_data.get('test_score', 0)
    answered = len(context.user_data.get('test_answered_questions', set()))
    total = context.user_data.get('test_total_questions', 0)
    train_type = context.user_data.get('test_train_type', 'training')
    test_type = context.user_data.get('test_type', ('name', 'date'))

    if answered == 0:
        percentage = 0
    else:
        percentage = (score / answered) * 100

    difficulty_id = context.user_data.get('test_difficulty')
    difficulty_name = difficulty_id_to_name[difficulty_id] if difficulty_id else "Любая"
    
    # Для марафона показываем специальный текст
    if train_type == 'marathon':
        text = (f"🏁 Марафон завершен!\n\n"
                f"Настройки теста:\n"
                f"• Сложность: {difficulty_name}\n"
                f"• Все эпохи подряд\n\n"
                f"Всего вопросов: {total}\n"
                f"Отвечено: {answered}\n"
                f"Правильных ответов: {score}\n"
                f"Процент правильных: {percentage:.1f}%\n\n")
    else:
        era_id = context.user_data.get('test_era')
        era_name = await get_era_name_by_id(era_id)

        text = (f"🎉 Тест завершен!\n\n"
                f"Настройки теста:\n"
                f"• Сложность: {difficulty_name}\n"
                f"• Эпоха: {era_name}\n\n"
                f"Всего вопросов: {total}\n"
                f"Отвечено: {answered}\n"
                f"Правильных ответов: {score}\n"
                f"Процент правильных: {percentage:.1f}%\n\n")

    reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Начать заново", callback_data=get_callback_type_training(test_type[0]))],
            [InlineKeyboardButton("📊 Главное меню", callback_data='back_main')]
        ])

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
                'test_total_questions', 'test_difficulty', 'test_era', 
                'test_answered_questions', 'test_train_type']:
        if key in context.user_data:
            del context.user_data[key]

    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)


# Остальные функции остаются без изменений
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
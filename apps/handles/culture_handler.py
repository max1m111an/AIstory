from __future__ import annotations

from pathlib import Path
import random
from typing import Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from assets import getMainMenu, main_menu_keybord
from handles.db_handles import get_random_cultures
from constants import MAIN_MENU, START_TEST

CATEGORY_DEFS = [
    ("title", "Название строения"),
    ("architect", "Архитектор"),
    ("foundation_year", "Год основания"),
    ("ruler", "При каком правителе построено"),
    ("style", "Архитектурный стиль"),
    ("city", "Город (локация)"),
]

CATEGORY_LABELS = {key: label for key, label in CATEGORY_DEFS}
PHOTO_DIR = Path("database/culture_photos")


def _normalize_card(raw: dict[str, Any]) -> dict[str, str]:
    """Нормализует названия полей БД в единый формат."""
    return {
        "title": str(raw.get("title") or raw.get("name") or raw.get("building_name") or "—"),
        "architect": str(raw.get("architect") or raw.get("author") or "—"),
        "foundation_year": str(raw.get("foundation_year") or raw.get("year") or raw.get("founded") or "—"),
        "ruler": str(raw.get("ruler") or raw.get("built_under") or raw.get("monarch") or "—"),
        "style": str(raw.get("style") or raw.get("architectural_style") or "—"),
        "city": str(raw.get("city") or raw.get("location") or "—"),
        "img_name": str(raw.get("img_name") or raw.get("image") or ""),
    }


def _build_answers_pool(cards: list[dict[str, str]], current_card: dict[str, str], field: str, count: int = 4) -> list[str]:
    correct = current_card[field]
    pool = {card[field] for card in cards if card[field] and card[field] != "—"}
    pool.discard(correct)

    options = random.sample(list(pool), min(count - 1, len(pool))) if pool else []
    options.append(correct)
    random.shuffle(options)
    return options


def _session(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    return context.user_data.setdefault("culture_session", {})


async def start_culture_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str):
    query = update.callback_query
    await query.answer()

    raw_cards = await get_random_cultures(5)
    cards = [_normalize_card(card) for card in raw_cards]

    if len(cards) < 5:
        await query.edit_message_text(
            "❌ Недостаточно данных для режима «Культура». Нужно минимум 5 карточек в таблице cultures.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📊 Главное меню", callback_data="back_main")]]),
        )
        return MAIN_MENU

    context.user_data["culture_session"] = {
        "mode": mode,
        "cards": cards,
        "all_cards": cards.copy(),
        "round": 1,
        "index": 0,
        "answers": {},
        "results": None,
        "active_category": None,
        "wrong_cards": [],
        "checked": False,
    }

    await _show_culture_card(update, context, force_new_message=True)
    return START_TEST


async def culture_dispatch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data == "culture_training":
        return await start_culture_mode(update, context, "training")
    if data == "culture_intensive":
        return await start_culture_mode(update, context, "intensive")
    if data == "culture_exit_main":
        return await exit_culture_to_main(update, context)
    if data == "culture_open_categories":
        await _show_culture_card(update, context)
        return START_TEST
    if data.startswith("culture_category_"):
        category = data.replace("culture_category_", "")
        await _show_category_question(update, context, category)
        return START_TEST
    if data.startswith("culture_pick_"):
        idx = int(data.replace("culture_pick_", ""))
        await _select_category_answer(update, context, idx)
        return START_TEST
    if data == "culture_check":
        await _check_current_card(update, context)
        return START_TEST
    if data == "culture_next":
        await _next_card(update, context)
        return START_TEST

    return START_TEST


async def _show_culture_card(update: Update, context: ContextTypes.DEFAULT_TYPE, force_new_message: bool = False):
    query = update.callback_query
    session = _session(context)

    cards = session.get("cards", [])
    idx = session.get("index", 0)
    card = cards[idx]

    caption = (
        f"🏛 Культура — {'Интенсив' if session.get('mode') == 'intensive' else 'Тренировка'}\n"
        f"Раунд: {session.get('round', 1)} | Карточка: {idx + 1}/{len(cards)}\n\n"
        "Выберите категорию и ответьте на все 6 пунктов."
    )

    keyboard = []
    answers = session.get("answers", {})
    results = session.get("results") or {}
    checked = session.get("checked", False)

    for key, label in CATEGORY_DEFS:
        if checked:
            status = "✅" if results.get(key) else "❌"
            text = f"{status} {answers.get(key, '—')}"
        elif key in answers:
            text = f"🟡 {answers[key]}"
        else:
            text = label
        keyboard.append([InlineKeyboardButton(text, callback_data=f"culture_category_{key}")])

    if len(answers) == len(CATEGORY_DEFS) and not checked:
        keyboard.append([InlineKeyboardButton("✅ Проверить", callback_data="culture_check")])

    if checked:
        keyboard.append([InlineKeyboardButton("➡️ Следующий вопрос", callback_data="culture_next")])

    keyboard.append([InlineKeyboardButton("📊 Главное меню", callback_data="culture_exit_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    image_path = PHOTO_DIR / card["img_name"] if card.get("img_name") else None

    if force_new_message:
        try:
            await query.message.delete()
        except Exception:
            pass

        if image_path and image_path.exists():
            with image_path.open("rb") as photo:
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup,
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=caption + "\n\n⚠️ Фото не найдено.",
                reply_markup=reply_markup,
            )
        return

    try:
        await query.edit_message_caption(caption=caption, reply_markup=reply_markup)
    except Exception:
        await query.edit_message_text(caption, reply_markup=reply_markup)


async def _show_category_question(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    query = update.callback_query
    session = _session(context)

    session["active_category"] = category

    cards = session.get("all_cards") or session.get("cards", [])
    card = session["cards"][session["index"]]
    options = _build_answers_pool(cards, card, category, count=4)

    session.setdefault("options", {})[category] = options

    selected = session.get("answers", {}).get(category)

    lines = []
    for i, value in enumerate(options, 1):
        prefix = "🟡 " if selected == value else ""
        lines.append(f"{i}. {prefix}{value}")

    text = (
        f"📌 Категория: {CATEGORY_LABELS.get(category, category)}\n\n"
        "Выберите правильный ответ:\n"
        f"{chr(10).join(lines)}"
    )

    keyboard = [[InlineKeyboardButton(str(i), callback_data=f"culture_pick_{i}")] for i in range(1, len(options) + 1)]
    keyboard.append([InlineKeyboardButton("⬅️ К карточке", callback_data="culture_open_categories")])
    keyboard.append([InlineKeyboardButton("📊 Главное меню", callback_data="culture_exit_main")])

    try:
        await query.edit_message_caption(caption=text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def _select_category_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, selected_index: int):
    session = _session(context)
    category = session.get("active_category")
    if not category:
        return

    options = session.get("options", {}).get(category, [])
    if selected_index <= 0 or selected_index > len(options):
        return

    session.setdefault("answers", {})[category] = options[selected_index - 1]
    await _show_culture_card(update, context)


async def _check_current_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = _session(context)
    card = session["cards"][session["index"]]
    answers = session.get("answers", {})

    results = {}
    for key, _ in CATEGORY_DEFS:
        results[key] = answers.get(key) == card.get(key)

    session["results"] = results
    session["checked"] = True

    if session.get("mode") == "intensive" and not all(results.values()):
        session.setdefault("wrong_cards", []).append(card)

    await _show_culture_card(update, context)


async def _next_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = _session(context)
    session["index"] += 1

    if session["index"] < len(session["cards"]):
        session["answers"] = {}
        session["results"] = None
        session["checked"] = False
        session["active_category"] = None
        session["options"] = {}
        await _show_culture_card(update, context)
        return

    if session.get("mode") == "intensive" and session.get("wrong_cards"):
        session["cards"] = session["wrong_cards"].copy()
        session["wrong_cards"] = []
        session["index"] = 0
        session["round"] = session.get("round", 1) + 1
        session["answers"] = {}
        session["results"] = None
        session["checked"] = False
        session["active_category"] = None
        session["options"] = {}
        await _show_culture_card(update, context)
        return

    await _show_culture_final(update, context)


async def _show_culture_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    session = _session(context)

    rounds = session.get("round", 1)
    total_cards = len(session.get("all_cards", []))

    text = (
        "📊 Режим «Культура» завершён!\n\n"
        f"• Режим: {'Интенсив' if session.get('mode') == 'intensive' else 'Тренировка'}\n"
        f"• Всего карточек: {total_cards}\n"
        f"• Раундов: {rounds}\n"
        "Отличная работа!"
    )

    context.user_data.pop("culture_session", None)

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Главное меню", callback_data="back_main")],
    ])

    try:
        await query.edit_message_caption(caption=text, reply_markup=reply_markup)
    except Exception:
        await query.edit_message_text(text, reply_markup=reply_markup)


async def exit_culture_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.pop("culture_session", None)

    try:
        await query.edit_message_caption(
            caption=getMainMenu(),
            reply_markup=InlineKeyboardMarkup(main_menu_keybord),
        )
    except Exception:
        await query.edit_message_text(
            getMainMenu(),
            reply_markup=InlineKeyboardMarkup(main_menu_keybord),
        )

    return MAIN_MENU

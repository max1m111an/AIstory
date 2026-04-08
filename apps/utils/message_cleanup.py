import logging

from telegram import Message
from telegram.error import BadRequest, Forbidden
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

LAST_BOT_MESSAGE_KEY = "last_bot_message_by_chat"


async def send_clean_message(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    text: str,
    **kwargs,
) -> Message:
    """
    Отправляет сообщение и удаляет предыдущее сообщение бота в этом чате.
    В результате в чате остается только последнее отправленное сообщение бота.
    """
    return await send_clean_message_with_storage(
        bot_data=context.application.bot_data,
        bot=context.bot,
        chat_id=chat_id,
        text=text,
        **kwargs,
    )


async def send_clean_message_with_storage(
    bot_data: dict,
    bot,
    chat_id: int,
    text: str,
    **kwargs,
) -> Message:
    messages_by_chat = bot_data.setdefault(LAST_BOT_MESSAGE_KEY, {})
    previous_message_ids = messages_by_chat.get(chat_id, [])

    # Обратная совместимость: раньше здесь мог храниться один int.
    if isinstance(previous_message_ids, int):
        previous_message_ids = [previous_message_ids]

    for previous_message_id in previous_message_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=previous_message_id)
        except (BadRequest, Forbidden):
            logger.debug(
                "Не удалось удалить старое сообщение бота chat_id=%s, message_id=%s",
                chat_id,
                previous_message_id,
            )

    message = await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    messages_by_chat[chat_id] = [message.message_id]
    return message

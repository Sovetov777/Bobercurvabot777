import os
import re
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ChatType

# ====================== НАСТРОЙКИ ======================
TOKEN = os.environ.get("TOKEN")

PHONE_PATTERN = re.compile(
    r'(?:\+7|8|7)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
    r'|(?:\+7|8|7)\d{10}',
    re.IGNORECASE
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def has_phone_number(text: str) -> bool:
    if not text:
        return False
    return bool(PHONE_PATTERN.search(text))


async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return

    try:
        member = await context.bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("administrator", "creator"):
            return
    except Exception:
        pass

    text = message.text or message.caption or ""

    if not has_phone_number(text):
        try:
            await message.delete()
            logger.info(f"Удалено сообщение без телефона | user={message.from_user.id}")
        except Exception as e:
            logger.error(f"Ошибка удаления: {e}")


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(
        MessageHandler(
            (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
            check_message
        )
    )

    print("Бот успешно запущен и работает...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

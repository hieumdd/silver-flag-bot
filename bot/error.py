import io
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from logger import get_logger


logger = get_logger(__name__)


def on_error(chat_id: int):
    async def _on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        error = context.error
        error_formatted = traceback.format_exception_only(error).pop()
        traceback_list = traceback.format_exception(None, error, error.__traceback__)

        logger.error(error_formatted, exc_info=error)

        with io.StringIO() as error_file:
            error_file.writelines(traceback_list)
            error_file.seek(0)

            await context.bot.send_document(
                chat_id=chat_id,
                document=error_file,
                filename="error.log",
                caption=error_formatted,
                parse_mode=ParseMode.HTML,
            )

    return _on_error

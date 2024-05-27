import io
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from yattag import Doc

from logger import get_logger


logger = get_logger(__name__)


def on_error(chat_id: int):
    async def _on_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
        error = context.error
        error_message = traceback.format_exception_only(error).pop()
        traceback_list = traceback.format_exception(None, error, error.__traceback__)

        logger.error(error_message, exc_info=error)

        with io.StringIO() as error_file:
            error_file.writelines(traceback_list)
            error_file.seek(0)

            doc, tag, text = Doc().tagtext()
            with tag("pre"):
                with tag("code", klass="language-python"):
                    text(error_message)

            await context.bot.send_document(
                chat_id=chat_id,
                document=error_file,
                filename="error.log",
                caption=doc.getvalue(),
                parse_mode=ParseMode.HTML,
            )

    return _on_error

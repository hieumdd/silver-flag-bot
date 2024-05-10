from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from logger import get_logger
from sjc.service import get_sjc_prices


logger = get_logger(__name__)


async def on_sjc_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Analyzing SJC Price")

    await update.message.reply_chat_action(ChatAction.TYPING)
    report = get_sjc_prices()
    if report:
        await update.message.reply_text(report.to_html(), parse_mode=ParseMode.HTML)

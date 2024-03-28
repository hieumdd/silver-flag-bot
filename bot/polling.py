from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode

from logger import get_logger
from trading.strategy.interface import Strategy

logger = get_logger(__name__)


async def on_polling(context: ContextTypes.DEFAULT_TYPE):
    strategy: Strategy = context.job.data
    chat_id = context.job.chat_id
    logger.info(f"Polling strategy {strategy.__class__}")

    analysis, signal = strategy.analyze()

    if signal:
        logger.info(f"Signal found for strategy {strategy.__class__}")
        await context.bot.send_chat_action(
            chat_id=chat_id,
            action=ChatAction.UPLOAD_PHOTO,
        )
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=analysis.plot,
            caption=signal.to_html(),
            parse_mode=ParseMode.HTML,
        )

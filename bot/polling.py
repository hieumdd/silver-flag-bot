from telegram.ext import ContextTypes

from logger import get_logger

logger = get_logger(__name__)


async def polling(context: ContextTypes.DEFAULT_TYPE):
    strategy = context.job.data
    chat_id = context.job.chat_id
    logger.info(f"Polling strategy {strategy.__class__}")

    analysis, signal = strategy.analyze()

    if signal:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=analysis.plot,
            caption=signal.to_html(analysis.symbol),
            parse_mode="html",
        )

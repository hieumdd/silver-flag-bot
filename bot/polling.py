from functools import partial
from zoneinfo import ZoneInfo

from telegram.ext import ContextTypes
from apscheduler.triggers.cron import CronTrigger

from logger import get_logger

logger = get_logger(__name__)


async def polling(context: ContextTypes.DEFAULT_TYPE):
    strategy = context.job.data
    chat_id = context.job.chat_id
    logger.info(f"Running strategy {strategy.__class__}")

    analysis, signal = strategy.analyze()

    if signal:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=analysis.plot,
            caption=signal.to_html(analysis.symbol),
            parse_mode="html",
        )


PollingCronTrigger = partial(
    CronTrigger,
    day_of_week="0-4",
    second="0",
    timezone=ZoneInfo("Asia/Ho_Chi_Minh"),
)

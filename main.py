import logging
import os
from datetime import time
from zoneinfo import ZoneInfo

from telegram.ext import Application, ContextTypes

from trading.strategy.multi_ma import MultiMA

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

timezone = ZoneInfo("Asia/Ho_Chi_Minh")
chat_id = -4154075164
strategy = MultiMA()


async def main(context: ContextTypes.DEFAULT_TYPE):
    logger.debug(f"Running strategy {strategy.__class__}")

    if signals := strategy.get_signals():
        logger.debug(f"Signal: {str(signal)}")
        for signal in signals:
            await context.bot.send_message(
                chat_id=chat_id,
                text=str(signal),
                parse_mode="html",
            )


application = Application.builder().token(os.getenv("TELEGRAM_TOKEN", "")).build()
application.job_queue.run_repeating(
    main,
    interval=60,
    first=time(9, tzinfo=timezone),
    last=time(11, 30, tzinfo=timezone),
)
application.job_queue.run_repeating(
    main,
    interval=60,
    first=time(13, tzinfo=timezone),
    last=time(14, 30, tzinfo=timezone),
)
application.run_polling()

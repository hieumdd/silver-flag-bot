from functools import partial
import logging
import os
from zoneinfo import ZoneInfo

from telegram.ext import Application, ContextTypes
from apscheduler.triggers.cron import CronTrigger

from trading.strategy.multi_ma import MultiMA

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

chat_id = -4154075164
strategy = MultiMA("VN30F1M")


async def main(context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Running strategy {strategy.__class__}")

    if signals := strategy.get_signals():
        for signal in signals:
            logger.info(f"Signal: {str(signal)}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=str(signal),
                parse_mode="html",
            )


timezone = ZoneInfo("Asia/Ho_Chi_Minh")
VN30CronTrigger = partial(CronTrigger, day_of_week="0-4", second="0", timezone=timezone)

application = Application.builder().token(os.getenv("TELEGRAM_TOKEN", "")).build()

application.job_queue.run_custom(
    main,
    job_kwargs={"trigger": VN30CronTrigger(hour="9-11")},
)
application.job_queue.run_custom(
    main,
    job_kwargs={"trigger": VN30CronTrigger(hour="11", minute="0-30")},
)
application.job_queue.run_custom(
    main,
    job_kwargs={"trigger": VN30CronTrigger(hour="13-14")},
)
application.job_queue.run_custom(
    main,
    job_kwargs={"trigger": VN30CronTrigger(hour="14", minute="0-30")},
)

application.run_polling()

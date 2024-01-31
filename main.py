from functools import partial
import logging
import os
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.triggers.cron import CronTrigger

from trading.strategy.macd_vwap import MACDVWAP

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

chat_id = -4154075164
strategy = MACDVWAP("VN30F1M")


async def polling(context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Running strategy {strategy.__class__}")

    plot, signals = strategy.analyze()

    logger.info(f"Strategy {strategy.__class__} analyzed: {len(signals)} signals")

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=plot,
        caption=str(type(strategy).__name__),
        parse_mode="html",
    )

    for signal in signals:
        await context.bot.send_message(
            chat_id=chat_id,
            text=str(signal),
            parse_mode="html",
        )


async def on_chart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Plotting strategy {strategy.__class__}")

    plot, _ = strategy.analyze()

    await update.message.reply_photo(
        photo=plot,
        caption=str(type(strategy).__name__),
        parse_mode="html",
    )


timezone = ZoneInfo("Asia/Ho_Chi_Minh")
VN30CronTrigger = partial(CronTrigger, day_of_week="0-4", second="0", timezone=timezone)

application = Application.builder().token(os.getenv("TELEGRAM_TOKEN", "")).build()

application.job_queue.run_custom(
    polling,
    job_kwargs={"trigger": VN30CronTrigger(hour="9-11")},
)
application.job_queue.run_custom(
    polling,
    job_kwargs={"trigger": VN30CronTrigger(hour="11", minute="0-30")},
)
application.job_queue.run_custom(
    polling,
    job_kwargs={"trigger": VN30CronTrigger(hour="13-14")},
)
application.job_queue.run_custom(
    polling,
    job_kwargs={"trigger": VN30CronTrigger(hour="14", minute="0-30")},
)

application.add_handler(CommandHandler("chart", on_chart))

application.run_polling()

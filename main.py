import os
from datetime import time
from zoneinfo import ZoneInfo

from telegram.ext import Application, ContextTypes

from trading.strategy.multi_ma import MultiMA

CHAT_ID = -4154075164

strategy = MultiMA()


async def main(context: ContextTypes.DEFAULT_TYPE):
    signals = strategy.get_signals()

    if signals:
        for signal in signals:
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=str(signal),
                parse_mode="html",
            )


application = Application.builder().token(os.getenv("TELEGRAM_TOKEN", "")).build()
application.job_queue.run_repeating(
    main,
    interval=60,
    first=time(9, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
    last=time(11, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
)
application.job_queue.run_repeating(
    main,
    interval=60,
    first=time(13, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
    last=time(14, 30, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")),
)
application.run_polling()

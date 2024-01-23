import json
import os

from telegram.ext import Application, ContextTypes
from ssi.client_model import GetIntradayOptions
from ssi.client_service import SSIClient

CHAT_ID = -4154075164

ssi_client = SSIClient()


async def main(context: ContextTypes.DEFAULT_TYPE):
    data = ssi_client.get_intraday(GetIntradayOptions("VN30F1M"))["data"][0]
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"""<pre>{json.dumps(data, indent=2)}</pre>""",
        parse_mode="html",
    )


application = Application.builder().token(os.getenv("TELEGRAM_TOKEN", "")).build()

application.job_queue.run_repeating(main, interval=5, first=0)

application.run_polling()

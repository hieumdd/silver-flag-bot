import os

from telegram.ext import Application, CommandHandler

import logger
from trading.strategy.atr_trailing_stop import ATRTrailingStop
from bot.error import on_error
from bot.analyze import on_analyze
from bot.params import on_params
from bot.polling import on_polling

if __name__ == "__main__":
    strategy = ATRTrailingStop("VN30F1M")
    chat_id = -4154075164

    async def post_init(application: Application):
        await application.bot.set_my_commands(
            [
                ("analyze", "Analyze"),
                ("params", "Params"),
            ]
        )

    application = (
        Application.builder()
        .token(os.getenv("TELEGRAM_TOKEN", ""))
        .post_init(post_init)
        .build()
    )

    for trigger in strategy.data_provider.timeframe.crons():
        application.job_queue.run_custom(
            on_polling(strategy, chat_id),
            job_kwargs={"trigger": trigger},
        )

    application.add_handler(CommandHandler("analyze", on_analyze(strategy)))
    application.add_handler(CommandHandler("params", on_params(strategy)))
    application.add_error_handler(on_error(chat_id))

    application.run_polling()

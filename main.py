import os

from telegram.ext import Application, CommandHandler

from logger import init_logger
from trading.strategy.macd_vwap import MACDVWAP
from bot.polling import polling
from bot.analyze import on_analyze

init_logger()

if __name__ == "__main__":
    strategy = MACDVWAP("VN30F1M")
    chat_id = -4154075164

    async def post_init(application: Application):
        await application.bot.set_my_commands([("analyze", "Analyze")])

    application = (
        Application.builder()
        .token(os.getenv("TELEGRAM_TOKEN", ""))
        .post_init(post_init)
        .build()
    )

    strategy.data_provider.timeframe.crons()

    for trigger in strategy.data_provider.timeframe.crons():
        application.job_queue.run_custom(
            polling,
            data=strategy,
            chat_id=chat_id,
            job_kwargs={"trigger": trigger},
        )

    application.add_handler(CommandHandler("analyze", on_analyze(strategy)))

    application.run_polling()

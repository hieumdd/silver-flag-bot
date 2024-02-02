from telegram import Update
from telegram.ext import ContextTypes

from logger import get_logger
from trading.strategy.interface import Strategy


logger = get_logger(__name__)


def on_analyze(strategy: Strategy):
    async def _on_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f"Analyzing strategy {strategy.__class__}")

        analysis, _ = strategy.analyze()

        await update.message.reply_photo(
            photo=analysis.plot,
            caption=analysis.to_html(),
            parse_mode="html",
        )

    return _on_analyze

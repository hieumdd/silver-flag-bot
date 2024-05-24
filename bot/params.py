from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from logger import get_logger
from trading.strategy.interface import Strategy, StrategyParams


logger = get_logger(__name__)


def on_params(strategy: Strategy):
    async def _on_params(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f"Getting strategy {strategy.__class__}'s params")

        await update.message.reply_chat_action(ChatAction.TYPING)
        await update.message.reply_text(
            text=StrategyParams(strategy).to_html(),
            parse_mode=ParseMode.HTML,
        )

    return _on_params

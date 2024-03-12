from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
from typing import Callable
from zoneinfo import ZoneInfo

from apscheduler.triggers.cron import CronTrigger


@dataclass
class Timeframe:
    interval: str
    finished_candle_threshold: timedelta
    cron_hour: Callable[[str], str] = lambda x: x
    cron_minute: Callable[[str], str] = lambda x: x

    def crons(self):
        base_cron = partial(
            CronTrigger,
            day_of_week="0-4",
            second="0",
            timezone=ZoneInfo("Asia/Ho_Chi_Minh"),
        )
        return [
            base_cron(hour=self.cron_hour("9-11"), minute=self.cron_minute("*")),
            base_cron(hour=self.cron_hour("11"), minute=self.cron_minute("0-30")),
            base_cron(hour=self.cron_hour("13-14"), minute=self.cron_minute("*")),
            base_cron(hour=self.cron_hour("14"), minute=self.cron_minute("0-30")),
        ]

    def is_finished(self) -> datetime:
        now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        return now - self.finished_candle_threshold


TF_1MIN = Timeframe("1min", timedelta(minutes=1), lambda x: x, lambda _: "*")
TF_5MIN = Timeframe("5min", timedelta(minutes=5), lambda x: x, lambda cron: f"{cron}/5")
TF_15MIN = Timeframe(
    "15min", timedelta(minutes=15), lambda x: x, lambda cron: f"{cron}/15"
)

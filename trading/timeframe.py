from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
from typing import Callable
from zoneinfo import ZoneInfo

from apscheduler.triggers.cron import CronTrigger


@dataclass
class Timeframe:
    interval: str
    minimum_threshold: timedelta
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
            base_cron(hour=self.cron_hour("9-10"), minute=self.cron_minute("*")),
            base_cron(hour=self.cron_hour("11"), minute=self.cron_minute("0-30")),
            base_cron(hour=self.cron_hour("13"), minute=self.cron_minute("*")),
            base_cron(hour=self.cron_hour("14"), minute=self.cron_minute("0-30")),
        ]

    def is_finished(self) -> datetime:
        now = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).replace(tzinfo=None)
        return now - self.minimum_threshold


TF_1MIN = Timeframe(
    interval="1min",
    minimum_threshold=timedelta(minutes=1),
    cron_hour=lambda x: x,
    cron_minute=lambda _: "*",
)
TF_5MIN = Timeframe(
    interval="5min",
    minimum_threshold=timedelta(minutes=5),
    cron_hour=lambda x: x,
    cron_minute=lambda cron: f"{cron}/5",
)
TF_15MIN = Timeframe(
    interval="15min",
    minimum_threshold=timedelta(minutes=15),
    cron_hour=lambda x: x,
    cron_minute=lambda cron: f"{cron}/15",
)

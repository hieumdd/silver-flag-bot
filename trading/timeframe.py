from functools import partial
from typing import Callable
from zoneinfo import ZoneInfo


from apscheduler.triggers.cron import CronTrigger


class Timeframe:
    def __init__(
        self,
        interval: str,
        cron_hour: Callable[[str], str] = lambda x: x,
        cron_minute: Callable[[str], str] = lambda x: x,
    ):
        self.interval = interval
        self.cron_hour = cron_hour
        self.cron_minute = cron_minute

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


TF_1MIN = Timeframe("1min", lambda x: x, lambda _: "*")
TF_5MIN = Timeframe("5min", lambda x: x, lambda cron: f"{cron}/5")
TF_15MIN = Timeframe("15min", lambda x: x, lambda cron: f"{cron}/15")

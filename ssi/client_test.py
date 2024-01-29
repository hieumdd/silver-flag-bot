from datetime import datetime

from ssi.client import SSIClient
from ssi.options import GetIntradayOptions


class TestClientService:
    client = SSIClient()

    def test_get_intraday(self):
        data = self.client.get_intraday(
            GetIntradayOptions(
                symbol="VN30F1M",
                start_date=datetime.today().date(),
                end_date=datetime.today().date(),
            )
        )
        assert data

from datetime import datetime

from ssi.client import SSIClient


class TestClientService:
    client = SSIClient()

    def test_get_intraday(self):
        data = self.client.get_intraday(
            symbol="VN30F1M",
            start_date=datetime.today().date(),
            end_date=datetime.today().date(),
        )
        assert data

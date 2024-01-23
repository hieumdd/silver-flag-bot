from ssi.client_service import SSIClient
from ssi.client_model import GetIntradayOptions


class TestClientService:
    client = SSIClient()

    def test_get_intraday(self):
        data = self.client.get_intraday(GetIntradayOptions("VN30F1M"))
        assert data

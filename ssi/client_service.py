from datetime import datetime
import os

import jwt
import httpx

from ssi.client_model import GetIntradayOptions

DATA_API_BASE_URL = "https://fc-data.ssi.com.vn/api/v2/Market"


class SSIAuth(httpx.Auth):
    def __init__(self):
        self.consumer_id = os.environ.get("SSI_CONSUMER_ID")
        self.consumer_secret = os.environ.get("SSI_CONSUMER_SECRET")
        self.token = None

    def _validate_token(self):
        if not self.token:
            return False

        exp = jwt.decode(self.token, options={"verify_signature": False})["exp"]
        if exp < datetime.now().timestamp():
            return False

        return True

    def _create_token(self):
        data = httpx.request(
            method="POST",
            url=f"{DATA_API_BASE_URL}/AccessToken",
            json={
                "consumerID": self.consumer_id,
                "consumerSecret": self.consumer_secret,
            },
        ).json()
        self.token = data["data"]["accessToken"]

    def auth_flow(self, request):
        if not self._validate_token():
            self._create_token()

        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


class SSIClient:
    def __init__(self):
        def validate_status_code(response: httpx.Response):
            response.raise_for_status()

        def validate_error(response: httpx.Response):
            response.read()
            data = response.json()
            if data.get("status") != "Success":
                raise ValueError(data)

        self.client = httpx.Client(
            base_url=DATA_API_BASE_URL,
            auth=SSIAuth(),
            event_hooks={"response": [validate_status_code, validate_error]},
        )

    def get_intraday(self, options: GetIntradayOptions):
        response = self.client.request(
            method="GET",
            url="/IntradayOhlc",
            params={
                "Symbol": options.symbol,
                "FromDate": options.from_date.strftime("%d/%m/%Y"),
                "ToDate": options.to_date.strftime("%d/%m/%Y"),
                "PageIndex": options.page_index,
                "PageSize": options.page_size,
                "resolution": options.resolution,
                "ascending": options.ascending,
            },
        )
        return response.json()

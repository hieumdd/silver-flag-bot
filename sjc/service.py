from datetime import datetime

from bs4 import BeautifulSoup
import httpx

from sjc.report import Report, Line


def get_sjc_prices():
    r = httpx.request("GET", "https://sjc.com.vn/xml/tygiavang.xml")
    if r.status_code != 200:
        return None

    data = r.text
    soup = BeautifulSoup(data, features="lxml")

    report = Report(
        updated_at=datetime.strptime(
            soup.find("ratelist").get("updated"), "%H:%M:%S %p %d/%m/%Y"
        ),
        lines=[
            Line(line.get("type"), line.get("buy"), line.get("sell"))
            for line in soup.find("city", attrs={"name": "Hồ Chí Minh"}).find_all(
                "item"
            )
        ],
    )
    return report

from bs4 import BeautifulSoup
import httpx
from typing import *


class ContestLoader:
    """Loads pages from codeforces"""

    # URL Constants
    BASE_URL = "https://codeforces.com/"
    LOGIN_URL = BASE_URL + "enter"
    GYM_URL = BASE_URL + "gym/{gym_id}/"
    STADINGS_URL = GYM_URL + "standings/page/{page}"
    STATUS_URL = GYM_URL + "/status?pageIndex={page}&order=BY_JUDGED_DESC"

    def __init__(self, config: Dict[str, Any]) -> None:
        self.session = httpx.AsyncClient(follow_redirects=True, timeout=10)
        self.handle_or_email = config["handleOrEmail"]
        self.password = config["password"]

    async def login(self):
        login = await self.session.get(self.LOGIN_URL)
        ss = BeautifulSoup(login.text, features="html.parser")

        csrf_token = ss.find("span", {"class": "csrf-token"})["data-csrf"]

        payload = {
            "handleOrEmail": self.handle_or_email,
            "action": "enter",
            "password": self.password,
            "csrf_token": csrf_token,
        }

        result = await self.session.post(self.LOGIN_URL, data=payload)
        
    async def get_problems_page(self, gym_id):
        url = self.GYM_URL.format(gym_id=gym_id)

        data = await self.session.get(url)

        return data.text

    async def get_standings_page(
        self, gym_id, page: int = 1, show_unofficial: bool = True
    ):
        url = self.STADINGS_URL.format(gym_id=gym_id, page=page)

        payload = {
            "newShowUnofficialValue": show_unofficial,
            "action": "toggleShowUnofficial",
        }

        await self.session.post(url, data=payload)

        data = await self.session.get(url)

        return data.text

    async def get_status_page(
        self, gym_id, page: int = 1, show_unofficial: bool = True
    ):
        url = self.STATUS_URL.format(gym_id=gym_id, page=page)

        data = await self.session.get(url)

        return data.text

    
import os
import pickle
from json import dumps
from typing import Any, Callable

import requests
from requests import Response

from vixbuddy.data import Data, Endpoint

# from tastyhelper.logger import log


class API:
    def __init__(self, data: Data, logger: Callable):
        self.data = data
        self.log = logger
        self.session_token: str | None = None
        self.remember_token: str | None = None
        self.quote_url: str | None = None
        self.quote_token: str | None = None
        self.email: str | None = None
        self.username: str | None = None
        self.external_id: str | None = None
        self.base_url: str = (
            # "https://api.cert.tastyworks.com"
            "https://api.tastyworks.com"
        )
        self.websocket_url: str = "wss://streamer.cert.tastyworks.com"
        self.headers = {
            "User-Agent": "tastyhelper/1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        log_message = "API initialized"
        try:
            with open("../pickles/auth.pickle", "rb") as f:
                old_auth = pickle.load(f)
        except FileNotFoundError:
            old_auth = None
            pass
        if old_auth:
            token = old_auth["data"]["session-token"]
            self.headers["Authorization"] = token
            log_message += " with saved session token"
        self.log(log_message, header="api.post_init")

    async def post(self, endpoint: str, body: dict[str, Any]) -> dict[str, Any] | None:
        try:
            requests_response = requests.post(
                self.base_url + endpoint, headers=self.headers, data=dumps(body)
            )
            if not requests_response.ok:
                self.log(
                    f"Error {requests_response.status_code}",
                    header="api.get",
                )
                return None
            return requests_response.json()
        except requests.exceptions.ConnectionError:
            self.log("Connection error", header="api.post")
            return None
        except requests.exceptions.JSONDecodeError:
            self.log("JSON decode error", header="api.post")
            return None

    async def get(self, endpoint: str) -> requests.Response | None:
        try:
            if self.session_token is None:
                await self.authenticate()
            if self.session_token is None:
                return None
            requests_response = requests.get(
                self.base_url + endpoint, headers=self.headers
            )
            if not requests_response.ok:
                self.log(
                    f"Error {requests_response.status_code}",
                    header="api.get",
                )
                return None
            return requests_response
        except requests.exceptions.ConnectionError:
            self.log("Connection error", header="api.get")
            return None
        except requests.exceptions.JSONDecodeError:
            self.log("JSON decode error", header="api.get")
            return None

    async def request_quote_token(self):
        self.log("Requsting quote token", header="api.request_quote_token")
        response = await self.get("/api-quote-tokens")
        if response is None:
            self.log("No response, giving up", header="api.request_quote_token")
            return
        self.quote_token = response.json()["data"]["token"]
        self.quote_url = response.json()["data"]["dxlink-url"]

    async def fetch_accounts(self):
        self.log("Fetching accounts", header="api.fetch_accounts")
        accounts_url = "/customers/me/accounts"
        response = await self.get(endpoint=accounts_url)
        if response is not None:
            self.data.store_response(Endpoint.ACCOUNTS, response)

    async def fetch_balance(self, account_number: str, balances: list):
        self.log(f"Fetching {account_number}", header="api.fetch_balance")
        balance = await self.get(f"/accounts/{account_number}/balances")
        if balance is not None:
            balances.append(balance)

    async def fetch_balances(self):
        balances: list[Response] = []
        for account_number in self.data.accounts.keys():
            await self.fetch_balance(account_number, balances)
        if balances:
            self.data.store_response(Endpoint.BALANCES, balances)

    async def fetch_positions(self):
        raise NotImplementedError

    async def fetch_transactions(self):
        raise NotImplementedError

    async def authenticate(self) -> dict[str, Any] | None:
        login = os.getenv("TASTY_LOGIN")
        password = os.getenv("TASTY_PASSWORD")
        if not login or not password:
            self.log(
                "tasty_login and/or tasty_password env variables not set",
                header="api.authenticate",
            )
            exit(1)
        body = {
            "login": login,
            "password": password,
            "remember-me": True,
        }
        response = await self.post("/sessions", body)
        if response is None:
            return None
        with open("../pickles/auth.pickle", "wb") as f:
            pickle.dump(response, f)
        try:
            self.session_token = response["data"]["session-token"]
            self.remember_token = response["data"]["remember-token"]
            self.username = response["data"]["user"]["username"]
            self.email = response["data"]["user"]["email"]
            self.external_id = response["data"]["user"]["external-id"]
            self.headers["Authorization"] = self.session_token  # pyright: ignore
            return response
        except AttributeError:
            self.log("Attribute not found", header="api.authenticate")
            return None

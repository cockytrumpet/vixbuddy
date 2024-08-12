import enum
import math
from datetime import timedelta
from typing import Any, Callable

import yfinance as yf
from requests import Response

# from tastyhelper.logger import log
from vixbuddy.stats import VIX, Account


class Endpoint(enum.Enum):
    ACCOUNTS = enum.auto()
    BALANCES = enum.auto()
    POSITIONS = enum.auto()
    TRANSACTIONS = enum.auto()


class Data:
    def __init__(self, logger: Callable) -> None:
        self._accounts: Response | None = None
        self._balances: list[Response] = list()
        self.accounts: dict[str, dict[str, Any]] = dict()
        self.vix: dict[str, Any] = dict()
        self.stats_vix: VIX | None = None
        self.stats_accounts: dict[str, Account] = dict()
        self.log = logger
        self.log("Data initialized", header="data.post_init")

    def store_response(
        self, endpoint: Endpoint, response: Response | list[Response]
    ) -> None:
        self.log(
            f"Storing response ({endpoint.__str__()})", header="data.store_response"
        )
        match endpoint:
            case Endpoint.ACCOUNTS if type(response) == Response:
                self._accounts = response
                self.process_accounts()
                # gui.update_accounts()
            case Endpoint.BALANCES if type(response) == list:
                self._balances = response
                self.process_balances()
                # gui.update_balances()
            case Endpoint.POSITIONS:
                raise NotImplementedError
            case Endpoint.TRANSACTIONS:
                raise NotImplementedError
            case _:
                raise ValueError

    async def get_vix(self):
        self.log("Fetching VIX history", header="main.get_vix")
        vix = yf.Ticker("^VIX")
        self.vix = dict(vix.fast_info.items())
        self.vix["history"] = vix
        self.process_vix()

    def process_vix(self):
        vix_open = self.vix["open"]
        vix_last = self.vix["lastPrice"]
        vix_day_low = self.vix["dayLow"]
        vix_day_high = self.vix["dayHigh"]
        last_24d = self.vix["history"].history(period="1mo")
        day24 = last_24d.iloc[0]
        day5 = last_24d.iloc[-5]
        day1 = last_24d.iloc[-1]
        most_recent = last_24d.index.max()
        day24_30m_prices = self.vix["history"].history(
            start=most_recent - timedelta(days=24), interval="30m"
        )
        day5_5m_prices = self.vix["history"].history(
            start=most_recent - timedelta(days=5), interval="5m"
        )
        day5_1m_prices = self.vix["history"].history(
            start=most_recent - timedelta(hours=24), interval="1m"
        )
        vix_5day_open = float(day5["Open"])
        vix_24day_open = float(day24["Open"])
        vix_day_change = vix_last - vix_open
        vix_5day_change = vix_last - vix_5day_open
        vix_24day_change = vix_last - vix_24day_open
        vix_day_change_percent = vix_day_change / vix_last
        vix_5day_change_percent = vix_5day_change / vix_last
        vix_24day_change_percent = vix_24day_change / vix_last
        self.stats_vix = VIX(
            change_1day=vix_day_change,
            change_1day_percent=vix_day_change_percent,
            change_24day=vix_24day_change,
            change_24day_percent=vix_24day_change_percent,
            change_5day=vix_5day_change,
            change_5day_percent=vix_5day_change_percent,
            high_1day=day1["High"],
            high_24day=day24_30m_prices["High"].max(),
            high_5day=day5_5m_prices["High"].max(),
            # TODO: fix these
            iv_rank_1day=(vix_last - vix_day_low) / (vix_day_high - vix_day_low) * 100,
            iv_rank_24day=(vix_last - day24_30m_prices["Low"].min())
            / (day24_30m_prices["High"].max() - day24_30m_prices["Low"].min())
            * 100,
            iv_rank_5day=(vix_last - day5_5m_prices["Low"].min())
            / (day5_5m_prices["High"].max() - day5_5m_prices["Low"].min())
            * 100,
            last=self.vix["lastPrice"],
            low_1day=self.vix["dayLow"],
            low_24day=day24_30m_prices["Low"].min(),
            low_5day=day5_5m_prices["Low"].min(),
            open_1day=day1["Open"],
            open_24day=day24["Open"],
            open_5day=day5["Open"],
            nums_24day=list(day24_30m_prices.get("Close")),
            nums_5day=list(day5_5m_prices.get("Close")),
            nums_1day=list(day5_1m_prices.get("Close")),
        )

    def process_accounts(self) -> None:
        if self._accounts is None:
            return
        accounts = self._accounts.json()["data"]["items"]
        for account in accounts:
            account_number = account["account"]["account-number"]
            if account_number == "1DA13984":  # skip leftover "TW Challenge" account
                continue
            self.log(f"Processing {account_number}", header="data.process_accounts")
            self.accounts[account_number] = account

    def process_balances(self) -> None:
        if self.stats_vix is None:
            return
        match True:
            case _ if self.stats_vix.last <= 15:
                max_short_alloc = 0.25
            case _ if self.stats_vix.last <= 20:
                max_short_alloc = 0.3
            case _ if self.stats_vix.last <= 30:
                max_short_alloc = 0.35
            case _ if self.stats_vix.last <= 40:
                max_short_alloc = 0.4
            case _:
                max_short_alloc = 0.5
        for balance in self._balances:
            self.process_balance(balance.json()["data"], max_short_alloc)

    def process_balance(self, balance: dict[str, Any], max_short_alloc: float) -> None:
        account_number = balance["account-number"]
        self.log(
            f"Processing balances for {account_number}", header="data.process_balance"
        )
        self.accounts[account_number]["balances"] = balance

        net_liq = float(balance["net-liquidating-value"])
        self.stats_accounts[account_number] = Account(
            number=balance["account-number"],
            nickname=self.accounts[account_number]["account"]["nickname"],
            net_liquidating_value=net_liq,
            max_short_premium_percent=max_short_alloc,
            cash_or_low_risk_percent=(1 - max_short_alloc),
            max_short_premium=max_short_alloc * net_liq,
            cash_or_low_risk=(1 - max_short_alloc) * net_liq,
            max_undefined_risk_bpr=net_liq * 0.07,
            max_defined_risk_bpr=net_liq * 0.05,
            portfolio_theta_min=math.ceil(net_liq * 0.001),
            portfolio_theta_max=math.floor(net_liq * 0.002),
        )

from dataclasses import dataclass, field
from typing import Any, Tuple

from rich.text import Text


@dataclass(slots=True)
class VIX:
    change_1day: float = 0.0
    change_1day_percent: float = 0.0
    change_24day: float = 0.0
    change_24day_percent: float = 0.0
    change_5day: float = 0.0
    change_5day_percent: float = 0.0
    high_1day: float = 0.0
    high_24day: float = 0.0
    high_5day: float = 0.0
    iv_rank_1day: float = 0.0
    iv_rank_24day: float = 0.0
    iv_rank_5day: float = 0.0
    last: float = 0.0
    low_1day: float = 0.0
    low_24day: float = 0.0
    low_5day: float = 0.0
    nums_1day: list[float] = field(default_factory=list)
    nums_24day: list[float] = field(default_factory=list)
    nums_5day: list[float] = field(default_factory=list)
    open_1day: float = 0.0
    open_24day: float = 0.0
    open_5day: float = 0.0

    def from_24day_to_DataTable(self) -> list[Tuple[Any]]:
        data_table = [
            ("", "", "", ""),
            (
                self.color_label(" month (24d)"),
                self.color_change(self.change_24day),
                self.color_change(self.change_24day_percent * 100, percent=True),
                "",
            ),
            ("", "", "", ""),
            (
                self.color_label(" open"),
                self.color_value(f"{self.open_24day:.2f}"),
                self.color_label("rank"),
                self.color_value(f"{self.iv_rank_24day:.2f}"),
            ),
            (
                self.color_label(" low"),
                self.color_value(f"{self.low_24day:.2f}"),
                self.color_label("high"),
                self.color_value(f"{self.high_24day:.2f}"),
            ),
        ]
        return data_table  # pyright: ignore

    def from_5day_to_DataTable(self) -> list[Tuple[Any]]:
        data_table = [
            ("", "", "", ""),
            (
                self.color_label(" week (5d) "),
                self.color_change(self.change_5day),
                self.color_change(self.change_5day_percent * 100, percent=True),
                "",
            ),
            (
                "",
                "",
                "",
                "",
            ),
            (
                self.color_label(" open"),
                self.color_value(f"{self.open_5day:.2f}"),
                self.color_label("rank"),
                self.color_value(f"{self.iv_rank_5day:.2f}"),
            ),
            (
                self.color_label(" low"),
                self.color_value(f"{self.low_5day:.2f}"),
                self.color_label("high"),
                self.color_value(f"{self.high_5day:.2f}"),
            ),
        ]
        return data_table  # pyright: ignore

    def from_today_to_DataTable(self) -> list[Tuple[Any]]:
        data_table = [
            ("", "", "", ""),
            (
                self.color_label(" day        "),
                self.color_change(self.change_1day),
                self.color_change(self.change_1day_percent * 100, percent=True),
                "",
            ),
            (
                "",
                "",
                "",
                "",
            ),
            (
                self.color_label(" open"),
                self.color_value(f"{self.open_1day:.2f}"),
                self.color_label("rank"),
                self.color_value(f"{self.iv_rank_1day:.2f}"),
            ),
            (
                self.color_label(" low"),
                self.color_value(f"{self.low_1day:.2f}"),
                self.color_label("high"),
                self.color_value(f"{self.high_1day:.2f}"),
            ),
            (self.color_label(" last"), self.color_value(f"{self.last:.2f}"), "", ""),
        ]
        return data_table  # pyright: ignore

    def color_change(self, price: float, percent: bool = False) -> Text:
        spaces_to_add = 0
        style = "bold"
        if price < 0:
            style += " red"
        elif price > 0:
            spaces_to_add += 1
            style += " green"
        else:
            spaces_to_add += 1
            style += " white"
        price_str = spaces_to_add * " "
        price_str += f"{price:.2f}"
        price_str += "%" if percent else ""
        return Text(price_str, style=style, justify="right")

    def color_label(self, label: str) -> Text:
        return Text(label, style="white", justify="left")

    def color_value(self, value: str) -> Text:
        return Text(value, style="deepskyblue", justify="right")


@dataclass(slots=True)
class Account:
    number: str = ""
    nickname: str = ""
    net_liquidating_value: float = 0.0
    max_short_premium_percent: float = 0.0
    cash_or_low_risk_percent: float = 0.0
    max_short_premium: float = 0.0
    cash_or_low_risk: float = 0.0
    max_undefined_risk_bpr: float = 0.0
    max_defined_risk_bpr: float = 0.0
    portfolio_theta_min: float = 0.0
    portfolio_theta_max: float = 0.0

    def to_DataTable(self) -> list[Tuple[Any]]:
        data_table = [
            ("", ""),
            (self.color_label(f"{self.number}"), self.color_label(f"{self.nickname}")),
            (
                self.color_label("net liq"),
                self.color_value(f"{self.net_liquidating_value:.2f}"),
            ),
            (
                self.color_label("cash or low risk"),
                self.color_value(f"{self.cash_or_low_risk:.2f}"),
            ),
            (
                self.color_label("max short premium"),
                self.color_value(f"{self.max_short_premium:.2f}"),
            ),
            (
                self.color_label("max undefined risk"),
                self.color_value(f"{self.max_undefined_risk_bpr:.2f}"),
            ),
            (
                self.color_label("max defined risk"),
                self.color_value(f"{self.max_defined_risk_bpr:.2f}"),
            ),
            (
                self.color_label("max portfolio theta"),
                self.color_value(f"{self.portfolio_theta_max:.2f}"),
            ),
            (
                self.color_label("min portfolio theta"),
                self.color_value(f"{self.portfolio_theta_min:.2f}"),
            ),
        ]
        return data_table  # pyright: ignore

    def color_label(self, label: str) -> Text:
        return Text(label, style="bold", justify="left")

    def color_value(self, value: str) -> Text:
        return Text(value, style="darkgrey", justify="right")

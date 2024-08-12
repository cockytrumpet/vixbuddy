import math

from vixbuddy.logger import log
from vixbuddy.stats import VIX, Account


async def print_stats(vix: VIX, accounts: dict[str, Account]):
    """print all stats to stdout"""
    log("Printing stats", header="main.print_tasks")
    print(
        f"VIX\n",
        f"last: {vix.last:.2f} (day IVR: {(vix.last - vix.low_1day)/(vix.high_1day - vix.low_1day)*100:.1f})\n",
        f"day open: {vix.open_1day:.2f}\n",
        f"day low: {vix.low_1day:.2f}\n",
        f"day high: {vix.high_1day:.2f}\n",
        f"day change: {vix.change_1day:.2f} ({vix.change_1day_percent * 100:.2f}%)\n",
        f"5-day change: {vix.change_5day:.2f} ({vix.change_5day_percent * 100:.2f}%)\n",
        f"24-day change: {vix.change_24day:.2f} ({vix.change_24day_percent * 100:.2f}%)\n",
    )
    for account in accounts.values():
        print(
            f"{account.number} - {account.nickname}\n",
            f"net liq: {account.net_liquidating_value:.2f}\n",
            f"max short premium allocation({account.max_short_premium_percent * 100}%): {account.max_short_premium:.2f}\n",
            f"cash/low-risk allocation({(account.cash_or_low_risk_percent) * 100}%): { account.cash_or_low_risk:.2f}\n",
            f"max undefined risk BPR(7%): {account.net_liquidating_value * .07:.2f}\n"
            f" max defined risk BPR(5%): {account.net_liquidating_value * .05:.2f}\n",
            f"portfolio theta min(0.1%): {math.ceil(account.net_liquidating_value * .001)}\n",
            f"portfolio theta max(0.2%): {math.floor(account.net_liquidating_value * .002)}",
            # TODO: figure out portfolio delta
        )

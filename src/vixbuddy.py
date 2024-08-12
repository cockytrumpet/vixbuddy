import time
from functools import partial
from typing import Any, Tuple

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import DataTable, Footer, RichLog, Sparkline

from vixbuddy.api import API
from vixbuddy.data import *


class AppFooter(Footer):
    DEFAULT_CSS = """
    Footer {
        height: 1;
        dock: bottom;
    }
    """


class LogContainer(Container):
    DEFAULT_CSS = """
    LogContainer {
        height: 5;
        width: 100%;
        padding: 0 1 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id="log")


class VixGraphs(Vertical):
    # fmt: off
    DEFAULT_CSS = """
    VixGraphs {
        height: 1fr;
        width: 1fr;
        align: center middle;
        padding: 0 2 1 0;
    }

    #fst > .sparkline--max-color {
        color: lime;
    }
    #fst > .sparkline--min-color {
        color: red;
    }
    """
    # fmt: on

    def __init__(self, nums: list[float] | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nums = nums

    def compose(self) -> ComposeResult:
        yield Sparkline(self.nums, summary_function=max, id="fst")


class VixStats(DataTable):
    DEFAULT_CSS = """
    VixStats {
        height: 1fr;
        width: 46;
        dock: left;
        # margin: 1 1 0 0;
    }
    """

    def __init__(self, table: list[Tuple[Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.table[0])
        table.add_rows(self.table[1:])
        table.cursor_type = "none"
        table.show_header = False


class AccountStats(DataTable):
    DEFAULT_CSS = """
    AccountStats {
        height: 1fr;
        width: auto;
        dock: left;
        # margin: 0 3 0 3;
        content-align: center middle;
    }
    """

    def __init__(self, table: list[Tuple[Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.table[0])
        table.add_rows(self.table[2:])
        table.cursor_type = "none"
        table.show_header = False
        table.styles.border = ("round", "grey")
        table.styles.align = ("center", "middle")
        table.border_title = self.table[1][1]  # pyright: ignore
        table.border_subtitle = self.table[1][0]
        table.border_title_color = "cyan"
        table.border_subtitle_color = "cyan"
        table.border_title_align = "left"
        table.border_title_align = "left"


class MainContainer(Vertical):
    DEFAULT_CSS = """
    MainContainer {
        height: 1fr;
        width: 1fr;
    }
    """


class PortfolioView(Screen):
    DEFAULT_CSS = """
    #VixContainer {
        height: 1fr;
        width: 1fr;
        margin: 1 0 0 0;
    }
    #VixContainer > Horizontal {
        # border: round grey;
    }
    #AccountsContainer {
        height: 10;
        width: 1fr;
        margin: 1 0 0 0;
    }
    #AccountsContainer > Vertical {
        height: 10;
        width: 36;
        margin: 0 0 0 0;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data: Data | None = None
        self.api: API | None = None

    def logger(self, message: str, destination: Widget, header: str):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # header_str = f" [{header}]: "
        header_str = " : "
        message_str = time_str + header_str + message
        destination.write(f"[yellow]{message_str}")

    def compose(self) -> ComposeResult:
        yield Vertical(id="MainContainer")
        yield LogContainer(id="LogContainer")
        yield AppFooter()

    async def on_mount(self) -> None:
        log_widget = self.query("#log").first()
        logger = partial(self.logger, destination=log_widget)
        self.data = Data(logger=logger)
        self.api = API(data=self.data, logger=logger)

        tasks = []
        tasks.append(self.data.get_vix())
        tasks.append(self.api.fetch_accounts())
        for task in tasks:
            await task
        await self.api.fetch_balances()
        main = self.query("#MainContainer").first()
        main.mount(AfterProcessing(self.data.stats_vix, self.data.stats_accounts))


class AfterProcessing(Widget):
    def __init__(self, vix: VIX, accounts: dict[str, Account], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vix = vix
        self.accounts = accounts
        self.table_24day = self.vix.from_24day_to_DataTable()
        self.table_5day = self.vix.from_5day_to_DataTable()
        self.table_1day = self.vix.from_today_to_DataTable()

    def compose(self) -> ComposeResult:
        with Vertical(id="VixContainer"):
            for table, data, id in [
                (self.table_24day, self.vix.nums_24day, "graph24"),
                (self.table_5day, self.vix.nums_5day, "graph5"),
                (self.table_1day, self.vix.nums_1day, "graph1"),
            ]:
                with Horizontal(id=f"VixRow_{id[5:]}"):
                    yield VixStats(table=table)
                    yield VixGraphs(id=id, nums=data)
        with Horizontal(id="AccountsContainer"):
            for account_number, account in self.accounts.items():
                with Vertical(id=f"account_{account_number}"):
                    yield AccountStats(
                        table=account.to_DataTable(),
                        id=f"details_{account_number}",
                    )


class VixHelper(App):
    BINDINGS = [
        Binding(key="q", action="quit", description="quit"),
        Binding(key="r", action="refresh", description="refresh"),
    ]

    def on_ready(self) -> None:
        self.push_screen(PortfolioView())

    def action_refresh(self):
        self.pop_screen()
        self.push_screen(PortfolioView())


if __name__ == "__main__":
    app = VixHelper()
    app.run()

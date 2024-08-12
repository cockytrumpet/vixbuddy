from dataclasses import dataclass, field
from json import dumps
from typing import Any

import websockets

from vixbuddy.logger import log


@dataclass(slots=True)
class Account_streamer:
    url: str
    token: str
    accounts: list[str]
    headers: dict[str, Any] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.headers.update(
            {
                "User-Agent": "tastyhelper/1.0",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": self.token,
            }
        )
        self.body.update(
            {
                "action": "connect",
                "value": self.accounts,
                "auth-token": self.token,
                "request-id": 42,
            }
        )

    async def connect(self) -> None:
        async with websockets.connect(
            self.url, extra_headers=self.headers
        ) as websocket:
            # subscribe to notifications from accounts
            msg = dumps(self.body)
            await websocket.send(msg)
            # make this loop forever?
            while True:
                response = await websocket.recv()
                log(f"{response}", header="streamer.connect")
                # process messages here

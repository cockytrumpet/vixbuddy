import time
from typing import Optional


def log(
    message: str,
    header: Optional[str] = None,
    to_file: bool = True,
    to_stdout: bool = True,
):
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    header_str = f" [{header}]: " if header else ": "
    message_str = time_str + header_str + message

    if to_file:
        with open("../logs/tastyhelper.log", "a") as f:
            f.write(message_str + "\n")

    if to_stdout:
        print(message_str)

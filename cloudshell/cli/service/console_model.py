from __future__ import annotations

from attrs import define


@define
class ConsoleParams:
    host: str
    username: str
    password: str
    port: int

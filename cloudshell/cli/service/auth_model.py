from __future__ import annotations

from attrs import define, field


@define
class Auth:
    username: str = ""
    password: str = field(default="", repr=False)
    enable_password: str = field(default="", repr=False)
    key: str = field(default="", repr=False)
    key_passphrase: str = field(default="", repr=False)

from dataclasses import dataclass


@dataclass
class LMS_Color:
    red: int
    green: int
    blue: int
    alpha: int
    name: str | None = None

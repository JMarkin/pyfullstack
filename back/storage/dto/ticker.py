from dataclasses import dataclass


@dataclass
class Ticker:
    name: str

@dataclass
class PriceTimestamp:
    price: int
    timestamp: int

@dataclass
class TickerDiff:
    name: str
    diff: int

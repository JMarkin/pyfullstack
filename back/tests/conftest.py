import logging
from datetime import datetime
from logging.config import dictConfig
from typing import Any

import pytest
from fastapi.testclient import TestClient

from back.settings import settings
from back.storage.abc import ABCStorage, PriceTimestamp, Ticker, TickerDiff

dictConfig(settings.log_config)

logger = logging.getLogger(__name__)


class DictStorage(ABCStorage):
    """Хранилище в опертивке.

    Немного вранье т.к. acid не соблюден
    """

    _d: dict[str, Any] = {
        "ticker": {},
        "ticker_state": {},
    }

    def __init__(self):
        self._d: dict[str, Any] = {
            "ticker": {},
            "ticker_state": {},
        }

    async def get_ticker(
        self,
        ticker_name: str,
        left: int | None = None,
        right: int | None = None,
    ) -> list[PriceTimestamp]:
        """Получение данных по цене тикера
        Args:
            ticker_name (str): код тикера
            left (int | None): timestamp интервала слева, по умолчанию с самого начала
            right (int | None): timestamp интервала справа, по умолчанию все справа
            count (int | None): количество данных на интервале, по умолчанию все
        Returns:
            list[Ticker]: список тикеров в заданом интервале
        """

        _ticker = self._d["ticker"]
        _ticker_state = self._d["ticker_state"][ticker_name]

        if left is None:
            left = _ticker_state[0]["timestamp"]

        if right is None:
            right = _ticker_state[-1]["timestamp"]


        res = []
        for i in range(len(_ticker_state)):
            state = _ticker_state[i]
            if state["timestamp"] < left or state["timestamp"] > right:
                continue
            resp.append(PriceTimestamp(price=state["price"], timestamp=state["timestamp"]))

        return resp

    async def insert_tickers_state(self, tickers: list[TickerDiff], timestamp: int):
        """Добавление данных по тикерам
        Args:
            tickers (list[Ticker]): список тикеров с данными дял обновления
            timestamp (int): время дял которого добавить
        """
        for t in tickers:
            _ticker = self._d["ticker_state"][t.name]
            new_price = self._d["ticker"][t.name]["price"] + t.diff
            _ticker.append({
                "price": new_price,
                "timestamp": timestamp,
            })
            self._d["ticker"][t.name]["price"] = new_price

    async def get_tickers(self) -> list[Ticker]:
        """Получение всех имеющихся тикеров."""
        return [Ticker(name=k) for k in self._d["ticker"]]

    async def insert_tickers(self, tickers: list[str]):
        """Добавление тикеров
        Args:
            tickers (list[str]): список имен тикеров
        """
        ts = int(datetime.utcnow().timestamp())
        for ticker in tickers:
            self._d["ticker"][ticker] = {"price": 0, "first_timestamp": ts, "last_timestamp": ts}
        for name in tickers:
            if not name in self._d["ticker_state"]:
                self._d["ticker_state"][name] = []
            self._d["ticker_state"][name].append({
                "price": 0,
                "timestamp": ts,
            },)


@pytest.fixture
def storage(monkeypatch):

    st = DictStorage()

    def mock_st():
        return st

    monkeypatch.setattr("back.app.configure_storage", mock_st)
    return st


@pytest.fixture
async def tickers(storage):
    tickers = ["1", "2"]
    await storage.insert_tickers(tickers)

    return tickers


@pytest.fixture
def client(storage):
    from back.app import app
    return TestClient(app)

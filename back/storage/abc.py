import abc

from back.settings import Settings, settings

from .dto.ticker import Ticker, TickerDiff, PriceTimestamp


class ABCStorage(abc.ABC):
    """Интерфейс для работы с хранилищем."""

    settings: Settings = settings

    @abc.abstractmethod
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
        Returns:
            list[PriceTimestamp]: список тикеров в заданом интервале
        """

    @abc.abstractmethod
    async def insert_tickers_state(self, tickers: list[TickerDiff], timestamp: int):
        """Добавление данных по тикерам
        Args:
            tickers (list[Ticker]): список тикеров с данными дял обновления
            timestamp (int): время дял которого добавить
        """

    @abc.abstractmethod
    async def get_tickers(self) -> list[Ticker]:
        """Получение всех имеющихся тикеров."""


    @abc.abstractmethod
    async def insert_tickers(self, tickers: list[str]):
        """Добавление тикеров
        Args:
            tickers (list[str]): список имен тикеров
        """


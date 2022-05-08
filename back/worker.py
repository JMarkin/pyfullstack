import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Process

from back.storage.abc import ABCStorage, TickerDiff
from back.ticker.utils import generate_movement

logger = logging.getLogger(__name__)


@dataclass
class CollectTickersWorker(Process):
    """Воркер для обновления данных."""
    storage: ABCStorage

    async def collect(self):
        tickers = await self.storage.get_tickers()
        logger.info('DB tickers %s', tickers)
        while 1:
            ticker_diffs = []
            for ticker in tickers:
                diff = TickerDiff(name=ticker.name, diff=generate_movement())
                ticker_diffs.append(diff)

            dt = datetime.utcnow()
            ts = int(dt.timestamp())
            logger.info('update states %s', ts)
            await self.storage.insert_tickers_state(ticker_diffs, ts)
            await asyncio.sleep(1)

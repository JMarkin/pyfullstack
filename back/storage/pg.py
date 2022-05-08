import logging
from contextlib import asynccontextmanager
from dataclasses import InitVar, dataclass, field
from datetime import datetime

import asyncpg

from .abc import ABCStorage, PriceTimestamp, Ticker, TickerDiff

logger = logging.getLogger(__name__)


@dataclass  # type: ignore
class PgStorage(ABCStorage):
    """Реализация стороджа для asyncpg."""
    dsn: InitVar[str]
    _pool: asyncpg.Pool = field(default=None, init=False, repr=False)

    def __post_init__(self, dsn: str):
        self._pool = asyncpg.create_pool(dsn)

    @asynccontextmanager
    async def _acquire(self):
        if not self._pool._initialized:
            self._pool = await self._pool

        async with self._pool.acquire() as conn:
            yield conn

    get_ticker_sql = '''
    select t.price, t.ts
    from ticker_state t
    left join ticker t2 on t.ticker_pk =t2."name"
    where t.ticker_pk = $1
    '''
    get_tickers_interval_where_all = ' and t.ts >= $2 and t.ts <= $3'
    get_tickers_interval_where_right = ' and t.ts >= t2.first_timestamp and t.ts <= $2'
    get_tickers_interval_where_left = ' and t.ts >= $2 and t.ts <= t2.last_timestamp'
    get_tickers_interval_where_none = ' and t.ts >= t2.first_timestamp and t.ts <= t2.last_timestamp'

    async def get_ticker(
        self,
        ticker_name: str,
        left: int | None = None,
        right: int | None = None,
    ) -> list[PriceTimestamp]:
        if left and right:
            sql = self.get_ticker_sql + self.get_tickers_interval_where_all
            values = [ticker_name, left, right]
        elif left:
            sql = self.get_ticker_sql + self.get_tickers_interval_where_left
            values = [ticker_name, left]
        elif right:
            sql = self.get_ticker_sql + self.get_tickers_interval_where_right
            values = [ticker_name, right]
        else:
            sql = self.get_ticker_sql + self.get_tickers_interval_where_none
            values = [ticker_name]

        async with self._acquire() as conn:
            ticker_states = await conn.fetch(sql, *values)

        return [PriceTimestamp(price=t['price'], timestamp=t['ts']) for t in ticker_states]

    insert_tickers_state_sql = '''
    insert into ticker_state(ticker_pk, price, ts)
    (
        select name, price+$1, $2
        from ticker where name=$3
    )
    '''

    async def insert_tickers_state(self, tickers: list[TickerDiff], timestamp: int):
        async with self._acquire() as conn:
            await conn.executemany(self.insert_tickers_state_sql, [(t.diff, timestamp, t.name) for t in tickers])

    get_tickers_sql = 'select name from ticker order by name'

    async def get_tickers(self) -> list[Ticker]:
        async with self._acquire() as conn:
            tickers = await conn.fetch(self.get_tickers_sql)
        resp = []
        for t in tickers:
            resp.append(Ticker(name=t['name']))
        return resp

    insert_tickers_sql = 'insert into ticker(name, first_timestamp, last_timestamp) values ($1, $2, $3)'

    async def insert_tickers(self, tickers: list[str]):
        ts = int(datetime.utcnow().timestamp())
        values = [(t, ts, ts) for t in tickers]
        async with self._acquire() as conn:
            await conn.executemany(self.insert_tickers_sql, values)
        tickers_diff = [TickerDiff(name=t, diff=0) for t in tickers]
        await self.insert_tickers_state(tickers_diff, ts)

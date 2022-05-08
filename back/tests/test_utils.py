from back.tests.conftest import DictStorage

from back.ticker.utils import gen_tickers

async def test_gen_tickers(storage: DictStorage):
    await gen_tickers(storage)

    assert len(storage._d["ticker"]) == 100

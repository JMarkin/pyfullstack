import asyncio

import pytest
from fastapi.testclient import TestClient

from back.tests.conftest import DictStorage
from back.worker import CollectTickersWorker


@pytest.fixture
def worker(storage: DictStorage):
    worker = CollectTickersWorker(storage)
    return worker


async def test_worker_collect(worker: CollectTickersWorker, tickers: list[str], storage: DictStorage):
    task = asyncio.create_task(worker.collect())

    await asyncio.sleep(2)

    task.cancel()
    assert len(storage._d["ticker_state"][tickers[0]]) > 1

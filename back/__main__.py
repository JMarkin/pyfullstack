import asyncio
from logging.config import dictConfig

import typer

from back.settings import settings
from back.storage.utils import configure_storage
from back.ticker.utils import gen_tickers

from .worker import CollectTickersWorker

dictConfig(settings.log_config)

cmd = typer.Typer()


async def _init_tickers():
    st = configure_storage()
    await gen_tickers(st)


@cmd.command()
def init_ticker():
    asyncio.run(_init_tickers())


async def _collect_worker():
    storage = configure_storage()
    worker = CollectTickersWorker(storage=storage)
    await worker.collect()


@cmd.command()
def collect_worker():
    asyncio.run(_collect_worker())

cmd()

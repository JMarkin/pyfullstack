from random import random

from back.storage.abc import ABCStorage


def generate_movement():
    movement = -1 if random() < 0.5 else 1
    return movement


async def gen_tickers(st: ABCStorage):
    tickers = [f"ticker_{str(i).zfill(2)}" for i in range(100)]
    await st.insert_tickers(tickers)
        

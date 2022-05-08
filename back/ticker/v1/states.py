from fastapi import APIRouter, Depends, Query

from back.schemas.base import BaseModel
from back.storage.abc import ABCStorage, PriceTimestamp
from back.storage.utils import get_storage

router = APIRouter()


class State(BaseModel):
    prices: list[int]
    timestamps: list[int]


@router.get('/state/{name}', response_model=State)
async def get_ticker_states(
        name: str,
        storage: ABCStorage = Depends(get_storage),
        left: int = Query(None),
        right: int = Query(None),
) -> list[State]:
    values: list[PriceTimestamp] = await storage.get_ticker(name, left, right)

    res = State(prices=[], timestamps=[])
    for v in values:
        res.prices.append(v.price)
        res.timestamps.append(v.timestamp)
    return res

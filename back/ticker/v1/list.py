from fastapi import APIRouter, Depends

from back.storage.abc import ABCStorage
from back.storage.utils import get_storage

router = APIRouter()


@router.get('/list')
async def tickers(st: ABCStorage = Depends(get_storage)):
    tickers = await st.get_tickers()

    return [v.name for v in tickers]

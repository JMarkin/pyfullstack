import asyncio
from logging.config import dictConfig

from fastapi import APIRouter, FastAPI

from back.settings import settings
from back.storage.utils import configure_storage
from back.ticker.router import router as ticker_router
from back.utils.json import JSONResponse

dictConfig(settings.log_config)

try:
    # noinspection PyPackageRequirements
    import uvloop

    uvloop.install()
except ImportError:
    uvloop = None
app = FastAPI(
    title='template',
    redoc_url='/redoc/',
    docs_url='/docs/',
    openapi_url='/openapi.json',
    default_response_class=JSONResponse,
)

root_router = APIRouter()

root_router.include_router(ticker_router)

app.include_router(root_router)


@app.on_event('startup')
async def init_storage():
    app.storage = configure_storage()

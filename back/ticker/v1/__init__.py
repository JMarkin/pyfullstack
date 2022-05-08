from fastapi import APIRouter

from .list import router as list_router
from .states import router as states_router

router = APIRouter(prefix='/v1')

router.include_router(states_router)
router.include_router(list_router)

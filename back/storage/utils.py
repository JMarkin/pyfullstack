from fastapi import Request

from back.settings import settings

from .abc import ABCStorage
from .pg import PgStorage


def configure_storage():
    return PgStorage(settings.DATABASE_URL)

def get_storage(request: Request) -> ABCStorage:
    return request.app.storage

import enum
import importlib
import traceback
from datetime import date, datetime, time
from inspect import istraceback
from typing import Iterable

import pytz
from fastapi.responses import JSONResponse as FastAPIResponse


def default_dumps(obj):

    if istraceback(obj):
        return "".join(traceback.format_tb(obj)).strip()

    if isinstance(obj, (date, time)):
        return obj.isoformat()

    if isinstance(obj, enum.Enum):
        return obj.value

    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            return obj.astimezone(pytz.UTC).isoformat()
        return obj.astimezone().isoformat()

    return str(obj)


JSON = "json"
ORJSON = "orjson"
UJSON = "ujson"

# Detect mode
mode = JSON
for json_lib in (ORJSON, UJSON, JSON):
    try:
        json = importlib.import_module(json_lib)
    except ImportError:
        continue
    else:
        mode = json_lib
        break

if mode == ORJSON:

    def dumps(data, **kwargs) -> str:
        return json.dumps(
            data,
            default=kwargs.pop("default", default_dumps),
            option=json.OPT_SERIALIZE_UUID | json.OPT_NAIVE_UTC,
        ).decode("utf-8")

    def loads(data, **kwargs) -> dict:
        return json.loads(data)

elif mode == UJSON:

    def convert(x, default=default_dumps):
        if isinstance(x, (str, int, float, bool)) or x is None:
            return x
        if isinstance(x, dict):
            return {k: convert(v, default) for k, v in x.items()}
        if isinstance(x, Iterable):
            return [convert(elem, default) for elem in x]
        return default(x)

    def dumps(data, **kwargs) -> str:
        data = convert(data, kwargs.get("default", default_dumps))
        return json.dumps(data, ensure_ascii=False, escape_forward_slashes=False)

    def loads(data, **kwargs) -> dict:
        return json.loads(data)
else:

    def dumps(data, **kwargs) -> str:
        default = kwargs.pop("default", default_dumps)
        return json.dumps(data, default=default, **kwargs)

    def loads(data, **kwargs) -> dict:
        return json.loads(data, **kwargs)


class JSONResponse(FastAPIResponse):
    media_type = "application/json"

    def render(self, content) -> bytes:
        return dumps(content).encode("utf-8")

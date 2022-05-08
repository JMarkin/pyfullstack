from functools import cached_property

from pydantic import BaseModel as DefaultBaseModel

from back.utils import json


class BaseModel(DefaultBaseModel):

    class Config:
        allow_population_by_field_name = True

        json_loads = json.loads
        json_dumps = json.dumps
        anystr_strip_whitespace = True
        keep_untouched = (cached_property, property)

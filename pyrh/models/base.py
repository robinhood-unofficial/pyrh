"""Base Model."""

from types import SimpleNamespace
from typing import Any, Dict, Mapping, Tuple

from marshmallow import INCLUDE, Schema, post_load

from pyrh.common import JSON


MAX_REPR_LEN = 50


class BaseModel(SimpleNamespace):
    """TODO."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs = {
            k: UnknownModel(**v) if isinstance(v, Mapping) else v
            for k, v in kwargs.items()
        }

        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        repr_ = super().__repr__()
        if len(repr_) > MAX_REPR_LEN:
            return repr_[:MAX_REPR_LEN] + " ...)"
        else:
            return repr_

    def __len__(self) -> int:
        return len(self.__dict__)


class UnknownModel(BaseModel):
    """TODO."""

    pass


class BaseSchema(Schema):
    """TODO."""

    __model__: Any = UnknownModel

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_object(self, data: JSON, **kwargs: Any) -> "__model__":
        return self.__model__(**data)

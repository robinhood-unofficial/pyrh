"""Base Model."""

from types import SimpleNamespace
from typing import Any, Dict, Mapping

from marshmallow import INCLUDE, Schema, post_load


JSON = Dict[str, Any]
MAX_REPR_LEN = 50


def _process_dict_values(value: Any) -> Any:
    """Process a returned from a JSON response.

    Args:
        value: A dict, list, or value returned from a JSON response.

    Returns:
        Either an UnknownModel, a List of processed values, or the original value \
            passed through.

    """
    if isinstance(value, Mapping):
        return UnknownModel(**value)
    elif isinstance(value, list):
        return [_process_dict_values(v) for v in value]
    else:
        return value


class BaseModel(SimpleNamespace):
    """BaseModel that all models should inherit from.

    Note:
        If a passed parameter is a nested dictionary, then it is created with the
        `UnknownModel` class. If it is a list, then it is created with

    Args:
        **kwargs: All passed parameters as converted to instance attributes.
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs = {k: _process_dict_values(v) for k, v in kwargs.items()}

        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        """Return a default repr of any Model.

        Returns:
            The string model parameters up to a `MAX_REPR_LEN`.

        """
        repr_ = super().__repr__()
        if len(repr_) > MAX_REPR_LEN:
            return repr_[:MAX_REPR_LEN] + " ...)"
        else:
            return repr_

    def __len__(self) -> int:
        """Return the length of the model.

        Returns:
            The number of attributes a given model has.

        """
        return len(self.__dict__)


class UnknownModel(BaseModel):
    """A convenience class that inherits from `BaseModel`."""

    pass


class BaseSchema(Schema):
    """The default schema for all models."""

    __model__: Any = UnknownModel
    """Determines the object that is created when the load method is called."""

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_object(self, data: JSON, **kwargs: Any) -> "__model__":
        """Build model for the given `__model__` class attribute.

        Args:
            data: The JSON diction to use to build the model.
            **kwargs: Unused but required to match signature of `Schema.make_object`

        Returns:
            An instance of the `__model__` class.

        """
        return self.__model__(**data)

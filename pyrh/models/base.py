"""Base Model."""
from collections.abc import MutableSequence
from types import SimpleNamespace
from typing import Any, Callable, Dict, Iterable, Mapping, Optional

from marshmallow import INCLUDE, Schema, fields, post_load
from yarl import URL

from pyrh.exceptions import InvalidOperation

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


class UnknownModel(BaseModel):
    """A convenience class that inherits from `BaseModel`."""

    pass


class BaseSchema(Schema):
    """The default schema for all models."""

    __model__: Any = UnknownModel
    """Determine the object that is created when the load method is called."""
    __first__: Optional[str] = None
    """Determine if `make_object` will try to get the first element the input key."""

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
        if self.__first__ is not None:
            data_list = data.get("results", [{}])
            # guard against empty return list of a valid results return
            data = data_list[0] if len(data_list) != 0 else {}
        return self.__model__(**data)


def has_results(func: Callable[..., Any]) -> Callable[..., Any]:
    """Check whether a particular function has results when filtering its data.

    Args:
        func: The function to be decorated

    Returns:
        The decorated function which raises `InvalidOperation` if the \
            decorated function does not have the `results` attribute

    """

    def _decorator(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not hasattr(self, "results") or self.results is None:
            raise InvalidOperation(
                "The result attribute cannot be None for this method call."
            )
        return func(self, *args, **kwargs)

    return _decorator


# TODO: figure mypy complains on this line
class BasePaginator(BaseModel, MutableSequence):  # type: ignore
    """Thin wrapper around `self.results` for a robinhood paginator."""

    @has_results
    def __getitem__(self, key: Any) -> Any:  # noqa: D105
        return self.results[key]

    @has_results
    def __setitem__(self, key: Any, value: Any) -> Any:  # noqa: D105
        self.results[key] = value

    @has_results
    def __delitem__(self, key: Any) -> None:  # noqa: D105
        del self.results[key]

    @has_results
    def __len__(self) -> int:  # noqa: D105
        return len(self.results)

    @has_results
    def insert(self, index: int, element: Any) -> None:  # noqa: D102
        self.results.insert(index, element)


class BasePaginatorSchema(BaseSchema):
    """BasePaginatorSchema for the BasePaginator class.

    Note:
        Make sure to re-define the results attribute based on the subclass schema.

    """

    __model__ = BasePaginator

    next = fields.URL(allow_none=True)
    previous = fields.URL(allow_none=True)
    results = fields.List(fields.Nested(UnknownModel))


# TODO: Figure how to resolve the circular import with SessionManager (type ignore)
def base_paginator(
    seed_url: "URL", session_manager: Any, schema: Any
) -> Iterable[Any]:  # type: ignore  # noqa: F821
    """Create a paginator using the passed parameters.

    Args:
        seed_url: The url to get the first batch of results.
        session_manager: The session manager that will manage the get.
        schema: The Schema subclass used to build individual instances.

    Yields:
        Instances of the object passed in the schema field.

    """
    resource_endpoint = seed_url
    while True:
        paginator = session_manager.get(resource_endpoint, schema=schema)
        for instrument in paginator:
            yield instrument
        if paginator.next is not None:
            resource_endpoint = paginator.next
        else:
            break

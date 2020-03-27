"""Define API models."""

from collections.abc import Mapping
from datetime import datetime
from types import SimpleNamespace
from typing import Any

import pytz
from marshmallow import INCLUDE, Schema, fields, post_load, validate


CHALLENGE_TYPE_VAL = validate.OneOf(["email", "sms"])
MAX_REPR_LEN = 50


class BaseModel(SimpleNamespace):
    """TODO."""

    def __init__(self, **kwargs) -> None:
        kwargs = {
            k: UnknownModel(**v) if isinstance(v, Mapping) else v
            for k, v in kwargs.items()
        }

        self.__dict__.update(kwargs)

    def __repr__(self):
        repr_ = super().__repr__()
        if len(repr_) > MAX_REPR_LEN:
            return repr_[:MAX_REPR_LEN] + " ...)"
        else:
            return repr_

    def __len__(self):
        return len(self.__dict__)


class UnknownModel(BaseModel):
    """TODO."""

    pass


class BaseSchema(Schema):

    __model__: Any = UnknownModel

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


def lazy_model(class_name):
    class_ = type(class_name, (BaseModel,), {})
    globals()[class_name] = class_

    return class_


class Challenge(BaseModel):
    @property
    def can_retry(self):
        return self.remaining_attempts > 0 and (
            datetime.now(tz=pytz.utc) < self.expires_at
        )


class ChallengeSchema(BaseSchema):
    __model__ = Challenge

    id = fields.UUID()
    user = fields.UUID()
    type = fields.Str(validate=CHALLENGE_TYPE_VAL)
    alternate_type = fields.Str(validate=CHALLENGE_TYPE_VAL)
    status = fields.Str(validate=validate.OneOf(["issued", "validated", "failed"]))
    remaining_retries = fields.Int()
    remaining_attempts = fields.Int()
    expires_at = fields.AwareDateTime(default_timezone=pytz.UTC)


class OAuth(BaseModel):
    @property
    def is_challenge(self):
        return hasattr(self, "challenge")

    @property
    def is_mfa(self):
        return hasattr(self, "mfa_required")

    @property
    def is_valid(self):
        return hasattr(self, "access_token") and hasattr(self, "refresh_token")


class OAuthSchema(BaseSchema):
    __model__ = OAuth

    detail = fields.Str()
    challenge = fields.Nested(ChallengeSchema)
    mfa_required = fields.Boolean()

    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_in = fields.Int()

"""Oauth models."""

from datetime import datetime

import pytz
from marshmallow import fields, validate

from .base import BaseModel, BaseSchema


CHALLENGE_TYPE_VAL = validate.OneOf(["email", "sms"])


class Challenge(BaseModel):
    remaining_attempts = 0

    @property
    def can_retry(self) -> bool:
        """TODO."""
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
    expires_at = fields.AwareDateTime(default_timezone=pytz.UTC)  # type: ignore


class OAuth(BaseModel):
    @property
    def is_challenge(self) -> bool:
        return hasattr(self, "challenge")

    @property
    def is_mfa(self) -> bool:
        return hasattr(self, "mfa_required")

    @property
    def is_valid(self) -> bool:
        return hasattr(self, "access_token") and hasattr(self, "refresh_token")


class OAuthSchema(BaseSchema):
    __model__ = OAuth

    detail = fields.Str()
    challenge = fields.Nested(ChallengeSchema)
    mfa_required = fields.Boolean()

    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_in = fields.Int()

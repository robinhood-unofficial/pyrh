"""Oauth models."""

from datetime import datetime

import pytz
from marshmallow import fields, validate

from .base import BaseModel, BaseSchema

CHALLENGE_TYPE_VAL = validate.OneOf(["email", "sms"])


class Challenge(BaseModel):
    """The challenge response model."""

    remaining_attempts = 0
    """Default `remaining_attempts` attribute if it is not set on instance."""

    @property
    def can_retry(self) -> bool:
        """Determine if the challenge can be retried.

        Returns:
            True if remaining_attempts is greater than zero and challenge is not \
                expired, False otherwise.

        """
        return self.remaining_attempts > 0 and (
            datetime.now(tz=pytz.utc) < self.expires_at
        )


class ChallengeSchema(BaseSchema):
    """The challenge response schema."""

    __model__ = Challenge

    id = fields.UUID()
    user = fields.UUID()
    type = fields.Str(validate=CHALLENGE_TYPE_VAL)
    alternate_type = fields.Str(
        validate=CHALLENGE_TYPE_VAL, required=False, allow_none=True
    )
    status = fields.Str(validate=validate.OneOf(["issued", "validated", "failed"]))
    remaining_retries = fields.Int()
    remaining_attempts = fields.Int()
    expires_at = fields.AwareDateTime(default_timezone=pytz.UTC)  # type: ignore


class OAuth(BaseModel):
    """The OAuth response model."""

    @property
    def is_challenge(self) -> bool:
        """Determine whether the oauth response is a challenge.

        Returns:
            True response has the `challenge` key, False otherwise.

        """
        return hasattr(self, "challenge")

    @property
    def is_mfa(self) -> bool:
        """Determine whether the oauth response is a mfa challenge.

        Returns:
            True response has the `mfa_required` key, False otherwise.

        """
        return hasattr(self, "mfa_required")

    @property
    def is_valid(self) -> bool:
        """Determine whether the oauth response is a valid response.

        Returns:
            True if the response has both the `access_token` and `refresh_token` keys, \
                False otherwise.

        """
        return hasattr(self, "access_token") and hasattr(self, "refresh_token")


class OAuthSchema(BaseSchema):
    """The OAuth response schema."""

    __model__ = OAuth

    detail = fields.Str()
    challenge = fields.Nested(ChallengeSchema)
    mfa_required = fields.Boolean()

    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_in = fields.Int()

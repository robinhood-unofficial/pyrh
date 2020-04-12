"""Manage Robinhood Sessions."""

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union, cast, overload
from urllib.request import getproxies

import certifi
import pytz
import requests
from marshmallow import fields, post_load
from requests import Response
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict
from typing_extensions import Literal
from yarl import URL

from pyrh import endpoints
from pyrh.cache import CACHE_ROOT
from pyrh.common import JSON
from pyrh.exceptions import AuthenticationError

from .base import BaseModel, BaseSchema
from .oauth import CHALLENGE_TYPE_VAL, OAuth, OAuthSchema


CLIENT_ID: str = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"
"""Robinhood client id."""

CACHE_LOGIN: Path = CACHE_ROOT.joinpath("login.json")
"""Path to login.json config file."""
CACHE_LOGIN.touch(exist_ok=True)

if TYPE_CHECKING:  # pragma: no cover
    CaseInsensitiveDictType = CaseInsensitiveDict[str]
else:
    CaseInsensitiveDictType = CaseInsensitiveDict

Proxies = Dict[str, str]
HEADERS: CaseInsensitiveDictType = CaseInsensitiveDict(
    {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "X-Robinhood-API-Version": "1.0.0",
        "Connection": "keep-alive",
        "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)",
    }
)
"""Headers used when performing requests with robinhood api."""

EXPIRATION_TIME: int = 10
"""Default expiration time for requests."""

# TODO: Watch this issue and remove the F811 ignores when it is fixed
# https://gitlab.com/pycqa/flake8/-/merge_requests/417 (we need at least pyflakes 2.2.0)


class SessionManager(BaseModel):
    """Mange connectivity with Robinhood API.

    Once logged into the session, this class will manage automatic oauth token update
    requests allowing for the automation systems to only require multi-factor
    authentication on initialization.

    Example:
        >>> sm = SessionManager(username="USERNAME", password="PASSWORD")
        >>> sm.login()  # xdoctest: +SKIP
        >>> sm.logout()  # xdoctest: +SKIP

    If you want to cache your session (you should) then you can use the following
    functions. This will allow you to re-cover from a script crash without having to
    manually re-enter multi-factor authentication codes.

    Example:
        >>> dump_session(sm)  # xdoctest: +SKIP
        >>> load_session(sm)  # xdoctest: +SKIP

    Args:
        username: The username to login to Robinhood.
        password: The password to login to Robinhood.
        challenge_type: Either sms or email. (only if not using mfa)
        headers: Any optional header dict modifications for the session.
        proxies: Any optional proxy dict modification for the session.
        **kwargs: Any other passed parameters as converted to instance attributes.

    Attributes:
        session: A requests session instance.
        expires_at: The time the oauth token will expire at, default is
            1970-01-01 00:00:00.
        certs: The path to the desired certs to check against.
        device_token: A random guid representing the current device.
        access_token: An oauth2 token to connect to the Robinhood API.
        refresh_token: An oauth2 refresh token to refresh the access_token when
            required.
        username: The username to login to Robinhood.
        password: The password to login to Robinhood.
        challenge_type: Either sms or email. (only if not using mfa)
        headers: Any optional header dict modifications for the session.
        proxies: Any optional proxy dict modification for the session.

    """

    def __init__(
        self,
        username: str,
        password: str,
        challenge_type: Optional[str] = "email",
        headers: Optional[CaseInsensitiveDictType] = None,
        proxies: Optional[Proxies] = None,
        **kwargs: Any,
    ) -> None:
        self.session: requests.Session = requests.session()
        self.session.headers = HEADERS if headers is None else headers
        self.session.proxies = getproxies() if proxies is None else proxies
        self.session.verify = certifi.where()
        self.expires_at = datetime.strptime("1970", "%Y").replace(
            tzinfo=pytz.UTC
        )  # some time in the past

        self.username: str = username
        self.password: str = password
        if challenge_type not in ["email", "sms"]:
            raise ValueError("challenge_type must be email or sms")
        self.challenge_type: str = challenge_type

        self._gen_device_token: str = str(uuid.uuid4())
        self.oauth: OAuth = OAuth()

        super().__init__(**kwargs)

    @property
    def token_expired(self) -> bool:
        """Check if the issued auth token has expired.

        Returns:
            True if expired otherwise False
        """
        return datetime.now(tz=pytz.UTC) > self.expires_at

    @property
    def login_set(self) -> bool:
        """Check if login info is properly configured.

        Returns:
            Whether or not username and password are set.
        """
        return self.password is not None and self.username is not None

    @property
    def authenticated(self) -> bool:
        """Check if the session is authenticated.

        Returns:
            Whether or not the session is logged in.
        """
        return "Authorization" in self.session.headers and not self.token_expired

    def login(self, force_refresh: bool = False) -> None:
        """Login to the session.

        This method logs the user in if they are not already and otherwise refreshes
        the oauth token if it is expired.

        Args:
            force_refresh: If already logged in, whether or not to force a oauth token
                refresh.

        """
        if "Authorization" not in self.session.headers:
            self._login_oauth2()
        elif self.oauth.is_valid and (self.token_expired or force_refresh):
            self._refresh_oauth2()

    # The following type hints helps mypy determine what the output type to assign based
    # on the `return_response` parameter. The same "stub" method approach is used for
    # the post method as well.
    # https://github.com/python/mypy/issues/8634#issuecomment-609411104
    @overload
    def get(
        self,
        url: Union[str, URL],
        params: Optional[Dict[str, Any]] = None,
        *,
        headers: Optional[CaseInsensitiveDictType] = None,
        raise_errors: bool = True,
        return_response: Literal[True],
        auto_login: bool = True,
    ) -> Response:  # noqa: D102  # pragma: no cover
        ...

    @overload  # noqa: F811
    def get(
        self,
        url: Union[str, URL],
        params: Optional[Dict[str, Any]] = None,
        *,
        headers: Optional[CaseInsensitiveDictType] = None,
        raise_errors: bool = True,
        return_response: Literal[False] = ...,
        auto_login: bool = True,
    ) -> JSON:  # noqa: D102  # pragma: no cover
        ...

    def get(  # noqa: F811
        self,
        url: Union[str, URL],
        params: Optional[Dict[str, Any]] = None,
        *,
        headers: Optional[CaseInsensitiveDictType] = None,
        raise_errors: bool = True,
        return_response: bool = False,
        auto_login: bool = True,
    ) -> Union[Response, JSON]:
        """Run a wrapped session HTTP GET request.

        Note:
            This method automatically prompts the user to log in if not already logged
            in.

        Args:
            url: The url to get from.
            params: query string parameters
            headers: A dict adding to and overriding the session headers.
            raise_errors: Whether or not raise errors on GET request result.
            return_response: Whether or not return a `requests.Response` object or the
                JSON response from the request.
            auto_login: Whether or not to automatically login on restricted endpoint
                errors.

        Returns:
            The POST response

        """
        params = {} if params is None else params
        res = self.session.get(
            str(url), params=params, headers={} if headers is None else headers
        )
        if res.status_code == 401 and auto_login:
            self.login(force_refresh=True)
            res = self.session.get(
                str(url), params=params, headers={} if headers is None else headers
            )
        if raise_errors:
            res.raise_for_status()

        return res if return_response else res.json()

    @overload
    def post(
        self,
        url: Union[str, URL],
        data: Optional[JSON] = None,
        *,
        headers: Optional[CaseInsensitiveDictType] = None,
        raise_errors: bool = True,
        return_response: Literal[True],
        auto_login: bool = True,
    ) -> Response:  # noqa: D102  # pragma: no cover
        ...

    @overload  # noqa: F811
    def post(
        self,
        url: Union[str, URL],
        data: Optional[JSON] = None,
        *,
        headers: Optional[CaseInsensitiveDictType] = None,
        raise_errors: bool = True,
        return_response: Literal[False] = ...,
        auto_login: bool = True,
    ) -> JSON:  # noqa: D102  # pragma: no cover
        ...

    def post(  # noqa: F811
        self,
        url: Union[str, URL],
        data: Optional[JSON] = None,
        *,
        headers: Optional[CaseInsensitiveDictType] = None,
        raise_errors: bool = True,
        return_response: bool = False,
        auto_login: bool = True,
    ) -> Union[JSON, Response]:
        """Run a wrapped session HTTP POST request.

        Note:
            This method automatically prompts the user to log in if not already logged
            in.

        Args:
            url: The url to post to.
            data: The payload to POST to the endpoint.
            headers: A dict adding to and overriding the session headers.
            return_response: Whether or not return a `requests.Response` object or the
                JSON response from the request.
            raise_errors: Whether or not raise errors on POST request.
            auto_login: Whether or not to automatically login on restricted endpoint
                errors.

        Returns:
            The response or an empty dict if an empty response is returned.

        """
        res = self.session.post(
            str(url), data=data, timeout=15, headers={} if headers is None else headers,
        )
        if (res.status_code == 401) and auto_login:
            self.login(force_refresh=True)
            res = self.session.post(
                str(url),
                data=data,
                timeout=15,
                headers={} if headers is None else headers,
            )
        if raise_errors:
            res.raise_for_status()

        return res if return_response else res.json()

    def _configure_manager(self, oauth: OAuth) -> None:
        """Process an authentication response dictionary.

        This method updates the internal state of the session based on a login or
        token refresh request.

        Args:
            oauth: An oauth response model from a login request.

        """
        self.oauth = oauth
        self.expires_at = datetime.now(tz=pytz.UTC) + timedelta(
            seconds=self.oauth.expires_in
        )
        self.session.headers.update(
            {"Authorization": f"Bearer {self.oauth.access_token}"}
        )

    def _challenge_oauth2(self, oauth: OAuth, oauth_payload: JSON) -> OAuth:
        """Process the ouath challenge flow.

        Args:
            oauth: An oauth response model from a login request.
            oauth_payload: The payload to use once the challenge has been processed.

        Returns:
            An OAuth response model from the login request.

        Raises:
            AuthenticationError: If there is an error in the initial challenge response.

        .. # noqa: DAR202
        .. https://github.com/terrencepreilly/darglint/issues/81

        """
        # login challenge
        challenge_url = endpoints.CHALLENGE(oauth.challenge.id)
        print(
            f"Input challenge code from {oauth.challenge.type.capitalize()} "
            f"({oauth.challenge.remaining_attempts}/"
            f"{oauth.challenge.remaining_retries}):"
        )
        challenge_code = input()
        challenge_payload = {"response": str(challenge_code)}
        challenge_header = CaseInsensitiveDict(
            {"X-ROBINHOOD-CHALLENGE-RESPONSE-ID": str(oauth.challenge.id)}
        )
        res = self.post(
            challenge_url,
            data=challenge_payload,
            raise_errors=False,
            headers=challenge_header,
            auto_login=False,
            return_response=True,
        )
        oauth_inner = OAuthSchema().load(res.json())
        if res.status_code == requests.codes.ok:
            try:
                res2 = self.post(
                    endpoints.OAUTH,
                    data=oauth_payload,
                    headers=challenge_header,
                    auto_login=False,
                )
            except HTTPError:
                raise AuthenticationError("Error in finalizing auth token")
            else:
                oauth = OAuthSchema().load(res2)
                return oauth
        elif oauth_inner.is_challenge and oauth_inner.challenge.can_retry:
            print("Invalid code entered")
            return self._challenge_oauth2(oauth, oauth_payload)
        else:
            raise AuthenticationError("Exceeded available attempts or code expired")

    def _mfa_oauth2(self, oauth_payload: JSON, attempts: int = 3) -> OAuth:
        """Mfa auth flow.

         For people with 2fa.

        Args:
            oauth_payload: JSON payload to send on mfa approval.
            attempts: The number of attempts to allow for mfa approval.

        Returns:
            An OAuth response model object.

        Raises:
            AuthenticationError: If the mfa code is incorrect more than specified \
                number of attempts.

        """
        print(f"Input mfa code:")
        mfa_code = input()
        oauth_payload["mfa_code"] = mfa_code
        res = self.post(
            endpoints.OAUTH,
            data=oauth_payload,
            raise_errors=False,
            auto_login=False,
            return_response=True,
        )
        attempts -= 1
        if (res.status_code != requests.codes.ok) and (attempts > 0):
            print("Invalid mfa code")
            return self._mfa_oauth2(oauth_payload, attempts)
        elif res.status_code == requests.codes.ok:
            # TODO: Write mypy issue on why this needs to be casted?
            return cast(OAuth, OAuthSchema().load(res.json()))
        else:
            raise AuthenticationError("Too many incorrect mfa attempts")

    def _login_oauth2(self) -> None:
        """Create a new oauth2 token.

        Raises:
            AuthenticationError: If the login credentials are not set, if a challenge
                wasn't accepted, or if an mfa code is not accepted.

        """
        self.session.headers.pop("Authorization", None)

        oauth_payload = {
            "password": self.password,
            "username": self.username,
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "expires_in": EXPIRATION_TIME,
            "scope": "internal",
            "device_token": self._gen_device_token,
            "challenge_type": self.challenge_type,
        }

        res = self.post(
            endpoints.OAUTH,
            data=oauth_payload,
            raise_errors=False,
            auto_login=False,
            return_response=True,
        )

        oauth = OAuthSchema().load(res.json())

        if oauth.is_challenge:
            oauth = self._challenge_oauth2(oauth, oauth_payload)
        elif oauth.is_mfa:
            oauth = self._mfa_oauth2(oauth_payload)

        if not oauth.is_valid:
            msg = f"{oauth.error}" if hasattr(oauth, "error") else "Unknown login error"
            raise AuthenticationError(msg)
        else:
            self._configure_manager(oauth)

    def _refresh_oauth2(self) -> None:
        """Refresh an oauth2 token.

        Raises:
            AuthenticationError: If refresh_token is missing or if there is an error
                when trying to refresh a token.

        """
        if not self.oauth.is_valid:
            raise AuthenticationError("Cannot refresh login with unset refresh token")
        relogin_payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.oauth.refresh_token,
            "scope": "internal",
            "client_id": CLIENT_ID,
            "expires_in": EXPIRATION_TIME,
        }
        self.session.headers.pop("Authorization", None)
        try:
            res = self.post(endpoints.OAUTH, data=relogin_payload, auto_login=False)
        except HTTPError:
            raise AuthenticationError("Failed to refresh token")

        oauth = OAuthSchema().load(res)
        self._configure_manager(oauth)

    def logout(self) -> None:
        """Logout from the session.

        Raises:
            AuthenticationError: If there is an error when logging out.

        """
        logout_payload = {"client_id": CLIENT_ID, "token": self.oauth.refresh_token}
        try:
            self.post(endpoints.OAUTH_REVOKE, data=logout_payload, auto_login=False)
            self.oauth = OAuth()
            self.session.headers.pop("Authorization", None)
        except HTTPError:
            raise AuthenticationError("Could not log out")

    def __repr__(self) -> str:
        """Return the object as a string.

        Returns:
            The string representation of the object.

        """
        return f"SessionManager<{self.username}>"


class SessionManagerSchema(BaseSchema):
    """Schema class for the SessionManager model."""

    __model__ = SessionManager

    username = fields.Email()  # type: ignore # Call untyped "Email" in typed context
    password = fields.Str()
    challenge_type = fields.Str(validate=CHALLENGE_TYPE_VAL)
    oauth = fields.Nested(OAuthSchema)
    expires_at = fields.AwareDateTime()
    device_token = fields.Str()
    headers = fields.Dict()
    proxies = fields.Dict()

    @post_load
    def make_object(self, data: JSON, **kwargs: Any) -> SessionManager:
        """Override default method to configure SessionManager object on load.

        Args:
            data: The JSON dictionary to process
            **kwargs: Not used but matches signature of `BaseSchema.make_object`

        Returns:
            A configured instance of SessionManager.
        """
        oauth = data.pop("oauth", None)
        expires_at = data.pop("expires_at", None)
        session_manager = self.__model__(**data)

        if oauth is not None and oauth.is_valid:
            session_manager.oauth = oauth
            session_manager.session.headers.update(
                {"Authorization": f"Bearer {session_manager.oauth.access_token}"}
            )
        if expires_at:
            session_manager.expires_at = expires_at

        return session_manager


def dump_session(
    session_manager: SessionManager, path: Optional[Union[Path, str]] = None
) -> None:
    """Save the current session parameters to a json file.

    Note:
        This function defaults to caching this information to
        ~/.robinhood/login.json

    Args:
        session_manager: A SessionManager instance.
        path: The location to save the file and its name.

    """
    path = CACHE_LOGIN if path is None else path
    json_str = SessionManagerSchema().dumps(session_manager, indent=4)

    with open(path, "w+") as file:
        file.write(json_str)


def load_session(path: Optional[Union[Path, str]] = None) -> SessionManager:
    """Load cached session parameters from a json file.

    Note:
        This function defaults to caching this information to
        ~/.robinhood/login.json

    Args:
        path: The location and file name to load from.

    Returns:
        A configured instance of SessionManager.

    """
    path = path or CACHE_LOGIN
    with open(path) as file:
        return cast(SessionManager, SessionManagerSchema().loads(file.read()))

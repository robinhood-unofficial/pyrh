"""Manage Robinhood Sessions"""

import json
import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from urllib.request import getproxies

import requests
from requests.structures import CaseInsensitiveDict

from pyrh.cache import CACHE_ROOT
from pyrh.exceptions import AuthenticationError


CERTS_PATH: Path = Path(__file__).parent.joinpath("./ssl/certs.pem")
"""Path to ssl files used when running post requests"""

CLIENT_ID: str = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"
"""Robinhood client id"""

CACHE_LOGIN: Path = CACHE_ROOT.joinpath("login.json")
"""Path to login.json config file"""
CACHE_LOGIN.touch(exist_ok=True)

# TODO: put urls in an API module
OAUTH_TOKEN_URL: str = "https://api.robinhood.com/oauth2/token/"
"""Oauth token generation endpoint"""

OAUTH_REVOKE_URL: str = "https://api.robinhood.com/oauth2/revoke_token/"
"""Oauth revocation endpoint."""

HEADERS: CaseInsensitiveDict = CaseInsensitiveDict(
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

EXPIRATION_TIME: int = 86400
"""Default expiration time for requests."""


class SessionManager(object):
    """Mange connectivity with Robinhood API.

    >> sm = SessionManager()
    >> sm.login(username="USERNAME", password="PASSWORD")  # xdoctest: +SKIP
    >> sm.logout()  # xdoctest: +SKIP

    Args:
        username: The username to login to Robinhood.
        password: The password to login to Robinhood.
        challenge_type: Either sms or email. (only if not using mfa)
        headers: Any optional header dict modifications for the session.
        proxies: Any optional proxy dict modification for the session.

    Attributes:
        session: A requests session instance.
        expires_at: The time the oauth token will expire at, default is \
            1970-01-01 00:00:00.
        certs: The path to the desired certs to check against.
        device_token: A random guid representing the current device.
        access_token: An oauth2 token to connect to the Robinhood API.
        refresh_token: An oauth2 refresh token to refresh the access_token when \
            required.
        username: The username to login to Robinhood.
        password: The password to login to Robinhood.
        challenge_type: Either sms or email. (only if not using mfa)
        headers: Any optional header dict modifications for the session.
        proxies: Any optional proxy dict modification for the session.

    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        challenge_type: Optional[str] = "email",
        headers: Optional[CaseInsensitiveDict] = None,
        proxies: Optional[Dict] = None,
    ) -> None:
        self.session: requests.Session = requests.session()
        self.session.headers = HEADERS if headers is None else headers
        self.session.proxies = getproxies() if proxies is None else proxies
        self.expires_at = datetime.strptime("1970", "%Y")  # some time in the past
        self.certs: Path = CERTS_PATH

        self.username: Optional[str] = username
        self.password: Optional[str] = password
        if challenge_type not in ["email", "sms"]:
            raise ValueError("challenge_type must be email or sms")
        self.challenge_type: str = challenge_type
        self.device_token: str = str(uuid.uuid4())

        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def to_json(self, path=None):
        path = path or CACHE_LOGIN
        data = deepcopy(self.__dict__)
        data.pop("session")
        data.pop("certs")
        data["expires_at"] = self.expires_at.strftime("%Y-%m-%d %H:%M:%S")

        with open(path, "w+") as file:
            file.write(json.dumps(data, indent=4, default=str))

    def from_json(self, path=None):
        path = path or CACHE_LOGIN
        with open(path) as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                return False

        for k, v in data.items():
            if k == "expires_at":
                v = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
            setattr(self, k, v)

        if self.access_token is not None:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.access_token}"}
            )

        return self

    @property
    def login_set(self):
        return self.password is not None and self.username is not None

    @property
    def authenticated(self):
        return (
            "Authorization" in self.session.headers and datetime.now() < self.expires_at
        )

    def login(self, force_refresh=False):
        """Login with session"""
        if "Authorization" not in self.session.headers:
            self.login_oauth2()
        elif self.refresh_token is not None and (
            self.expires_at < datetime.now() or force_refresh
        ):
            self.refresh_oauth2()

    def get(self, url, headers=None, raise_errors=True):
        """
        Execute HTTP GET
        """
        res = self.session.get(url, headers={} if headers is None else headers)
        if res.status_code == 401:
            self.login(force_refresh=True)
            res = self.session.get(url, headers={} if headers is None else headers)
        if raise_errors:
            res.raise_for_status()
        return res.json()

    def post(self, url, data=None, headers=None, raise_errors=True, auto_login=True):
        """
        Execute HTTP POST
        """
        res = self.session.post(
            url,
            data=data,
            timeout=15,
            verify=self.certs,
            headers={} if headers is None else headers,
        )
        if (res.status_code == 401) and auto_login:
            self.login(force_refresh=True)
            res = self.session.post(
                url,
                data=data,
                timeout=15,
                verify=self.certs,
                headers={} if headers is None else headers,
            )
        if raise_errors:
            res.raise_for_status()
        if res.headers.get("Content-Length", None) == "0":
            return None
        else:
            return res.json()

    def _process_auth_body(self, res):
        try:
            self.access_token = res["access_token"]
            self.refresh_token = res["refresh_token"]
            self.expires_at = datetime.now() + timedelta(seconds=EXPIRATION_TIME)
            self.session.headers.update(
                {"Authorization": f"Bearer {self.access_token}"}
            )
        except KeyError:
            raise AuthenticationError(
                "Authorization result body missing required responses."
            )

    def login_oauth2(self):
        """Login using username and password"""

        if not self.login_set and not self.from_json():
            raise AuthenticationError(
                "Username and password must be passed to constructor or must be loaded "
                "from json"
            )
        self.session.headers.pop("Authorization", None)

        oauth_payload = {
            "password": self.password,
            "username": self.username,
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "expires_in": EXPIRATION_TIME,
            "scope": "internal",
            "device_token": self.device_token,
            "challenge_type": self.challenge_type,
        }

        res = self.post(
            OAUTH_TOKEN_URL, data=oauth_payload, raise_errors=False, auto_login=False
        )

        if res is None or "error" in res:
            raise AuthenticationError("Unknown login error")
        elif "detail" in res and any(k in res["detail"] for k in ["Invalid", "Unable"]):
            raise AuthenticationError(f"{res['detail']}")
        elif "challenge" in res:
            challenge_id = res["challenge"]["id"]
            # TODO: use api module
            challenge_url = (
                f"https://api.robinhood.com/challenge/{challenge_id}/respond/"
            )
            print(f"Input challenge code from {self.challenge_type.capitalize()}:")
            challenge_code = input()
            challenge_payload = {"response": str(challenge_code)}
            challenge_header = {"X-ROBINHOOD-CHALLENGE-RESPONSE-ID": challenge_id}
            data_challenge = self.post(
                challenge_url,
                data=challenge_payload,
                raise_errors=False,
                headers=challenge_header,
                auto_login=False,
            )
            if data_challenge.get("status", "") != "validated":
                raise AuthenticationError("Challenge response was not accepted")
            res = self.post(
                OAUTH_TOKEN_URL,
                data=oauth_payload,
                headers=challenge_header,
                auto_login=False,
            )
        elif "mfa_required" in res:
            print(f"Input mfa code:")
            mfa_code = input()
            oauth_payload["mfa_code"] = mfa_code
            res = self.post(
                OAUTH_TOKEN_URL,
                data=oauth_payload,
                raise_errors=False,
                auto_login=False,
            )
            if "detail" in res and res["detail"] == "Please enter a valid code.":
                raise AuthenticationError("Mfa code was not accepted")

        self._process_auth_body(res)

    def refresh_oauth2(self):
        """(Re)login using the Oauth2 refresh token"""
        if self.refresh_token is None:
            raise AuthenticationError("Cannot refresh login with unset refresh token")
        relogin_payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": "internal",
            "client_id": CLIENT_ID,
            "expires_in": EXPIRATION_TIME,
        }
        self.session.headers.pop("Authorization", None)
        res = self.post(
            OAUTH_TOKEN_URL, data=relogin_payload, auto_login=False, raise_errors=False
        )
        if "error" in res:
            raise AuthenticationError("Failed to refresh token")
        self._process_auth_body(res)

    def logout(self):
        """
        Logout for given Oauth2 bearer token
        """
        logout_payload = {
            "client_id": CLIENT_ID,
            "token": self.refresh_token,
        }
        res = self.post(
            OAUTH_REVOKE_URL, data=logout_payload, raise_errors=False, auto_login=False
        )
        if res is None:
            self.access_token = None
            self.refresh_token = None
        else:
            raise AuthenticationError("Could not log out")

    def __repr__(self):
        return f"SessionManager<{self.username}>"

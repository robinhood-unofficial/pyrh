"""This module contains the caching logic for Robinhood login data."""

import ast
import base64
import pathlib
import pickle
import time
from datetime import datetime
from typing import ByteString, Dict, Union

from cryptography.fernet import Fernet

from pyrh.exceptions import InvalidCacheFile

from .oauth import OAuth, OAuthSchema

LOGIN_ROOT: pathlib.Path = pathlib.Path("~/.robinhood").expanduser()
"""The root directory where the login tokens are stored.

Creates the directory on import.
"""
LOGIN_ROOT.mkdir(parents=True, exist_ok=True)

LOGIN_FILE: pathlib.Path = LOGIN_ROOT.joinpath("login.pickle")
"""Path to login.pickle file.

Creates the file on import.
"""
LOGIN_FILE.touch(exist_ok=True)


def encrypt_token(payload: Dict[str, str], key: str) -> ByteString:
    """Encrypt the login data using Fernet algorithm.

    Args:
        payload: Payload to encrypt.
        key: Encryption key.

    Returns:
        ByteString:
        Returns the encrypted login data as a Bytes object.
    """
    key = base64.urlsafe_b64encode(key.encode())
    fernet = Fernet(key)
    encoded_payload = str(payload).encode()
    return fernet.encrypt(encoded_payload)


def decrypt_token(payload: ByteString, key: str) -> str:
    """Decrypt the login data using Fernet algorithm.

    Args:
        payload: Payload to encrypt.
        key: Encryption key.

    Returns:
        str:
        Returns the decrypted login data as a string.
    """
    key = base64.urlsafe_b64encode(key.encode())
    fernet = Fernet(key)
    return fernet.decrypt(payload).decode()


def load_existing_oauth(username: str, password: str) -> Union[OAuth, None]:
    """Get the path to the login file.

    Args:
        username: Username for the Robinhood account.
        password: Password for the Robinhood account.

    Returns:
        OAuth:
        Returns the OAuth schema as a response.
    """
    try:
        with LOGIN_FILE.open("rb") as file:
            encrypted = pickle.load(file)
        json_data = ast.literal_eval(
            decrypt_token(encrypted, str(username + password)[0:32])
        )
        assert isinstance(json_data, dict), "Cached data must be a dictionary."
        assert json_data.get("login"), "Cached data must contain 'login' key."
        assert json_data.get("expiry"), "Cached data must contain 'expiry' key."
        assert isinstance(json_data["expiry"], int), "'expiry' must be an integer."
        if json_data["expiry"] < int(time.time()):
            print("Cached login data has expired.")
            return None
        assert isinstance(json_data["login"], dict), "'login' must be a dictionary."
    except AssertionError as error:
        print(f"Invalid cached data: {error}")
        raise InvalidCacheFile("Cached login file is invalid or corrupted.")
    except (FileNotFoundError, EOFError):
        return None
    else:
        return OAuthSchema().load(json_data["login"])


def save_existing_oauth(data: OAuth, username: str, password: str) -> None:
    """Save the login data to the login file.

    Args:
        data: Data to be stored locally.
        username: Username for the Robinhood account.
        password: Password for the Robinhood account.
    """
    expiry = int(time.time()) + data.expires_in
    expiration_dt = datetime.fromtimestamp(expiry).isoformat()
    login_data = {
        "login": data.__dict__,
        "expiry": expiry,
        "expiration_dt": expiration_dt,
    }
    encrypted = encrypt_token(login_data, str(username + password)[0:32])
    with LOGIN_FILE.open("wb") as file:
        pickle.dump(encrypted, file)
        file.flush()
    print(f"Login data saved to {LOGIN_FILE} valid until {expiration_dt}.")

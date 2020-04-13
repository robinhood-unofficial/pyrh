"""Shared resources across pyrh."""

from typing import Any, Dict

from yarl import URL


JSON = Dict[str, Any]

API_BASE = URL("https://api.robinhood.com")
"""Base robinhood api endpoint."""

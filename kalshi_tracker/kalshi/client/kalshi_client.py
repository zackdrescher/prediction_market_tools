"""A client that allows utils to call authenticated Kalshi API endpoints."""

from __future__ import annotations

import base64
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from kalshi_tracker.dateutil import now_utc

from .http_error import HttpError

if TYPE_CHECKING:
    from requests.models import Response

THRESHOLD_IN_MILLISECONDS = 100


class KalshiClient:
    """A simple client that allows utils to call authenticated Kalshi API endpoints."""

    def __init__(
        self,
        host: str,
        key_id: str,
        private_key: rsa.RSAPrivateKey,
        user_id: str | None = None,
        rate_limit_threshold: int = THRESHOLD_IN_MILLISECONDS,
    ) -> None:
        """Initialize the client and logs in the specified user.

        Raises an HttpError if the user could not be authenticated.
        """

        self.host = host
        self.key_id = key_id
        self.private_key = private_key
        self.user_id = user_id
        self.last_api_call = now_utc()
        self.rate_limit_threshold = rate_limit_threshold

    def rate_limit(self) -> None:
        """Block the thread until the rate limit is satisfied.

        Built in rate-limiter. We STRONGLY encourage you to keep
        some sort of rate limiting, just in case there is a bug in your
        code. Feel free to adjust the threshold
        """
        # Adjust time between each api call

        now = now_utc()
        threshold_in_microseconds = 1000 * THRESHOLD_IN_MILLISECONDS
        threshold_in_seconds = THRESHOLD_IN_MILLISECONDS / 1000
        if now - self.last_api_call < timedelta(microseconds=threshold_in_microseconds):
            time.sleep(threshold_in_seconds)
        self.last_api_call = now_utc()

    def post(self, path: str, body: str | None = None) -> Response:
        """POST to an authenticated Kalshi HTTP endpoint.

        Returns the response body. Raises an HttpError on non-2XX results.
        """
        self.rate_limit()

        response = requests.post(
            self.host + path,
            data=body,
            headers=self.request_headers("POST", path),
        )
        self.raise_if_bad_response(response)
        return response.json()

    def get(self, path: str, params: dict[str, Any] | None = None) -> Response:
        """GET from an authenticated Kalshi HTTP endpoint.

        Returns the response body. Raises an HttpError on non-2XX results.
        """
        if params is None:
            params = {}
        self.rate_limit()

        response = requests.get(
            self.host + path,
            headers=self.request_headers("GET", path),
            params=params,
        )
        self.raise_if_bad_response(response)
        return response.json()

    def delete(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        body: str | None = None,
    ) -> Response:
        """DELETE from an authenticated Kalshi HTTP endpoint.

        Returns the response body. Raises an HttpError on non-2XX results.
        """
        if params is None:
            params = {}
        self.rate_limit()

        response = requests.delete(
            self.host + path,
            headers=self.request_headers("DELETE", path),
            params=params,
            data=body,
        )
        self.raise_if_bad_response(response)
        return response.json()

    def request_headers(self, method: str, path: str) -> dict[str, Any]:
        """Generate the headers for an authenticated request."""

        # Get the current time
        current_time = now_utc()

        # Convert the time to a timestamp (seconds since the epoch)
        timestamp = current_time.timestamp()

        # Convert the timestamp to milliseconds
        current_time_milliseconds = int(timestamp * 1000)
        timestampt_str = str(current_time_milliseconds)

        # remove query params
        path_parts = path.split("?")

        msg_string = timestampt_str + method + "/trade-api/v2" + path_parts[0]
        signature = self.sign_pss_text(msg_string)

        headers = {"Content-Type": "application/json"}

        headers["KALSHI-ACCESS-KEY"] = self.key_id
        headers["KALSHI-ACCESS-SIGNATURE"] = signature
        headers["KALSHI-ACCESS-TIMESTAMP"] = timestampt_str
        return headers

    def sign_pss_text(self, text: str) -> str:
        """Sign a message using RSA-PSS."""
        # Before signing, we need to hash our message.
        # The hash is what we actually sign.
        # Convert the text to bytes
        message = text.encode("utf-8")
        try:
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH,
                ),
                hashes.SHA256(),
            )
            return base64.b64encode(signature).decode("utf-8")
        except InvalidSignature as e:
            raise ValueError("RSA sign PSS failed") from e

    def raise_if_bad_response(self, response: requests.Response) -> None:
        """Raise an HttpError if the response is not 2XX."""
        if response.status_code not in range(200, 299):
            raise HttpError(response.reason, response.status_code)

    def query_generation(self, params: dict) -> str:
        """Generate a query string from a dictionary of parameters."""
        relevant_params = {k: v for k, v in params.items() if v is not None}
        if len(relevant_params):
            query = (
                "?"
                + "".join(
                    "&" + str(k) + "=" + str(v) for k, v in relevant_params.items()
                )[1:]
            )
        else:
            query = ""
        return query

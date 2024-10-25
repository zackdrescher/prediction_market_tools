"""A client that allows utils to call authenticated Kalshi API endpoints."""

from __future__ import annotations

import base64
import json
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from kalshi_tracker.dateutil import now_utc

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
        """Block the trhead until the rate limit is satisfied.

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
        self.last_api_call = now_utc

    def post(self, path: str, body: dict) -> Response:
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

    def delete(self, path: str, params: dict[str | Any] | None = None) -> Response:
        """Post from an authenticated Kalshi HTTP endpoint.

        Returns the response body. Raises an HttpError on non-2XX results.
        """
        if params is None:
            params = {}
        self.rate_limit()

        response = requests.delete(
            self.host + path,
            headers=self.request_headers("DELETE", path),
            params=params,
        )
        self.raise_if_bad_response(response)
        return response.json()

    def request_headers(self, method: str, path: str) -> dict[str | Any]:
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


class HttpError(Exception):
    """Represents an HTTP error with reason and status code."""

    def __init__(self, reason: str, status: int) -> None:
        """Initialize the error with a reason and status code."""
        super().__init__(reason)
        self.reason = reason
        self.status = status

    def __str__(self) -> str:
        """Return a string representation of the error."""
        return "HttpError(%d %s)" % (self.status, self.reason)


class ExchangeClient(KalshiClient):
    """A client that allows utils to call authenticated Kalshi Exchange API endpoints."""

    def __init__(
        self,
        exchange_api_base: str,
        key_id: str,
        private_key: rsa.RSAPrivateKey,
    ) -> None:
        """Initialize the client."""
        super().__init__(
            exchange_api_base,
            key_id,
            private_key,
        )
        self.key_id = key_id
        self.private_key = private_key
        self.exchange_url = "/exchange"
        self.markets_url = "/markets"
        self.events_url = "/events"
        self.series_url = "/series"
        self.portfolio_url = "/portfolio"

    def logout(
        self,
    ) -> Response:
        """Logout the user."""
        return self.post("/logout")

    def get_exchange_status(
        self,
    ) -> Response:
        """Get the status of the exchange."""
        return self.get(self.exchange_url + "/status")

    # market endpoints!

    def get_markets(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        event_ticker: str | None = None,
        series_ticker: str | None = None,
        max_close_ts: int | None = None,
        min_close_ts: int | None = None,
        status: str | None = None,
        tickers: str | None = None,
    ) -> Response:
        """Get a list of markets."""
        query_string = self.query_generation(params=dict(locals().items()))
        return self.get(self.markets_url + query_string)

    def get_market_url(self, ticker: str) -> Response:
        """Get the URL for a specific market."""
        return self.markets_url + "/" + ticker

    def get_market(self, ticker: str) -> Response:
        """Get a specific market."""
        market_url = self.get_market_url(ticker=ticker)
        return self.get(market_url)

    def get_event(self, event_ticker: str) -> Response:
        """Get a specific event."""
        return self.get(self.events_url + "/" + event_ticker)

    def get_series(self, series_ticker: str) -> Response:
        """Get a specific series."""
        return self.get(self.series_url + "/" + series_ticker)

    def get_market_history(
        self,
        ticker: str,
        limit: int | None = None,
        cursor: str | None = None,
        max_ts: int | None = None,
        min_ts: int | None = None,
    ) -> Response:
        """Get the history of a specific market."""
        relevant_params = {k: v for k, v in locals().items() if k != "ticker"}
        query_string = self.query_generation(params=relevant_params)
        market_url = self.get_market_url(ticker=ticker)
        return self.get(market_url + "/history" + query_string)

    def get_orderbook(
        self,
        ticker: str,
        depth: int | None = None,
    ) -> Response:
        """Get the orderbook of a specific market."""
        relevant_params = {k: v for k, v in locals().items() if k != "ticker"}
        query_string = self.query_generation(params=relevant_params)
        market_url = self.get_market_url(ticker=ticker)
        return self.get(market_url + "/orderbook" + query_string)

    def get_trades(
        self,
        ticker: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        max_ts: int | None = None,
        min_ts: int | None = None,
    ) -> Response:
        """Get the trades of a specific market."""
        query_string = self.query_generation(params=dict(locals().items()))
        if ticker is not None:
            if len(query_string):
                query_string += "&"
            else:
                query_string += "?"
            query_string += "ticker=" + str(ticker)

        trades_url = self.markets_url + "/trades"
        return self.get(trades_url + query_string)

    # portfolio endpoints!

    def get_balance(
        self,
    ) -> Response:
        """Get the balance of the user."""
        return self.get(self.portfolio_url + "/balance")

    def create_order(
        self,
        ticker: str,
        client_order_id: str,
        side: str,
        action: str,
        count: int,
        order_type: str,
        yes_price: int | None = None,
        no_price: int | None = None,
        expiration_ts: int | None = None,
        sell_position_floor: int | None = None,
        buy_max_cost: int | None = None,
    ) -> Response:
        """Create an order."""
        relevant_params = {
            k: v for k, v in locals().items() if k != "self" and v is not None
        }

        order_json = json.dumps(relevant_params)
        orders_url = self.portfolio_url + "/orders"
        return self.post(path=orders_url, body=order_json)

    def batch_create_orders(self, orders: list) -> Response:
        """Create a list of orders."""
        orders_json = json.dumps({"orders": orders})
        batched_orders_url = self.portfolio_url + "/orders/batched"
        return self.post(path=batched_orders_url, body=orders_json)

    def decrease_order(
        self,
        order_id: str,
        reduce_by: int,
    ) -> Response:
        """Decrease the size of a specific order."""
        order_url = self.portfolio_url + "/orders/" + order_id
        decrease_json = json.dumps({"reduce_by": reduce_by})
        return self.post(path=order_url + "/decrease", body=decrease_json)

    def cancel_order(self, order_id: str) -> Response:
        """Cancel a specific order."""
        order_url = self.portfolio_url + "/orders/" + order_id
        return self.delete(path=order_url + "/cancel")

    def batch_cancel_orders(self, order_ids: list) -> Response:
        """Cancel a list of orders."""
        order_ids_json = json.dumps({"ids": order_ids})
        batched_orders_url = self.portfolio_url + "/orders/batched"
        return self.delete(path=batched_orders_url, body=order_ids_json)

    def get_fills(
        self,
        ticker: str | None = None,
        order_id: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Response:
        """Get a list of fills for the user."""
        fills_url = self.portfolio_url + "/fills"
        query_string = self.query_generation(params=dict(locals().items()))
        return self.get(fills_url + query_string)

    def get_orders(
        self,
        ticker: str | None = None,
        event_ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Response:
        """Get a list of orders for the user."""
        orders_url = self.portfolio_url + "/orders"
        query_string = self.query_generation(params=dict(locals().items()))
        return self.get(orders_url + query_string)

    def get_order(self, order_id: str) -> Response:
        """Get a specific order."""
        orders_url = self.portfolio_url + "/orders"
        return self.get(orders_url + "/" + order_id)

    def get_positions(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        settlement_status: str | None = None,
        ticker: str | None = None,
        event_ticker: str | None = None,
    ) -> Response:
        """Get a list of positions for the user."""
        positions_url = self.portfolio_url + "/positions"
        query_string = self.query_generation(params=dict(locals().items()))
        return self.get(positions_url + query_string)

    def get_portfolio_settlements(
        self,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> Response:
        """Get a list of settlements for the user."""
        positions_url = self.portfolio_url + "/settlements"
        query_string = self.query_generation(params=dict(locals().items()))
        return self.get(positions_url + query_string)

"""A client that allows utils to call authenticated Kalshi Exchange API endpoints."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .kalshi_client import KalshiClient

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric import rsa
    from requests.models import Response


class ExchangeClient(KalshiClient):
    """A client that calls authenticated Kalshi Exchange API endpoints."""

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

    def logout(self) -> Response:
        """Logout the user."""
        return self.post("/logout")

    def get_exchange_status(self) -> Response:
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

    def get_market_url(self, ticker: str) -> str:
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

    def get_balance(self) -> Response:
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

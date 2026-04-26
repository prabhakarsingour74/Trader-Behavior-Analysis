# bot/binance_client.py

import time
import hmac
import hashlib
import urllib.parse
from decimal import Decimal, ROUND_DOWN
from typing import Dict, Any, Optional

import requests

from bot.logging_config import setup_logging

# Binance USD-M Futures Testnet base URL
BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = setup_logging()
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add timestamp, recvWindow and signature to params.
        Uses sorted keys + proper URL encoding to avoid subtle issues.
        """
        base_params = dict(params)  # copy to avoid mutating caller's dict
        base_params["timestamp"] = int(time.time() * 1000)
        base_params.setdefault("recvWindow", 5000)

        # Sort by key (recommended by Binance) and URL-encode
        ordered_items = dict(sorted(base_params.items()))
        query_string = urllib.parse.urlencode(ordered_items, doseq=True)

        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        ordered_items["signature"] = signature
        return ordered_items

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Low-level HTTP request wrapper for Binance Futures.
        """
        url = f"{BASE_URL}{endpoint}"
        params = params or {}
        signed_params = self._sign_request(params)

        self.logger.info(f"🌐 Request: {method} {endpoint} | Params: {signed_params}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=signed_params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            self.logger.info(f"✅ Response: {data}")
            return data
        except requests.exceptions.HTTPError as e:
            text = e.response.text if e.response is not None else str(e)
            self.logger.error(f"❌ Network/API Error: {text}")
            raise RuntimeError(f"API request failed: {text}") from e
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Network/API Error: {str(e)}")
            raise RuntimeError(f"API request failed: {str(e)}") from e

    # ---------- Utility helpers ----------

    @staticmethod
    def _format_decimal(value: float, decimals: int) -> str:
        """
        Format a float as a decimal string without scientific notation,
        rounding DOWN to the allowed precision.
        """
        q = Decimal(str(value)).quantize(
            Decimal("1." + "0" * decimals),
            rounding=ROUND_DOWN,
        )
        return format(q.normalize(), "f")

    # ---------- Public API methods ----------

    def get_server_time(self) -> Dict[str, Any]:
        """
        Simple public endpoint to verify connectivity.
        """
        url = f"{BASE_URL}/fapi/v1/time"
        self.logger.info("🌐 Request: GET /fapi/v1/time")
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self.logger.info(f"✅ Response: {data}")
        return data

    def get_account_info(self) -> Dict[str, Any]:
        """
        Signed endpoint to verify API key/secret and permissions.
        If this fails with -2015, your keys or permissions are wrong.
        """
        return self._request("GET", "/fapi/v2/account", {})

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = 0.0,
        quantity_decimals: int = 5,
        price_decimals: int = 2,
    ) -> Dict[str, Any]:
        """
        Place a MARKET or LIMIT order on Binance USD-M Futures Testnet.

        :param symbol: e.g. "BTCUSDT"
        :param side: "BUY" or "SELL"
        :param order_type: "MARKET" or "LIMIT"
        :param quantity: Order quantity in base asset
        :param price: Limit price (required if order_type == "LIMIT")
        :param quantity_decimals: Allowed quantity precision (default 5)
        :param price_decimals: Allowed price precision (default 2)
        """

        qty_str = self._format_decimal(quantity, quantity_decimals)

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": qty_str,
        }

        if order_type == "LIMIT":
            if price <= 0:
                raise ValueError("Price must be > 0 for LIMIT orders")
            price_str = self._format_decimal(price, price_decimals)
            params["price"] = price_str
            params["timeInForce"] = "GTC"

        self.logger.info(
            f"📤 Placing order: {side} {qty_str} {symbol} @ {order_type}"
            + (f" price={params.get('price')}" if "price" in params else "")
        )

        return self._request("POST", "/fapi/v1/order", params)

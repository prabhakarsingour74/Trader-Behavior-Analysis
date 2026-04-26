from trading_bot.bot.binance_client import BinanceFuturesClient
from bot.logging_config import setup_logging

class OrderManager:
    def __init__(self, client: BinanceFuturesClient):
        self.client = client
        self.logger = setup_logging()

    def execute(self, symbol: str, side: str, order_type: str, quantity: float, price: float = 0.0) -> dict:
        self.logger.info(f"📤 Placing order: {side} {quantity} {symbol} @ {order_type} {'(Price: ' + str(price) + ')' if price else '(Market)'}")

        try:
            response = self.client.place_order(symbol, side, order_type, quantity, price)
            self._print_order_details(response)
            return response
        except Exception as e:
            self.logger.error(f"❌ Order placement failed: {e}")
            print(f"❌ Order failed: {e}")
            raise

    def _print_order_details(self, response: dict):
        print("\n" + "="*40)
        print("✅ ORDER REQUEST SUMMARY")
        print(f"Symbol: {response.get('symbol')}")
        print(f"Side: {response.get('side')}")
        print(f"Type: {response.get('type')}")
        print(f"Quantity: {response.get('origQty')}")
        if response.get('type') == 'LIMIT':
            print(f"Limit Price: {response.get('price')}")

        print("\n📊 ORDER RESPONSE DETAILS")
        print(f"Order ID: {response.get('orderId')}")
        print(f"Status: {response.get('status')}")
        print(f"Executed Qty: {response.get('executedQty')}")
        print(f"Avg Price: {response.get('avgPrice') or 'N/A (not filled yet)'}")
        print(f"Commission: {response.get('commission')} {response.get('commissionAsset')}")
        print(f"✅ Success: Order placed successfully on Binance Futures Testnet.")
        print("="*40 + "\n")
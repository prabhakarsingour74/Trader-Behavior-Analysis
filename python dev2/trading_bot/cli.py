# cli.py

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.binance_client import BinanceFuturesClient
from bot.logging_config import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple Binance Futures Testnet trading CLI"
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        help="Order side",
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT"],
        help="Order type",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        type=float,
        help="Order quantity (base asset amount)",
    )
    parser.add_argument(
        "--price",
        required=False,
        type=float,
        help="Limit price (required if type=LIMIT)",
    )
    parser.add_argument(
        "--test-keys",
        action="store_true",
        help="Call /fapi/v2/account to verify keys & permissions instead of placing an order",
    )

    return parser.parse_args()


def main() -> None:
    load_dotenv()
    logger = setup_logging()
    logger.info("🚀 CLI started")

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("❌ BINANCE_API_KEY or BINANCE_API_SECRET not set in environment")
        sys.exit(1)

    client = BinanceFuturesClient(api_key, api_secret)

    args = parse_args()

    # Optional: test keys instead of placing order
    if args.test_keys:
        logger.info("🔑 Testing API key & permissions with /fapi/v2/account")
        try:
            info = client.get_account_info()
            print("Account info:", info)
        except Exception as e:
            print("❌ Key test failed:", e)
        return

    # Validate LIMIT order price
    if args.type == "LIMIT" and (args.price is None or args.price <= 0):
        logger.error("❌ LIMIT orders require a positive --price value")
        sys.exit(1)

    try:
        order = client.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price or 0.0,
        )
        print("✅ Order placed successfully:")
        print(order)
    except Exception as e:
        logger.error(f"💥 Execution failed: {e}")
        print(f"❌ Execution failed. Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

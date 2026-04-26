import argparse

def validate_symbol(value: str) -> str:
    symbol = value.upper().strip()
    if not symbol.endswith("USDT"):
        raise argparse.ArgumentTypeError("Symbol must end with 'USDT' (e.g., BTCUSDT)")
    return symbol

def validate_side(value: str) -> str:
    side = value.upper().strip()
    if side not in ("BUY", "SELL"):
        raise argparse.ArgumentTypeError("Side must be 'BUY' or 'SELL'")
    return side

def validate_order_type(value: str) -> str:
    otype = value.upper().strip()
    if otype not in ("MARKET", "LIMIT"):
        raise argparse.ArgumentTypeError("Order type must be 'MARKET' or 'LIMIT'")
    return otype

def validate_quantity(value: str) -> float:
    try:
        qty = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Quantity must be a valid number")
    if qty <= 0:
        raise argparse.ArgumentTypeError("Quantity must be greater than 0")
    return qty
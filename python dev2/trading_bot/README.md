# 🤖 Binance Futures Testnet Trading Bot

A lightweight, structured Python CLI to place `MARKET` and `LIMIT` orders on Binance Futures Testnet (USDT-M). Built with clean separation of concerns, strict input validation, and production-grade logging.

## 📋 Evaluation Checklist
- ✅ Places MARKET & LIMIT orders on testnet
- ✅ Supports BUY/SELL sides
- ✅ CLI input validation (symbol, side, type, quantity, price)
- ✅ Structured code (`client.py`, `orders.py`, `validators.py`, `cli.py`)
- ✅ Logs requests, responses, and errors to `logs/trading_bot.log`
- ✅ Handles invalid input, API errors, and network failures gracefully

## 🛠️ Setup

1. **Register Testnet Account**: https://testnet.binancefuture.com
2. **Generate API Keys**: API Management → Create Key → ✅ Enable Futures permissions
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
# config.py

BINANCE_API_KEY = "NgGWZfcUgyB6QVFOzCQVJmkOSa1cfusNi1w6emTZPapbrYf60xoL6olA4B70Eb3h"
BINANCE_API_SECRET = "oIUp076Xd5YVwXFo82E8DE2fOwIcrmFSvePHH1YHJI31NlGZqv5j5soL7MdlbZoU"
TELEGRAM_BOT_TOKEN = "7894745130:AAHlFYuDAuRlhStlVQ6UDsNlUMiYzar0Bvo"
TELEGRAM_CHAT_ID = "-1002574858930"

# Timeframes to use for analysis
TIMEFRAMES = ['15m', '1h', '4h', '1d']

# Minimum candles for each timeframe (to ensure 1 month+ data)
CANDLE_LIMITS = {
    '15m': 3000,
    '1h': 800,
    '4h': 200,
    '1d': 35
}

SCAN_INTERVAL = 120  # seconds between scans
MIN_CANDLES = 100    # minimum candles required for indicators
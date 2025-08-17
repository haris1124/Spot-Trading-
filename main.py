# main.py

import asyncio
from signal_generator import SignalGenerator

if __name__ == "__main__":
    bot = SignalGenerator()
    asyncio.run(bot.scan_market())
# portfolio.py

import logging

class Portfolio:
    def __init__(self, binance_client, config):
        self.client = binance_client
        self.config = config

    async def open_position(self, symbol, entry_price, stop_loss, take_profit):
        # Example: Buy at market price
        try:
            # Calculate amount to buy (for example, $10 per trade)
            usdt_amount = 10
            amount = usdt_amount / entry_price
            order = await self.client.create_order(
                symbol=symbol,
                type='market',
                side='buy',
                amount=round(amount, 6)
            )
            logging.info(f"Spot BUY order placed: {order}")
            # For spot, you must manually sell later or alert user
            # Place TP/SL as alerts or manual orders (Binance spot does not support OCO via ccxt)
        except Exception as e:
            logging.error(f"Error placing spot order: {e}")
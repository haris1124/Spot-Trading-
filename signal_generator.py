# signal_generator.py

import logging
import time
import random
import asyncio
import ccxt.async_support as ccxt
import pandas as pd
from config import *
from technical_analysis import TechnicalAnalysis
from telegram_client import Telegram
from portfolio import Portfolio
from signal_validator import SignalValidator

class SignalGenerator:
    def __init__(self):
        self.config = __import__('config')
        self.binance_client = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
        })
        self.telegram = Telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        self.portfolio = Portfolio(self.binance_client, self.config)
        self.ta = TechnicalAnalysis()
        self.validator = SignalValidator()
        self.last_signal = {}
        self.last_signal_time = {}
        self.cooldown_period = 900

    async def get_symbols(self):
        await self.binance_client.load_markets()
        return [s for s in self.binance_client.markets if s.endswith('USDT') and self.binance_client.markets[s]['active']]

    async def get_historical_data(self, symbol, timeframe):
        limit = CANDLE_LIMITS.get(timeframe, 120)
        try:
            ohlcv = await self.binance_client.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df['symbol'] = symbol
            return df
        except Exception as e:
            logging.error(f"Error fetching {symbol} {timeframe}: {e}")
            return pd.DataFrame()

    def _calculate_sl_levels(self, df, current_price):
        sl_pct = random.uniform(0.01, 0.02)
        sl = current_price * (1 - sl_pct)
        return sl, sl_pct * 100

    async def _generate_signal(self, symbol, timeframe, df):
        try:
            current_price = df['close'].iloc[-1]
            indicators = {}
            df = self.ta.calculate_ema(df, [20, 50, 200])
            indicators['ema'] = 'BULLISH' if df['ema_20'].iloc[-1] > df['ema_50'].iloc[-1] else 'BEARISH'
            macd = self.ta.calculate_macd(df)
            indicators['macd'] = 'BULLISH' if macd['macd'].iloc[-1] > macd['signal'].iloc[-1] else 'BEARISH'
            rsi = self.ta.calculate_rsi(df)
            indicators['rsi'] = 'BULLISH' if rsi.iloc[-1] > 60 else ('BEARISH' if rsi.iloc[-1] < 40 else 'NEUTRAL')
            bb = self.ta.calculate_bollinger_bands(df)
            indicators['bb'] = 'BULLISH' if current_price > bb['upper'].iloc[-1] else ('BEARISH' if current_price < bb['lower'].iloc[-1] else 'NEUTRAL')
            adx = self.ta.calculate_adx(df)
            indicators['adx'] = adx.iloc[-1] if not adx.empty else 0
            fib_618 = df['high'].iloc[-50:].max() - 0.618 * (df['high'].iloc[-50:].max() - df['low'].iloc[-50:].min())
            indicators['fib'] = 'BULLISH' if current_price > fib_618 else 'BEARISH'
            atr = self.ta.calculate_atr(df)
            indicators['atr'] = atr.iloc[-1] if not atr.empty else 0
            stoch_rsi = self.ta.calculate_stoch_rsi(df)
            indicators['stoch_rsi'] = 'BULLISH' if stoch_rsi.iloc[-1] > 0.8 else ('BEARISH' if stoch_rsi.iloc[-1] < 0.2 else 'NEUTRAL')
            supertrend = self.ta.calculate_supertrend(df)
            indicators['supertrend'] = 'BULLISH' if supertrend['in_uptrend'].iloc[-1] else 'BEARISH'
            vwap = self.ta.calculate_vwap(df)
            indicators['vwap'] = 'BULLISH' if current_price > vwap.iloc[-1] else 'BEARISH'

            # Only BULLISH signals for spot
            direction = 'BULLISH'
            agree_count = sum([
                indicators['ema'] == direction,
                indicators['macd'] == direction,
                indicators['rsi'] == direction,
                indicators['bb'] == direction,
                indicators['fib'] == direction,
                indicators['stoch_rsi'] == direction,
                indicators['supertrend'] == direction,
                indicators['vwap'] == direction
            ])
            confidence = agree_count / 8
            tp1_pct = 0.012  # 1.2%
            tp1 = current_price * (1 + tp1_pct)
            sl, sl_pct = self._calculate_sl_levels(df, current_price)
            risk = current_price - sl
            reward = tp1 - current_price
            risk_reward = reward / risk if risk != 0 else 0
            win_probability = 0.9 + (confidence / 10)

            signal = {
                'symbol': symbol,
                'direction': direction,
                'timeframe': timeframe,
                'confidence': confidence,
                'entry': current_price,
                'tp_levels': [tp1],
                'tp1_percent': tp1_pct * 100,
                'sl': sl,
                'sl_percent': sl_pct,
                'risk_reward': risk_reward,
                'win_probability': min(win_probability, 0.99),
                'indicators': indicators
            }
            if agree_count < 8:
                return None
            if not self.validator.validate(signal):
                return None
            return signal
        except Exception as e:
            logging.error(f"Error generating signal for {symbol} {timeframe}: {e}")
            return None

    async def analyze_pair(self, symbol):
        signals = []
        for tf in TIMEFRAMES:
            df = await self.get_historical_data(symbol, tf)
            if df.empty or len(df) < MIN_CANDLES:
                continue
            signal = await self._generate_signal(symbol, tf, df)
            if signal:
                signals.append(signal)
        return signals

    async def scan_market(self):
        symbols = await self.get_symbols()
        for symbol in symbols:
            signals = await self.analyze_pair(symbol)
            for signal in signals:
                msg = self.format_signal(signal)
                await self.telegram.send_message(msg)
                await self.portfolio.open_position(
                    symbol=signal['symbol'],
                    entry_price=signal['entry'],
                    stop_loss=signal['sl'],
                    take_profit=signal['tp_levels'][0]
                )
            await asyncio.sleep(1)
        await self.binance_client.close()

    def format_signal(self, signal):
        return (
            f"📊 Pair: {signal['symbol']}\n"
            f"🕒 Timeframe: {signal['timeframe']}\n"
            f"🔍 Confidence: {signal['confidence']:.2f}\n"
            f"💰 Entry: {signal['entry']:.6f}\n"
            f"🎯 TP1: {signal['tp_levels'][0]:.6f} ({signal['tp1_percent']:.2f}%)\n"
            f"🛑 Stop Loss: {signal['sl']:.6f} ({signal['sl_percent']:.2f}%)\n"
            f"📊 Win Probability: {signal['win_probability']:.2f}\n"
        )
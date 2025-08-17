# technical_analysis.py

import pandas as pd
import numpy as np

class TechnicalAnalysis:
    def calculate_ema(self, df, periods):
        for period in periods:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
        return df

    def calculate_macd(self, df):
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        return pd.DataFrame({'macd': macd, 'signal': signal})

    def calculate_rsi(self, df, period=14):
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_bollinger_bands(self, df, period=20):
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = sma + 2 * std
        lower = sma - 2 * std
        return pd.DataFrame({'upper': upper, 'lower': lower})

    def calculate_adx(self, df, period=14):
        high = df['high']
        low = df['low']
        close = df['close']
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift()))
        tr3 = pd.DataFrame(abs(low - close.shift()))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = abs(100 * (minus_dm.rolling(window=period).mean() / atr))
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(window=period).mean()
        return adx

    def calculate_atr(self, df, period=14):
        high = df['high']
        low = df['low']
        close = df['close']
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def calculate_stoch_rsi(self, df, period=14):
        rsi = self.calculate_rsi(df, period)
        min_rsi = rsi.rolling(window=period).min()
        max_rsi = rsi.rolling(window=period).max()
        stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
        return stoch_rsi

    def calculate_supertrend(self, df, period=10, multiplier=3):
        atr = self.calculate_atr(df, period)
        hl2 = (df['high'] + df['low']) / 2
        upperband = hl2 + (multiplier * atr)
        lowerband = hl2 - (multiplier * atr)
        in_uptrend = [True]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > upperband.iloc[i-1]:
                in_uptrend.append(True)
            elif df['close'].iloc[i] < lowerband.iloc[i-1]:
                in_uptrend.append(False)
            else:
                in_uptrend.append(in_uptrend[-1])
        return pd.DataFrame({'in_uptrend': in_uptrend})

    def calculate_vwap(self, df):
        cum_vol = df['volume'].cumsum()
        cum_vol_price = (df['close'] * df['volume']).cumsum()
        vwap = cum_vol_price / cum_vol
        return vwap
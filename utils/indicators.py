# -*- coding: utf-8 -*-
"""
ماژول محاسبه اندیکاتورهای تکنیکال
"""

import numpy as np
import pandas as pd

def calculate_ema(data, period=20):
    """محاسبه میانگین متحرک نمایی (EMA)"""
    return data['Close'].ewm(span=period, adjust=False).mean()

def calculate_sma(data, period=20):
    """محاسبه میانگین متحرک ساده (SMA)"""
    return data['Close'].rolling(window=period).mean()

def calculate_rsi(data, period=14):
    """
    محاسبه شاخص قدرت نسبی (RSI)
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        period (int): دوره زمانی RSI
        
    خروجی:
        Series: مقادیر RSI
    """
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # برای محاسبات بعد از دوره اولیه
    for i in range(period, len(delta)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period-1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period-1) + loss.iloc[i]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """
    محاسبه باندهای بولینگر
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        period (int): دوره زمانی میانگین متحرک
        std_dev (int): تعداد انحراف معیار
        
    خروجی:
        tuple: (middle_band, upper_band, lower_band)
    """
    middle_band = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return middle_band, upper_band, lower_band

def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    محاسبه واگرایی/همگرایی میانگین متحرک (MACD)
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        fast_period (int): دوره سریع
        slow_period (int): دوره آهسته
        signal_period (int): دوره سیگنال
        
    خروجی:
        tuple: (macd_line, signal_line, histogram)
    """
    fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()
    
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calculate_stochastic(data, k_period=14, d_period=3):
    """
    محاسبه اسیلاتور استوکاستیک
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        k_period (int): دوره %K
        d_period (int): دوره %D
        
    خروجی:
        tuple: (k_line, d_line)
    """
    lowest_low = data['Low'].rolling(window=k_period).min()
    highest_high = data['High'].rolling(window=k_period).max()
    
    k_line = 100 * ((data['Close'] - lowest_low) / (highest_high - lowest_low))
    d_line = k_line.rolling(window=d_period).mean()
    
    return k_line, d_line

def calculate_atr(data, period=14):
    """
    محاسبه میانگین دامنه حقیقی (ATR)
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        period (int): دوره زمانی
        
    خروجی:
        Series: مقادیر ATR
    """
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(window=period).mean()
    
    return atr

def calculate_ichimoku(data, tenkan_period=9, kijun_period=26, senkou_b_period=52, displacement=26):
    """
    محاسبه ابر ایچیموکو
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        tenkan_period (int): دوره خط تنکان
        kijun_period (int): دوره خط کیجون
        senkou_b_period (int): دوره خط سنکو B
        displacement (int): میزان جابجایی برای ابر
        
    خروجی:
        tuple: (tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span)
    """
    # محاسبه تنکان سن (خط تبدیل)
    tenkan_high = data['High'].rolling(window=tenkan_period).max()
    tenkan_low = data['Low'].rolling(window=tenkan_period).min()
    tenkan_sen = (tenkan_high + tenkan_low) / 2
    
    # محاسبه کیجون سن (خط پایه)
    kijun_high = data['High'].rolling(window=kijun_period).max()
    kijun_low = data['Low'].rolling(window=kijun_period).min()
    kijun_sen = (kijun_high + kijun_low) / 2
    
    # محاسبه سنکو اسپن A (خط اول ابر)
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(displacement)
    
    # محاسبه سنکو اسپن B (خط دوم ابر)
    senkou_high = data['High'].rolling(window=senkou_b_period).max()
    senkou_low = data['Low'].rolling(window=senkou_b_period).min()
    senkou_span_b = ((senkou_high + senkou_low) / 2).shift(displacement)
    
    # محاسبه چیکو اسپن (خط تأخیری)
    chikou_span = data['Close'].shift(-displacement)
    
    return tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span

def detect_divergence(data, price_col='Close', indicator_col='RSI', window=10):
    """
    تشخیص واگرایی بین قیمت و یک اندیکاتور
    
    پارامترها:
        data (DataFrame): داده‌های قیمت و اندیکاتور
        price_col (str): نام ستون قیمت
        indicator_col (str): نام ستون اندیکاتور
        window (int): اندازه پنجره برای بررسی واگرایی
        
    خروجی:
        DataFrame: سیگنال‌های واگرایی
    """
    data = data.copy()
    data['Price_Diff'] = data[price_col].diff(window)
    data['Indicator_Diff'] = data[indicator_col].diff(window)
    
    # تشخیص واگرایی مثبت (قیمت پایین‌تر، اندیکاتور بالاتر)
    bullish_divergence = (data['Price_Diff'] < 0) & (data['Indicator_Diff'] > 0)
    
    # تشخیص واگرایی منفی (قیمت بالاتر، اندیکاتور پایین‌تر)
    bearish_divergence = (data['Price_Diff'] > 0) & (data['Indicator_Diff'] < 0)
    
    data['Bullish_Divergence'] = bullish_divergence
    data['Bearish_Divergence'] = bearish_divergence
    
    return data[['Bullish_Divergence', 'Bearish_Divergence']]

def detect_support_resistance(data, window=10, threshold=0.01):
    """
    تشخیص سطوح حمایت و مقاومت
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        window (int): اندازه پنجره برای بررسی
        threshold (float): آستانه تشخیص
        
    خروجی:
        tuple: (levels, is_support, is_resistance)
    """
    data = data.copy()
    levels = []
    is_support = []
    is_resistance = []
    
    for i in range(window, len(data) - window):
        max_left = data['High'].iloc[i-window:i].max()
        max_right = data['High'].iloc[i+1:i+window+1].max()
        min_left = data['Low'].iloc[i-window:i].min()
        min_right = data['Low'].iloc[i+1:i+window+1].min()
        
        # تشخیص سطح حمایت
        if min_left > data['Low'].iloc[i] < min_right and abs(min_left - data['Low'].iloc[i]) / data['Low'].iloc[i] > threshold:
            levels.append(data['Low'].iloc[i])
            is_support.append(True)
            is_resistance.append(False)
        
        # تشخیص سطح مقاومت
        elif max_left < data['High'].iloc[i] > max_right and abs(max_left - data['High'].iloc[i]) / data['High'].iloc[i] > threshold:
            levels.append(data['High'].iloc[i])
            is_support.append(False)
            is_resistance.append(True)
    
    return levels, is_support, is_resistance

def detect_candlestick_patterns(data):
    """
    تشخیص الگوهای شمعی
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        
    خروجی:
        DataFrame: سیگنال‌های الگوهای شمعی
    """
    data = data.copy()
    
    # محاسبه دامنه بدنه و سایه‌ها
    data['Body'] = abs(data['Close'] - data['Open'])
    data['Upper_Shadow'] = data.apply(
        lambda x: x['High'] - x['Close'] if x['Close'] > x['Open'] else x['High'] - x['Open'],
        axis=1
    )
    data['Lower_Shadow'] = data.apply(
        lambda x: x['Open'] - x['Low'] if x['Close'] > x['Open'] else x['Close'] - x['Low'],
        axis=1
    )
    
    # میانگین اندازه بدنه برای تعیین الگوها
    avg_body = data['Body'].mean()
    
    # دوجی (بدنه کوچک)
    data['Doji'] = data['Body'] < 0.1 * avg_body
    
    # چکش (بدنه کوچک، سایه پایینی بلند)
    data['Hammer'] = (data['Body'] < 0.5 * avg_body) & (data['Lower_Shadow'] > 2 * data['Body']) & (data['Upper_Shadow'] < 0.5 * data['Body'])
    
    # ستاره شوتینگ (بدنه کوچک، سایه بالایی بلند)
    data['Shooting_Star'] = (data['Body'] < 0.5 * avg_body) & (data['Upper_Shadow'] > 2 * data['Body']) & (data['Lower_Shadow'] < 0.5 * data['Body'])
    
    # الگوی بلعیدن صعودی (Bullish Engulfing)
    data['Bullish_Engulfing'] = False
    for i in range(1, len(data)):
        if (data['Close'].iloc[i-1] < data['Open'].iloc[i-1]) and (data['Close'].iloc[i] > data['Open'].iloc[i]):
            if (data['Open'].iloc[i] < data['Close'].iloc[i-1]) and (data['Close'].iloc[i] > data['Open'].iloc[i-1]):
                data.loc[data.index[i], 'Bullish_Engulfing'] = True
    
    # الگوی بلعیدن نزولی (Bearish Engulfing)
    data['Bearish_Engulfing'] = False
    for i in range(1, len(data)):
        if (data['Close'].iloc[i-1] > data['Open'].iloc[i-1]) and (data['Close'].iloc[i] < data['Open'].iloc[i]):
            if (data['Open'].iloc[i] > data['Close'].iloc[i-1]) and (data['Close'].iloc[i] < data['Open'].iloc[i-1]):
                data.loc[data.index[i], 'Bearish_Engulfing'] = True
    
    # الگوی پین‌بار (Pinbar)
    data['Pinbar'] = (data['Upper_Shadow'] > 2 * data['Body']) | (data['Lower_Shadow'] > 2 * data['Body'])
    
    return data[['Doji', 'Hammer', 'Shooting_Star', 'Bullish_Engulfing', 'Bearish_Engulfing', 'Pinbar']]

def fibonacci_levels(start, end):
    """
    محاسبه سطوح فیبوناچی
    
    پارامترها:
        start (float): قیمت شروع
        end (float): قیمت پایان
        
    خروجی:
        dict: سطوح فیبوناچی
    """
    diff = abs(end - start)
    direction = 1 if end > start else -1
    
    levels = {
        0: start,
        0.236: start + direction * 0.236 * diff,
        0.382: start + direction * 0.382 * diff,
        0.5: start + direction * 0.5 * diff,
        0.618: start + direction * 0.618 * diff,
        0.786: start + direction * 0.786 * diff,
        1: end,
        1.272: start + direction * 1.272 * diff,
        1.618: start + direction * 1.618 * diff
    }
    
    return levels
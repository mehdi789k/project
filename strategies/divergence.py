# -*- coding: utf-8 -*-
"""
استراتژی واگرایی RSI
"""

import pandas as pd
import numpy as np
from utils.indicators import calculate_rsi, calculate_bollinger_bands, detect_divergence

class Divergence_Strategy:
    """
    استراتژی واگرایی RSI
    
    این استراتژی به دنبال شناسایی واگرایی بین قیمت و شاخص RSI است:
    - واگرایی مثبت: قیمت اوج‌های پایین‌تری می‌سازد اما RSI اوج‌های بالاتری می‌سازد
    - واگرایی منفی: قیمت اوج‌های بالاتری می‌سازد اما RSI اوج‌های پایین‌تری می‌سازد
    """
    
    def __init__(self, rsi_period=14, window=10, bb_period=20, bb_std=2):
        """
        مقداردهی اولیه
        
        پارامترها:
            rsi_period (int): دوره RSI
            window (int): اندازه پنجره برای بررسی واگرایی
            bb_period (int): دوره باندهای بولینگر
            bb_std (int): تعداد انحراف معیار باندهای بولینگر
        """
        self.rsi_period = rsi_period
        self.window = window
        self.bb_period = bb_period
        self.bb_std = bb_std
    
    def find_extrema(self, data, column, window=5):
        """
        شناسایی نقاط اکسترمم (اوج‌ها و حضیض‌ها)
        
        پارامترها:
            data (DataFrame): داده‌ها
            column (str): نام ستون برای بررسی
            window (int): اندازه پنجره برای شناسایی نقاط اکسترمم
            
        خروجی:
            tuple: (highs, lows)
        """
        highs = []
        lows = []
        
        for i in range(window, len(data) - window):
            # بررسی آیا نقطه i یک اوج است
            if all(data[column].iloc[i] > data[column].iloc[i-j] for j in range(1, window+1)) and \
               all(data[column].iloc[i] > data[column].iloc[i+j] for j in range(1, window+1)):
                highs.append((i, data[column].iloc[i]))
            
            # بررسی آیا نقطه i یک حضیض است
            if all(data[column].iloc[i] < data[column].iloc[i-j] for j in range(1, window+1)) and \
               all(data[column].iloc[i] < data[column].iloc[i+j] for j in range(1, window+1)):
                lows.append((i, data[column].iloc[i]))
        
        return highs, lows
    
    def run(self, data):
        """
        اجرای استراتژی روی داده‌ها
        
        پارامترها:
            data (DataFrame): داده‌های قیمت
            
        خروجی:
            DataFrame: سیگنال‌های خرید و فروش
        """
        # محاسبه شاخص‌ها
        data['RSI'] = calculate_rsi(data, self.rsi_period)
        mid_band, upper_band, lower_band = calculate_bollinger_bands(data, self.bb_period, self.bb_std)
        data['BB_Middle'] = mid_band
        data['BB_Upper'] = upper_band
        data['BB_Lower'] = lower_band
        
        # شناسایی اوج‌ها و حضیض‌های قیمت و RSI
        price_highs, price_lows = self.find_extrema(data, 'Close')
        rsi_highs, rsi_lows = self.find_extrema(data, 'RSI')
        
        signals = []
        
        # بررسی واگرایی مثبت (قیمت پایین‌تر، RSI بالاتر)
        for i in range(1, len(price_lows)):
            # آخرین دو حضیض قیمت
            price_idx1, price_low1 = price_lows[i-1]
            price_idx2, price_low2 = price_lows[i]
            
            # بررسی آیا حضیض دوم قیمت پایین‌تر است
            if price_low2 < price_low1:
                # پیدا کردن حضیض‌های RSI در محدوده زمانی مشابه
                rsi_indices = [idx for idx, _ in rsi_lows if price_idx1 - self.window <= idx <= price_idx1 + self.window]
                if not rsi_indices:
                    continue
                
                rsi_idx1 = min(rsi_indices, key=lambda x: abs(x - price_idx1))
                
                rsi_indices = [idx for idx, _ in rsi_lows if price_idx2 - self.window <= idx <= price_idx2 + self.window]
                if not rsi_indices:
                    continue
                
                rsi_idx2 = min(rsi_indices, key=lambda x: abs(x - price_idx2))
                
                # آیا حضیض دوم RSI بالاتر است؟
                if data['RSI'].iloc[rsi_idx2] > data['RSI'].iloc[rsi_idx1]:
                    # واگرایی مثبت
                    # تأیید با باندهای بولینگر (قیمت نزدیک باند پایین)
                    if data['Close'].iloc[price_idx2] < data['BB_Lower'].iloc[price_idx2] * 1.01:
                        signals.append({
                            'Date': data['Date'].iloc[price_idx2],
                            'Price': data['Close'].iloc[price_idx2],
                            'Signal': 1,  # 1 برای خرید
                            'RSI': data['RSI'].iloc[price_idx2],
                            'Divergence': 'Positive'
                        })
        
        # بررسی واگرایی منفی (قیمت بالاتر، RSI پایین‌تر)
        for i in range(1, len(price_highs)):
            # آخرین دو اوج قیمت
            price_idx1, price_high1 = price_highs[i-1]
            price_idx2, price_high2 = price_highs[i]
            
            # بررسی آیا اوج دوم قیمت بالاتر است
            if price_high2 > price_high1:
                # پیدا کردن اوج‌های RSI در محدوده زمانی مشابه
                rsi_indices = [idx for idx, _ in rsi_highs if price_idx1 - self.window <= idx <= price_idx1 + self.window]
                if not rsi_indices:
                    continue
                
                rsi_idx1 = min(rsi_indices, key=lambda x: abs(x - price_idx1))
                
                rsi_indices = [idx for idx, _ in rsi_highs if price_idx2 - self.window <= idx <= price_idx2 + self.window]
                if not rsi_indices:
                    continue
                
                rsi_idx2 = min(rsi_indices, key=lambda x: abs(x - price_idx2))
                
                # آیا اوج دوم RSI پایین‌تر است؟
                if data['RSI'].iloc[rsi_idx2] < data['RSI'].iloc[rsi_idx1]:
                    # واگرایی منفی
                    # تأیید با باندهای بولینگر (قیمت نزدیک باند بالا)
                    if data['Close'].iloc[price_idx2] > data['BB_Upper'].iloc[price_idx2] * 0.99:
                        signals.append({
                            'Date': data['Date'].iloc[price_idx2],
                            'Price': data['Close'].iloc[price_idx2],
                            'Signal': -1,  # -1 برای فروش
                            'RSI': data['RSI'].iloc[price_idx2],
                            'Divergence': 'Negative'
                        })
        
        return pd.DataFrame(signals)
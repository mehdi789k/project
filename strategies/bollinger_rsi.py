# -*- coding: utf-8 -*-
"""
استراتژی ترکیبی باندهای بولینگر و RSI
"""

import pandas as pd
import numpy as np
from utils.indicators import calculate_rsi, calculate_bollinger_bands

class Bollinger_RSI_Strategy:
    """
    استراتژی ترکیبی باندهای بولینگر و RSI
    
    این استراتژی بر اساس ترکیب باندهای بولینگر و RSI عمل می‌کند:
    - خرید: هنگامی که قیمت به باند پایین بولینگر نزدیک می‌شود و RSI زیر 30 است
    - فروش: هنگامی که قیمت به باند بالای بولینگر نزدیک می‌شود و RSI بالای 70 است
    """
    
    def __init__(self, bb_period=20, bb_std=2, rsi_period=14, rsi_buy=30, rsi_sell=70):
        """
        مقداردهی اولیه
        
        پارامترها:
            bb_period (int): دوره باندهای بولینگر
            bb_std (int): تعداد انحراف معیار
            rsi_period (int): دوره RSI
            rsi_buy (int): سطح RSI برای سیگنال خرید
            rsi_sell (int): سطح RSI برای سیگنال فروش
        """
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_buy = rsi_buy
        self.rsi_sell = rsi_sell
    
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
        
        # محاسبه فاصله از باندها (به صورت درصد)
        data['Price_to_Lower'] = (data['Close'] - data['BB_Lower']) / data['BB_Lower'] * 100
        data['Price_to_Upper'] = (data['BB_Upper'] - data['Close']) / data['Close'] * 100
        
        # شناسایی الگوهای شمعی
        data['Bullish_Candle'] = data['Close'] > data['Open']
        data['Bearish_Candle'] = data['Close'] < data['Open']
        
        # شناسایی سیگنال‌های خرید و فروش
        signals = []
        
        for i in range(1, len(data)):
            # شرط خرید: قیمت نزدیک باند پایین و RSI زیر 30 و شمع صعودی
            if (data['Price_to_Lower'].iloc[i] < 1.0) and (data['RSI'].iloc[i] < self.rsi_buy) and (data['Bullish_Candle'].iloc[i]):
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': 1,  # 1 برای خرید
                    'RSI': data['RSI'].iloc[i],
                    'BB_Lower': data['BB_Lower'].iloc[i],
                    'BB_Upper': data['BB_Upper'].iloc[i]
                })
            
            # شرط فروش: قیمت نزدیک باند بالا و RSI بالای 70 و شمع نزولی
            elif (data['Price_to_Upper'].iloc[i] < 1.0) and (data['RSI'].iloc[i] > self.rsi_sell) and (data['Bearish_Candle'].iloc[i]):
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': -1,  # -1 برای فروش
                    'RSI': data['RSI'].iloc[i],
                    'BB_Lower': data['BB_Lower'].iloc[i],
                    'BB_Upper': data['BB_Upper'].iloc[i]
                })
        
        return pd.DataFrame(signals)
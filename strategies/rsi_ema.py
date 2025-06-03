# -*- coding: utf-8 -*-
"""
استراتژی ترکیبی RSI و EMA
"""

import pandas as pd
import numpy as np
from utils.indicators import calculate_rsi, calculate_ema

class RSI_EMA_Strategy:
    """
    استراتژی ترکیبی RSI و EMA
    
    این استراتژی بر اساس ترکیب شاخص‌های RSI و EMA عمل می‌کند:
    - خرید: هنگامی که RSI از زیر 40 عبور کند و قیمت بالای EMA(50) باشد
    - فروش: هنگامی که RSI از بالای 70 عبور کند و قیمت زیر EMA(50) باشد
    """
    
    def __init__(self, rsi_period=14, ema_period=50, rsi_buy=40, rsi_sell=70):
        """
        مقداردهی اولیه
        
        پارامترها:
            rsi_period (int): دوره RSI
            ema_period (int): دوره EMA
            rsi_buy (int): سطح RSI برای سیگنال خرید
            rsi_sell (int): سطح RSI برای سیگنال فروش
        """
        self.rsi_period = rsi_period
        self.ema_period = ema_period
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
        data['EMA'] = calculate_ema(data, self.ema_period)
        
        # شناسایی سیگنال‌های خرید و فروش
        signals = []
        
        for i in range(1, len(data)):
            # شرط خرید: RSI از زیر 40 رد شده و قیمت بالای EMA
            if (data['RSI'].iloc[i-1] < self.rsi_buy and data['RSI'].iloc[i] >= self.rsi_buy) and data['Close'].iloc[i] > data['EMA'].iloc[i]:
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': 1,  # 1 برای خرید
                    'RSI': data['RSI'].iloc[i],
                    'EMA': data['EMA'].iloc[i]
                })
            
            # شرط فروش: RSI از بالای 70 رد شده و قیمت زیر EMA
            elif (data['RSI'].iloc[i-1] > self.rsi_sell and data['RSI'].iloc[i] <= self.rsi_sell) and data['Close'].iloc[i] < data['EMA'].iloc[i]:
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': -1,  # -1 برای فروش
                    'RSI': data['RSI'].iloc[i],
                    'EMA': data['EMA'].iloc[i]
                })
        
        return pd.DataFrame(signals)
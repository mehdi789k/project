# -*- coding: utf-8 -*-
"""
استراتژی کراس مووینگ اوریج با فیلتر RSI
"""

import pandas as pd
import numpy as np
from utils.indicators import calculate_ema, calculate_rsi

class MA_Crossover_Strategy:
    """
    استراتژی کراس مووینگ اوریج با فیلتر RSI
    
    این استراتژی بر اساس کراس میانگین‌های متحرک و تأیید با RSI عمل می‌کند:
    - خرید: هنگامی که EMA کوتاه‌مدت از بالای EMA بلندمدت عبور می‌کند و RSI بالای 50 است
    - فروش: هنگامی که EMA کوتاه‌مدت از پایین EMA بلندمدت عبور می‌کند و RSI زیر 50 است
    """
    
    def __init__(self, short_period=9, long_period=21, rsi_period=14):
        """
        مقداردهی اولیه
        
        پارامترها:
            short_period (int): دوره EMA کوتاه‌مدت
            long_period (int): دوره EMA بلندمدت
            rsi_period (int): دوره RSI
        """
        self.short_period = short_period
        self.long_period = long_period
        self.rsi_period = rsi_period
    
    def run(self, data):
        """
        اجرای استراتژی روی داده‌ها
        
        پارامترها:
            data (DataFrame): داده‌های قیمت
            
        خروجی:
            DataFrame: سیگنال‌های خرید و فروش
        """
        # محاسبه شاخص‌ها
        data['EMA_Short'] = calculate_ema(data, self.short_period)
        data['EMA_Long'] = calculate_ema(data, self.long_period)
        data['RSI'] = calculate_rsi(data, self.rsi_period)
        
        # شناسایی کراس‌ها
        data['Cross'] = 0
        
        for i in range(1, len(data)):
            # کراس صعودی (کوتاه‌مدت از پایین بلندمدت عبور می‌کند)
            if (data['EMA_Short'].iloc[i-1] <= data['EMA_Long'].iloc[i-1]) and (data['EMA_Short'].iloc[i] > data['EMA_Long'].iloc[i]):
                data.loc[data.index[i], 'Cross'] = 1
            
            # کراس نزولی (کوتاه‌مدت از بالای بلندمدت عبور می‌کند)
            elif (data['EMA_Short'].iloc[i-1] >= data['EMA_Long'].iloc[i-1]) and (data['EMA_Short'].iloc[i] < data['EMA_Long'].iloc[i]):
                data.loc[data.index[i], 'Cross'] = -1
        
        # شناسایی سیگنال‌های خرید و فروش
        signals = []
        
        for i in range(1, len(data)):
            # سیگنال خرید: کراس صعودی و RSI بالای 50
            if (data['Cross'].iloc[i] == 1) and (data['RSI'].iloc[i] > 50):
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': 1,  # 1 برای خرید
                    'RSI': data['RSI'].iloc[i],
                    'EMA_Short': data['EMA_Short'].iloc[i],
                    'EMA_Long': data['EMA_Long'].iloc[i]
                })
            
            # سیگنال فروش: کراس نزولی و RSI زیر 50
            elif (data['Cross'].iloc[i] == -1) and (data['RSI'].iloc[i] < 50):
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': -1,  # -1 برای فروش
                    'RSI': data['RSI'].iloc[i],
                    'EMA_Short': data['EMA_Short'].iloc[i],
                    'EMA_Long': data['EMA_Long'].iloc[i]
                })
        
        return pd.DataFrame(signals)
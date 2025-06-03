# -*- coding: utf-8 -*-
"""
استراتژی پولبک روند
"""

import pandas as pd
import numpy as np
from utils.indicators import calculate_ema, calculate_rsi

class Trend_Pullback_Strategy:
    """
    استراتژی پولبک روند
    
    این استراتژی به دنبال معامله در جهت روند اصلی پس از یک پولبک (اصلاح) است:
    - روند صعودی: EMA(50) بالای EMA(200) و قیمت در حال اصلاح به سمت فیبوناچی
    - روند نزولی: EMA(50) زیر EMA(200) و قیمت در حال اصلاح به سمت فیبوناچی
    """
    
    def __init__(self, ema_short=50, ema_long=200, rsi_period=14, rsi_threshold=40):
        """
        مقداردهی اولیه
        
        پارامترها:
            ema_short (int): دوره EMA کوتاه مدت
            ema_long (int): دوره EMA بلند مدت
            rsi_period (int): دوره RSI
            rsi_threshold (int): سطح RSI برای تأیید سیگنال
        """
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.rsi_period = rsi_period
        self.rsi_threshold = rsi_threshold
    
    def run(self, data):
        """
        اجرای استراتژی روی داده‌ها
        
        پارامترها:
            data (DataFrame): داده‌های قیمت
            
        خروجی:
            DataFrame: سیگنال‌های خرید و فروش
        """
        # محاسبه شاخص‌ها
        data['EMA_50'] = calculate_ema(data, self.ema_short)
        data['EMA_200'] = calculate_ema(data, self.ema_long)
        data['RSI'] = calculate_rsi(data, self.rsi_period)
        
        # تعیین روند
        data['UpTrend'] = data['EMA_50'] > data['EMA_200']
        
        # محاسبه فاصله قیمت از EMA کوتاه مدت (به عنوان معیاری برای پولبک)
        data['Price_to_EMA50'] = (data['Close'] - data['EMA_50']) / data['EMA_50'] * 100
        
        # شناسایی سیگنال‌های خرید و فروش
        signals = []
        
        for i in range(5, len(data)):
            # شرط روند صعودی
            uptrend = data['UpTrend'].iloc[i-5:i].all()
            
            # شرط روند نزولی
            downtrend = (~data['UpTrend'].iloc[i-5:i]).all()
            
            # شرط پولبک در روند صعودی: قیمت نزدیک EMA50 یا کمی زیر آن
            pullback_in_uptrend = uptrend and (-5 < data['Price_to_EMA50'].iloc[i] < 0)
            
            # شرط پولبک در روند نزولی: قیمت نزدیک EMA50 یا کمی بالای آن
            pullback_in_downtrend = downtrend and (0 < data['Price_to_EMA50'].iloc[i] < 5)
            
            # تأیید با RSI
            rsi_confirms_buy = data['RSI'].iloc[i] > self.rsi_threshold and data['RSI'].iloc[i] < 60
            rsi_confirms_sell = data['RSI'].iloc[i] < (100 - self.rsi_threshold) and data['RSI'].iloc[i] > 40
            
            # سیگنال خرید
            if pullback_in_uptrend and rsi_confirms_buy and data['Close'].iloc[i] > data['Close'].iloc[i-1]:
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': 1,  # 1 برای خرید
                    'RSI': data['RSI'].iloc[i],
                    'EMA_50': data['EMA_50'].iloc[i],
                    'EMA_200': data['EMA_200'].iloc[i]
                })
            
            # سیگنال فروش
            elif pullback_in_downtrend and rsi_confirms_sell and data['Close'].iloc[i] < data['Close'].iloc[i-1]:
                signals.append({
                    'Date': data['Date'].iloc[i],
                    'Price': data['Close'].iloc[i],
                    'Signal': -1,  # -1 برای فروش
                    'RSI': data['RSI'].iloc[i],
                    'EMA_50': data['EMA_50'].iloc[i],
                    'EMA_200': data['EMA_200'].iloc[i]
                })
        
        return pd.DataFrame(signals)
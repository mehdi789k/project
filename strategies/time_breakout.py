# -*- coding: utf-8 -*-
"""
استراتژی شکست بر اساس زمان
"""

import pandas as pd
import numpy as np
from datetime import time
from utils.indicators import calculate_atr, detect_support_resistance

class Time_Breakout_Strategy:
    """
    استراتژی شکست بر اساس زمان
    
    این استراتژی بر اساس شکست قیمت در زمان‌های خاصی از روز عمل می‌کند:
    - تعیین محدوده قیمت در ساعات اولیه معاملات
    - معامله بر اساس شکست این محدوده در ادامه روز
    """
    
    def __init__(self, morning_start=time(9, 30), morning_end=time(10, 0), 
                 breakout_threshold=0.5, volume_factor=1.5):
        """
        مقداردهی اولیه
        
        پارامترها:
            morning_start (time): زمان شروع تعیین محدوده
            morning_end (time): زمان پایان تعیین محدوده
            breakout_threshold (float): آستانه شکست (به درصد)
            volume_factor (float): ضریب حجم برای تأیید شکست
        """
        self.morning_start = morning_start
        self.morning_end = morning_end
        self.breakout_threshold = breakout_threshold
        self.volume_factor = volume_factor
    
    def run(self, data):
        """
        اجرای استراتژی روی داده‌ها
        
        پارامترها:
            data (DataFrame): داده‌های قیمت
            
        خروجی:
            DataFrame: سیگنال‌های خرید و فروش
        """
        # تبدیل ستون تاریخ به ساعت
        if 'Date' in data.columns and hasattr(data['Date'].iloc[0], 'time'):
            data['Time'] = data['Date'].apply(lambda x: x.time())
        else:
            # اگر ستون ساعت وجود نداشت، نمی‌توانیم این استراتژی را اجرا کنیم
            print("هشدار: داده‌های زمانی برای استراتژی شکست بر اساس زمان موجود نیست.")
            return pd.DataFrame()
        
        # محاسبه میانگین دامنه حقیقی (ATR)
        data['ATR'] = calculate_atr(data)
        
        # محاسبه میانگین حجم
        data['Avg_Volume'] = data['Volume'].rolling(window=20).mean()
        
        # تعیین محدوده صبحگاهی
        signals = []
        date_groups = data.groupby(data['Date'].dt.date)
        
        for date, group in date_groups:
            # فیلتر کردن کندل‌های صبحگاهی
            morning_candles = group[(group['Time'] >= self.morning_start) & (group['Time'] <= self.morning_end)]
            
            if len(morning_candles) > 0:
                # تعیین محدوده
                morning_high = morning_candles['High'].max()
                morning_low = morning_candles['Low'].min()
                
                # محاسبه دامنه
                range_size = morning_high - morning_low
                
                # تعیین شکست با استفاده از ATR
                atr_value = morning_candles['ATR'].iloc[-1]
                breakout_amount = atr_value * self.breakout_threshold
                
                # فیلتر کردن کندل‌های بعد از صبح
                day_candles = group[group['Time'] > self.morning_end]
                
                for i, row in day_candles.iterrows():
                    # شکست بالا
                    if row['High'] > (morning_high + breakout_amount) and row['Volume'] > (row['Avg_Volume'] * self.volume_factor):
                        signals.append({
                            'Date': row['Date'],
                            'Price': row['Close'],
                            'Signal': 1,  # 1 برای خرید
                            'Range_High': morning_high,
                            'Range_Low': morning_low,
                            'ATR': row['ATR']
                        })
                        break  # فقط اولین شکست در هر روز
                    
                    # شکست پایین
                    elif row['Low'] < (morning_low - breakout_amount) and row['Volume'] > (row['Avg_Volume'] * self.volume_factor):
                        signals.append({
                            'Date': row['Date'],
                            'Price': row['Close'],
                            'Signal': -1,  # -1 برای فروش
                            'Range_High': morning_high,
                            'Range_Low': morning_low,
                            'ATR': row['ATR']
                        })
                        break  # فقط اولین شکست در هر روز
        
        return pd.DataFrame(signals)
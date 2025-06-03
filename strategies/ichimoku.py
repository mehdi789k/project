# -*- coding: utf-8 -*-
"""
استراتژی ایچیموکو کلاود
"""

import pandas as pd
import numpy as np
from utils.indicators import calculate_ichimoku

class Ichimoku_Strategy:
    """
    استراتژی ایچیموکو کلاود
    
    این استراتژی بر اساس سیستم ایچیموکو عمل می‌کند:
    - خرید: هنگامی که تنکان-سن از بالای کیجون-سن عبور می‌کند و قیمت بالای ابر است
    - فروش: هنگامی که تنکان-سن از زیر کیجون-سن عبور می‌کند و قیمت زیر ابر است
    """
    
    def __init__(self, tenkan_period=9, kijun_period=26, senkou_b_period=52, displacement=26):
        """
        مقداردهی اولیه
        
        پارامترها:
            tenkan_period (int): دوره تنکان-سن
            kijun_period (int): دوره کیجون-سن
            senkou_b_period (int): دوره سنکو اسپن B
            displacement (int): میزان جابجایی
        """
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_b_period = senkou_b_period
        self.displacement = displacement
    
    def run(self, data):
        """
        اجرای استراتژی روی داده‌ها
        
        پارامترها:
            data (DataFrame): داده‌های قیمت
            
        خروجی:
            DataFrame: سیگنال‌های خرید و فروش
        """
        # محاسبه شاخص‌های ایچیموکو
        tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span = calculate_ichimoku(
            data, self.tenkan_period, self.kijun_period, self.senkou_b_period, self.displacement
        )
        
        data['Tenkan'] = tenkan_sen
        data['Kijun'] = kijun_sen
        data['Senkou_A'] = senkou_span_a
        data['Senkou_B'] = senkou_span_b
        data['Chikou'] = chikou_span
        
        # تعیین وضعیت ابر
        data['Cloud_Green'] = data['Senkou_A'] > data['Senkou_B']
        data['Above_Cloud'] = (data['Close'] > data['Senkou_A']) & (data['Close'] > data['Senkou_B'])
        data['Below_Cloud'] = (data['Close'] < data['Senkou_A']) & (data['Close'] < data['Senkou_B'])
        data['In_Cloud'] = ~(data['Above_Cloud'] | data['Below_Cloud'])
        
        # محاسبه کراس تنکان و کیجون
        data['TK_Cross'] = np.nan
        
        for i in range(1, len(data)):
            if (data['Tenkan'].iloc[i-1] < data['Kijun'].iloc[i-1]) and (data['Tenkan'].iloc[i] >= data['Kijun'].iloc[i]):
                data.loc[data.index[i], 'TK_Cross'] = 1  # کراس مثبت
            elif (data['Tenkan'].iloc[i-1] > data['Kijun'].iloc[i-1]) and (data['Tenkan'].iloc[i] <= data['Kijun'].iloc[i]):
                data.loc[data.index[i], 'TK_Cross'] = -1  # کراس منفی
        
        # شناسایی سیگنال‌های خرید و فروش
        signals = []
        
        for i in range(self.displacement, len(data)):
            # سیگنال خرید: کراس مثبت تنکان-کیجون و قیمت بالای ابر
            if (data['TK_Cross'].iloc[i] == 1) and data['Above_Cloud'].iloc[i]:
                # تأیید با چیکو اسپن
                if i+self.displacement < len(data) and data['Chikou'].iloc[i] > data['Close'].iloc[i-self.displacement]:
                    signals.append({
                        'Date': data['Date'].iloc[i],
                        'Price': data['Close'].iloc[i],
                        'Signal': 1,  # 1 برای خرید
                        'Tenkan': data['Tenkan'].iloc[i],
                        'Kijun': data['Kijun'].iloc[i],
                        'Cloud_Top': max(data['Senkou_A'].iloc[i], data['Senkou_B'].iloc[i]),
                        'Cloud_Bottom': min(data['Senkou_A'].iloc[i], data['Senkou_B'].iloc[i])
                    })
            
            # سیگنال فروش: کراس منفی تنکان-کیجون و قیمت زیر ابر
            elif (data['TK_Cross'].iloc[i] == -1) and data['Below_Cloud'].iloc[i]:
                # تأیید با چیکو اسپن
                if i+self.displacement < len(data) and data['Chikou'].iloc[i] < data['Close'].iloc[i-self.displacement]:
                    signals.append({
                        'Date': data['Date'].iloc[i],
                        'Price': data['Close'].iloc[i],
                        'Signal': -1,  # -1 برای فروش
                        'Tenkan': data['Tenkan'].iloc[i],
                        'Kijun': data['Kijun'].iloc[i],
                        'Cloud_Top': max(data['Senkou_A'].iloc[i], data['Senkou_B'].iloc[i]),
                        'Cloud_Bottom': min(data['Senkou_A'].iloc[i], data['Senkou_B'].iloc[i])
                    })
        
        return pd.DataFrame(signals)
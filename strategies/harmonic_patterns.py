# -*- coding: utf-8 -*-
"""
استراتژی الگوهای هارمونیک
"""

import pandas as pd
import numpy as np
from utils.indicators import calculate_rsi, fibonacci_levels

class Harmonic_Patterns_Strategy:
    """
    استراتژی الگوهای هارمونیک
    
    این استراتژی به دنبال شناسایی الگوهای هارمونیک (مانند Gartley و Butterfly) است:
    - شناسایی نقاط مهم XABCD
    - تأیید با نسبت‌های فیبوناچی
    - ورود در نقطه D
    """
    
    def __init__(self, min_swing=10, tolerance=0.05, rsi_period=14):
        """
        مقداردهی اولیه
        
        پارامترها:
            min_swing (int): حداقل طول موج برای شناسایی نقاط چرخش
            tolerance (float): میزان تلورانس برای نسبت‌های فیبوناچی
            rsi_period (int): دوره RSI برای تأیید سیگنال
        """
        self.min_swing = min_swing
        self.tolerance = tolerance
        self.rsi_period = rsi_period
    
    def find_swing_points(self, data, window=5):
        """
        شناسایی نقاط چرخش قیمت
        
        پارامترها:
            data (DataFrame): داده‌های قیمت
            window (int): اندازه پنجره برای شناسایی نقاط چرخش
            
        خروجی:
            tuple: (swing_highs, swing_lows)
        """
        swing_highs = []
        swing_lows = []
        
        for i in range(window, len(data) - window):
            # بررسی آیا کندل i یک نقطه چرخش بالا است
            if all(data['High'].iloc[i] > data['High'].iloc[i-j] for j in range(1, window+1)) and \
               all(data['High'].iloc[i] > data['High'].iloc[i+j] for j in range(1, window+1)):
                swing_highs.append((i, data['High'].iloc[i]))
            
            # بررسی آیا کندل i یک نقطه چرخش پایین است
            if all(data['Low'].iloc[i] < data['Low'].iloc[i-j] for j in range(1, window+1)) and \
               all(data['Low'].iloc[i] < data['Low'].iloc[i+j] for j in range(1, window+1)):
                swing_lows.append((i, data['Low'].iloc[i]))
        
        return swing_highs, swing_lows
    
    def check_gartley(self, points):
        """
        بررسی آیا نقاط داده شده الگوی Gartley را تشکیل می‌دهند
        
        پارامترها:
            points (list): لیست نقاط XABCD
            
        خروجی:
            bool: آیا الگوی Gartley است یا خیر
        """
        # استخراج نقاط
        x_idx, x_price = points[0]
        a_idx, a_price = points[1]
        b_idx, b_price = points[2]
        c_idx, c_price = points[3]
        d_idx, d_price = points[4]
        
        # محاسبه طول موج‌ها
        xa = abs(a_price - x_price)
        ab = abs(b_price - a_price)
        bc = abs(c_price - b_price)
        cd = abs(d_price - c_price)
        xd = abs(d_price - x_price)
        
        # بررسی نسبت‌های فیبوناچی
        ab_xa_ratio = ab / xa
        bc_ab_ratio = bc / ab
        cd_bc_ratio = cd / bc
        xd_xa_ratio = xd / xa
        
        # شرایط الگوی Gartley
        ab_check = 0.618 - self.tolerance <= ab_xa_ratio <= 0.618 + self.tolerance
        bc_check = 0.382 - self.tolerance <= bc_ab_ratio <= 0.886 + self.tolerance
        cd_check = 1.272 - self.tolerance <= cd_bc_ratio <= 1.272 + self.tolerance
        xd_check = 0.786 - self.tolerance <= xd_xa_ratio <= 0.786 + self.tolerance
        
        return ab_check and bc_check and cd_check and xd_check
    
    def check_butterfly(self, points):
        """
        بررسی آیا نقاط داده شده الگوی Butterfly را تشکیل می‌دهند
        
        پارامترها:
            points (list): لیست نقاط XABCD
            
        خروجی:
            bool: آیا الگوی Butterfly است یا خیر
        """
        # استخراج نقاط
        x_idx, x_price = points[0]
        a_idx, a_price = points[1]
        b_idx, b_price = points[2]
        c_idx, c_price = points[3]
        d_idx, d_price = points[4]
        
        # محاسبه طول موج‌ها
        xa = abs(a_price - x_price)
        ab = abs(b_price - a_price)
        bc = abs(c_price - b_price)
        cd = abs(d_price - c_price)
        xd = abs(d_price - x_price)
        
        # بررسی نسبت‌های فیبوناچی
        ab_xa_ratio = ab / xa
        bc_ab_ratio = bc / ab
        cd_bc_ratio = cd / bc
        xd_xa_ratio = xd / xa
        
        # شرایط الگوی Butterfly
        ab_check = 0.786 - self.tolerance <= ab_xa_ratio <= 0.786 + self.tolerance
        bc_check = 0.382 - self.tolerance <= bc_ab_ratio <= 0.886 + self.tolerance
        cd_check = 1.618 - self.tolerance <= cd_bc_ratio <= 1.618 + self.tolerance
        xd_check = 1.27 - self.tolerance <= xd_xa_ratio <= 1.27 + self.tolerance
        
        return ab_check and bc_check and cd_check and xd_check
    
    def run(self, data):
        """
        اجرای استراتژی روی داده‌ها
        
        پارامترها:
            data (DataFrame): داده‌های قیمت
            
        خروجی:
            DataFrame: سیگنال‌های خرید و فروش
        """
        # محاسبه RSI برای تأیید
        data['RSI'] = calculate_rsi(data, self.rsi_period)
        
        # شناسایی نقاط چرخش
        swing_highs, swing_lows = self.find_swing_points(data)
        
        # ترکیب نقاط چرخش و مرتب‌سازی بر اساس اندیس
        all_swings = swing_highs + swing_lows
        all_swings.sort(key=lambda x: x[0])
        
        signals = []
        
        # بررسی الگوهای هارمونیک با هر 5 نقطه متوالی
        for i in range(len(all_swings) - 4):
            points = all_swings[i:i+5]
            
            # بررسی آیا نقاط به اندازه کافی از هم فاصله دارند
            if points[4][0] - points[0][0] < self.min_swing:
                continue
            
            # بررسی الگوی Gartley
            if self.check_gartley(points):
                # استخراج نقطه D (آخرین نقطه)
                d_idx, d_price = points[4]
                
                # تعیین نوع الگو (Bullish یا Bearish)
                is_bullish = points[0][1] > points[4][1]  # اگر X بالاتر از D باشد، الگو صعودی است
                
                # تأیید با RSI
                if (is_bullish and data['RSI'].iloc[d_idx] < 30) or (not is_bullish and data['RSI'].iloc[d_idx] > 70):
                    signals.append({
                        'Date': data['Date'].iloc[d_idx],
                        'Price': data['Close'].iloc[d_idx],
                        'Signal': 1 if is_bullish else -1,
                        'Pattern': 'Gartley',
                        'RSI': data['RSI'].iloc[d_idx],
                        'X_Price': points[0][1],
                        'A_Price': points[1][1],
                        'B_Price': points[2][1],
                        'C_Price': points[3][1],
                        'D_Price': points[4][1]
                    })
            
            # بررسی الگوی Butterfly
            if self.check_butterfly(points):
                # استخراج نقطه D (آخرین نقطه)
                d_idx, d_price = points[4]
                
                # تعیین نوع الگو (Bullish یا Bearish)
                is_bullish = points[0][1] > points[4][1]  # اگر X بالاتر از D باشد، الگو صعودی است
                
                # تأیید با RSI
                if (is_bullish and data['RSI'].iloc[d_idx] < 30) or (not is_bullish and data['RSI'].iloc[d_idx] > 70):
                    signals.append({
                        'Date': data['Date'].iloc[d_idx],
                        'Price': data['Close'].iloc[d_idx],
                        'Signal': 1 if is_bullish else -1,
                        'Pattern': 'Butterfly',
                        'RSI': data['RSI'].iloc[d_idx],
                        'X_Price': points[0][1],
                        'A_Price': points[1][1],
                        'B_Price': points[2][1],
                        'C_Price': points[3][1],
                        'D_Price': points[4][1]
                    })
        
        return pd.DataFrame(signals)
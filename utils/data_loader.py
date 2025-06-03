# -*- coding: utf-8 -*-
"""
ماژول بارگذاری داده‌ها از فایل‌های CSV
"""

import pandas as pd
import re
import os

def load_csv_data(file_path):
    """
    بارگذاری داده‌های بازار مالی از فایل CSV
    
    پارامترها:
        file_path (str): مسیر فایل CSV
        
    خروجی:
        tuple: (DataFrame داده‌ها، نماد، تایم‌فریم)
    """
    # خواندن فایل CSV
    df = pd.read_csv(file_path)
    
    # استخراج نام نماد و تایم‌فریم از نام فایل
    file_name = os.path.basename(file_path)
    symbol_match = re.search(r'([A-Z]+/[A-Z]+|[A-Z]+)', file_name)
    timeframe_match = re.search(r'(M1|M5|M15|M30|H1|H4|D1|W1|MN)', file_name, re.IGNORECASE)
    
    symbol = symbol_match.group(1) if symbol_match else "Unknown"
    timeframe = timeframe_match.group(1) if timeframe_match else "Unknown"
    
    # تبدیل ستون تاریخ به تایپ datetime
    if 'Date' in df.columns or 'date' in df.columns:
        date_col = 'Date' if 'Date' in df.columns else 'date'
        df[date_col] = pd.to_datetime(df[date_col])
    
    # بررسی و تغییر نام ستون‌های ضروری
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    column_mapping = {}
    
    for col in df.columns:
        for req_col in required_columns:
            if req_col.lower() in col.lower():
                column_mapping[col] = req_col
    
    # تغییر نام ستون‌ها
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    # اطمینان از وجود ستون‌های ضروری
    for col in required_columns:
        if col not in df.columns:
            if col == 'Volume' and 'volume' in df.columns:
                df = df.rename(columns={'volume': 'Volume'})
            elif col == 'Close' and 'close' in df.columns:
                df = df.rename(columns={'close': 'Close'})
            elif col == 'Open' and 'open' in df.columns:
                df = df.rename(columns={'open': 'Open'})
            elif col == 'High' and 'high' in df.columns:
                df = df.rename(columns={'high': 'High'})
            elif col == 'Low' and 'low' in df.columns:
                df = df.rename(columns={'low': 'Low'})
            else:
                print(f"هشدار: ستون {col} در فایل وجود ندارد.")
    
    # تنظیم ایندکس
    if 'Date' in df.columns:
        df.set_index('Date', inplace=True)
    
    # مرتب‌سازی داده‌ها بر اساس تاریخ (صعودی)
    df.sort_index(inplace=True)
    
    # برگرداندن ایندکس به ستون عادی برای استفاده راحت‌تر
    df.reset_index(inplace=True)
    
    print(f"داده‌های {symbol} با تایم‌فریم {timeframe} بارگذاری شد.")
    print(f"تعداد رکوردها: {len(df)}")
    print(f"بازه زمانی: از {df['Date'].min()} تا {df['Date'].max()}")
    
    return df, symbol, timeframe
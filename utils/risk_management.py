# -*- coding: utf-8 -*-
"""
ماژول مدیریت ریسک
"""

import pandas as pd
import numpy as np

def calculate_risk_reward(signals, data, risk_ratio=2):
    """
    محاسبه حد ضرر و حد سود برای سیگنال‌ها
    
    پارامترها:
        signals (DataFrame): سیگنال‌های معاملاتی
        data (DataFrame): داده‌های قیمت
        risk_ratio (float): نسبت ریسک به ریوارد
        
    خروجی:
        DataFrame: سیگنال‌ها با اضافه شدن حد ضرر و حد سود
    """
    if signals.empty:
        return signals
    
    # محاسبه میانگین دامنه حقیقی (ATR) برای تعیین حد ضرر
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    atr = true_range.rolling(window=14).mean()
    
    # اضافه کردن ATR به سیگنال‌ها
    signals_with_dates = pd.merge_asof(signals.sort_values('Date'), 
                                      data[['Date', 'Close']].assign(ATR=atr),
                                      on='Date')
    
    # تعیین حد ضرر و حد سود بر اساس ATR
    signals_with_dates['StopLoss'] = signals_with_dates.apply(
        lambda row: row['Price'] - 1.5 * row['ATR'] if row['Signal'] == 1 else row['Price'] + 1.5 * row['ATR'],
        axis=1
    )
    
    signals_with_dates['TakeProfit'] = signals_with_dates.apply(
        lambda row: row['Price'] + risk_ratio * 1.5 * row['ATR'] if row['Signal'] == 1 else row['Price'] - risk_ratio * 1.5 * row['ATR'],
        axis=1
    )
    
    # محاسبه نسبت ریسک به ریوارد
    signals_with_dates['RiskReward'] = risk_ratio
    
    return signals_with_dates

def calculate_position_size(account_balance, risk_percentage, entry_price, stop_loss):
    """
    محاسبه اندازه پوزیشن بر اساس مدیریت ریسک
    
    پارامترها:
        account_balance (float): موجودی حساب
        risk_percentage (float): درصد ریسک (مثلاً 1 برای 1%)
        entry_price (float): قیمت ورود
        stop_loss (float): حد ضرر
        
    خروجی:
        float: اندازه پوزیشن (تعداد لات)
    """
    risk_amount = account_balance * (risk_percentage / 100)
    
    # محاسبه فاصله بین قیمت ورود و حد ضرر
    stop_distance = abs(entry_price - stop_loss)
    
    # محاسبه اندازه پوزیشن (برای ارزهای فارکس)
    if stop_distance > 0:
        position_size = risk_amount / stop_distance
    else:
        position_size = 0
    
    return position_size

def simulate_trades(signals, initial_balance=10000, risk_percentage=1):
    """
    شبیه‌سازی معاملات بر اساس سیگنال‌ها
    
    پارامترها:
        signals (DataFrame): سیگنال‌های معاملاتی با حد ضرر و حد سود
        initial_balance (float): موجودی اولیه حساب
        risk_percentage (float): درصد ریسک برای هر معامله
        
    خروجی:
        tuple: (DataFrame با نتایج معاملات، موجودی نهایی)
    """
    if signals.empty or 'StopLoss' not in signals.columns or 'TakeProfit' not in signals.columns:
        return signals, initial_balance
    
    balance = initial_balance
    results = []
    
    for i, row in signals.iterrows():
        # محاسبه اندازه پوزیشن
        position_size = calculate_position_size(balance, risk_percentage, row['Price'], row['StopLoss'])
        
        # محاسبه مقدار سود/ضرر
        if row['Signal'] == 1:  # خرید
            risk = (row['Price'] - row['StopLoss']) * position_size
            reward = (row['TakeProfit'] - row['Price']) * position_size
        else:  # فروش
            risk = (row['StopLoss'] - row['Price']) * position_size
            reward = (row['Price'] - row['TakeProfit']) * position_size
        
        # فرض کنید برای هر معامله یا به حد سود می‌رسیم یا به حد ضرر (50-50)
        # این بخش را می‌توانید با منطق پیچیده‌تری جایگزین کنید
        # مثلاً با استفاده از داده‌های تاریخی برای تعیین اینکه آیا به حد سود یا حد ضرر رسیده‌ایم
        
        # برای سادگی، فرض می‌کنیم نرخ برد 60% است
        if np.random.random() < 0.6:
            result = reward
            outcome = "سود"
        else:
            result = -risk
            outcome = "ضرر"
        
        # به‌روزرسانی موجودی
        balance += result
        
        # ذخیره نتیجه
        results.append({
            'Date': row['Date'],
            'Signal': row['Signal'],
            'Entry': row['Price'],
            'StopLoss': row['StopLoss'],
            'TakeProfit': row['TakeProfit'],
            'Position_Size': position_size,
            'Risk': risk,
            'Result': result,
            'Outcome': outcome,
            'Balance': balance
        })
    
    return pd.DataFrame(results), balance

def calculate_trading_metrics(results):
    """
    محاسبه معیارهای ارزیابی استراتژی
    
    پارامترها:
        results (DataFrame): نتایج معاملات
        
    خروجی:
        dict: معیارهای ارزیابی
    """
    if results.empty:
        return {}
    
    # تعداد کل معاملات
    total_trades = len(results)
    
    # تعداد معاملات سودده
    winning_trades = len(results[results['Result'] > 0])
    
    # تعداد معاملات ضررده
    losing_trades = len(results[results['Result'] < 0])
    
    # نرخ برد
    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
    
    # میانگین سود معاملات سودده
    avg_win = results[results['Result'] > 0]['Result'].mean() if winning_trades > 0 else 0
    
    # میانگین ضرر معاملات ضررده
    avg_loss = results[results['Result'] < 0]['Result'].mean() if losing_trades > 0 else 0
    
    # نسبت سود به ضرر
    profit_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
    
    # سود/ضرر کل
    total_profit = results['Result'].sum()
    
    # حداکثر افت سرمایه
    balance_curve = results['Balance'].values
    max_drawdown = 0
    peak = balance_curve[0]
    
    for value in balance_curve:
        if value > peak:
            peak = value
        
        dd = (peak - value) / peak * 100
        if dd > max_drawdown:
            max_drawdown = dd
    
    # شاخص شارپ (ساده‌سازی شده)
    returns = results['Result'] / results['Balance'].shift(1)
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_ratio': profit_ratio,
        'total_profit': total_profit,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio
    }
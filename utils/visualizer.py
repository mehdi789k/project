# -*- coding: utf-8 -*-
"""
ماژول نمایش نتایج تحلیل استراتژی‌ها
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.ticker import FuncFormatter
import mplcursors

def plot_strategy_results(data, signals, strategy_name, symbol, timeframe):
    """
    نمایش نتایج استراتژی
    
    پارامترها:
        data (DataFrame): داده‌های قیمت
        signals (DataFrame): سیگنال‌های معاملاتی
        strategy_name (str): نام استراتژی
        symbol (str): نماد
        timeframe (str): تایم‌فریم
    """
    # تنظیم فونت فارسی
    plt.rcParams['font.family'] = 'Tahoma'
    
    # ایجاد شکل و محورها
    fig, ax = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
    fig.suptitle(f'نتایج استراتژی {strategy_name} برای {symbol} ({timeframe})', fontsize=16)
    
    # نمودار قیمت
    ax[0].plot(data['Date'], data['Close'], label='قیمت بسته شدن', color='blue', linewidth=1.5)
    
    # اضافه کردن سیگنال‌های خرید
    buy_signals = signals[signals['Signal'] == 1]
    if not buy_signals.empty:
        ax[0].scatter(buy_signals['Date'], buy_signals['Price'], 
                     marker='^', color='green', s=100, label='سیگنال خرید')
    
    # اضافه کردن سیگنال‌های فروش
    sell_signals = signals[signals['Signal'] == -1]
    if not sell_signals.empty:
        ax[0].scatter(sell_signals['Date'], sell_signals['Price'], 
                     marker='v', color='red', s=100, label='سیگنال فروش')
    
    # اضافه کردن حد ضرر و حد سود
    for _, signal in buy_signals.iterrows():
        ax[0].plot([signal['Date'], signal['Date']], 
                  [signal['StopLoss'], signal['TakeProfit']], 
                  color='purple', linestyle='--', alpha=0.7)
    
    for _, signal in sell_signals.iterrows():
        ax[0].plot([signal['Date'], signal['Date']], 
                  [signal['StopLoss'], signal['TakeProfit']], 
                  color='purple', linestyle='--', alpha=0.7)
    
    # اضافه کردن اطلاعات بیشتر استراتژی
    if 'RSI' in signals.columns:
        ax[1].plot(data['Date'], signals['RSI'], label='RSI', color='purple', linewidth=1.5)
        ax[1].axhline(y=30, color='green', linestyle='--', alpha=0.5)
        ax[1].axhline(y=70, color='red', linestyle='--', alpha=0.5)
        ax[1].set_ylabel('RSI', fontsize=12)
        ax[1].set_ylim(0, 100)
    elif 'EMA_50' in signals.columns and 'EMA_200' in signals.columns:
        ax[1].plot(data['Date'], signals['EMA_50'], label='EMA 50', color='orange', linewidth=1.5)
        ax[1].plot(data['Date'], signals['EMA_200'], label='EMA 200', color='purple', linewidth=1.5)
        ax[1].set_ylabel('EMA', fontsize=12)
    
    # تنظیمات محور و راهنما
    ax[0].set_ylabel('قیمت', fontsize=12)
    ax[0].grid(True, alpha=0.3)
    ax[0].legend(loc='upper left')
    
    ax[1].grid(True, alpha=0.3)
    ax[1].legend(loc='upper left')
    
    # تنظیم فرمت تاریخ
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # چرخش برچسب‌های تاریخ
    plt.setp(ax[0].xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax[1].xaxis.get_majorticklabels(), rotation=45)
    
    # اضافه کردن آمار
    win_rate = calculate_win_rate(signals)
    profit_factor = calculate_profit_factor(signals)
    
    stats_text = f'نرخ موفقیت: {win_rate:.2f}%\nضریب سودآوری: {profit_factor:.2f}'
    ax[0].annotate(stats_text, xy=(0.02, 0.02), xycoords='axes fraction', 
                  bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7),
                  fontsize=10, verticalalignment='bottom')
    
    # اضافه کردن اطلاعات تعاملی با موس
    cursor = mplcursors.cursor(hover=True)
    
    @cursor.connect("add")
    def on_add(sel):
        x, y = sel.target
        date = mdates.num2date(x).strftime('%Y-%m-%d')
        sel.annotation.set(text=f'تاریخ: {date}\nقیمت: {y:.5f}')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.94)
    plt.show()

def calculate_win_rate(signals):
    """محاسبه نرخ موفقیت"""
    if 'Result' not in signals.columns or len(signals) == 0:
        return 0
    
    wins = len(signals[signals['Result'] > 0])
    return (wins / len(signals)) * 100

def calculate_profit_factor(signals):
    """محاسبه ضریب سودآوری"""
    if 'Result' not in signals.columns or len(signals) == 0:
        return 0
    
    total_profit = signals[signals['Result'] > 0]['Result'].sum()
    total_loss = abs(signals[signals['Result'] < 0]['Result'].sum())
    
    if total_loss == 0:
        return float('inf')
    
    return total_profit / total_loss

def plot_equity_curve(signals):
    """نمایش منحنی سرمایه"""
    if 'Result' not in signals.columns or len(signals) == 0:
        return
    
    equity = 10000  # سرمایه اولیه
    equity_curve = [equity]
    
    for _, signal in signals.iterrows():
        equity += signal['Result']
        equity_curve.append(equity)
    
    dates = list(signals['Date'])
    dates.insert(0, dates[0] - pd.Timedelta(days=1))  # افزودن یک تاریخ قبل از اولین معامله
    
    plt.figure(figsize=(14, 6))
    plt.plot(dates, equity_curve, linewidth=2)
    plt.title('منحنی سرمایه')
    plt.xlabel('تاریخ')
    plt.ylabel('سرمایه (دلار)')
    plt.grid(True, alpha=0.3)
    
    # فرمت‌دهی محور عمودی به صورت دلار
    def currency_formatter(x, pos):
        return f'${x:,.0f}'
    
    plt.gca().yaxis.set_major_formatter(FuncFormatter(currency_formatter))
    
    # چرخش برچسب‌های تاریخ
    plt.xticks(rotation=45)
    
    # محاسبه و نمایش بازده کلی
    total_return = ((equity_curve[-1] - equity_curve[0]) / equity_curve[0]) * 100
    max_drawdown = calculate_max_drawdown(equity_curve)
    
    stats_text = f'بازده کلی: {total_return:.2f}%\nحداکثر افت سرمایه: {max_drawdown:.2f}%'
    plt.annotate(stats_text, xy=(0.02, 0.02), xycoords='axes fraction', 
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7),
                fontsize=10, verticalalignment='bottom')
    
    plt.tight_layout()
    plt.show()

def calculate_max_drawdown(equity_curve):
    """محاسبه حداکثر افت سرمایه"""
    max_dd = 0
    peak = equity_curve[0]
    
    for value in equity_curve:
        if value > peak:
            peak = value
        
        dd = (peak - value) / peak * 100
        if dd > max_dd:
            max_dd = dd
    
    return max_dd
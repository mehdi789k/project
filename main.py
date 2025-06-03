# -*- coding: utf-8 -*-
"""
برنامه اصلی تحلیل استراتژی‌های معاملاتی
نوشته شده برای ویندوز 11 و پایتون 3.11.9
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# وارد کردن ماژول‌های استراتژی
from strategies.rsi_ema import RSI_EMA_Strategy
from strategies.bollinger_rsi import Bollinger_RSI_Strategy
from strategies.trend_pullback import Trend_Pullback_Strategy
from strategies.time_breakout import Time_Breakout_Strategy
from strategies.ichimoku import Ichimoku_Strategy
from strategies.harmonic_patterns import Harmonic_Patterns_Strategy
from strategies.divergence import Divergence_Strategy
from strategies.ma_crossover import MA_Crossover_Strategy

from utils.data_loader import load_csv_data
from utils.visualizer import plot_strategy_results
from utils.risk_management import calculate_risk_reward

class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("سیستم تحلیل استراتژی‌های معاملاتی")
        self.root.geometry("1000x700")
        
        # تنظیم فونت برای نمایش متون فارسی
        self.font = ('Tahoma', 10)
        
        self.create_widgets()
        
        # لیست استراتژی‌ها
        self.strategies = {
            "RSI + EMA": RSI_EMA_Strategy(),
            "بولینگر باند + RSI": Bollinger_RSI_Strategy(),
            "استراتژی پولبک روند": Trend_Pullback_Strategy(),
            "شکست بر اساس زمان": Time_Breakout_Strategy(),
            "ایچیموکو": Ichimoku_Strategy(),
            "الگوهای هارمونیک": Harmonic_Patterns_Strategy(),
            "واگرایی": Divergence_Strategy(),
            "کراس مووینگ اوریج": MA_Crossover_Strategy()
        }
        
        # داده‌های فعلی
        self.data = None
        self.symbol = None
        self.timeframe = None
        
    def create_widgets(self):
        # ایجاد فریم اصلی
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # فریم بالایی برای انتخاب فایل و استراتژی
        top_frame = ttk.Frame(main_frame, padding="5")
        top_frame.pack(fill=tk.X, pady=5)
        
        # دکمه انتخاب فایل CSV
        ttk.Button(top_frame, text="انتخاب فایل CSV", command=self.load_csv).pack(side=tk.LEFT, padx=5)
        
        # نمایش فایل انتخاب شده
        self.file_label = ttk.Label(top_frame, text="فایلی انتخاب نشده است", font=self.font)
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        # فریم استراتژی‌ها
        strategy_frame = ttk.LabelFrame(main_frame, text="انتخاب استراتژی", padding="10")
        strategy_frame.pack(fill=tk.X, pady=5)
        
        # لیست استراتژی‌ها
        self.strategy_var = tk.StringVar()
        strategies = ["RSI + EMA", "بولینگر باند + RSI", "استراتژی پولبک روند", 
                     "شکست بر اساس زمان", "ایچیموکو", "الگوهای هارمونیک",
                     "واگرایی", "کراس مووینگ اوریج"]
        
        self.strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.strategy_var, 
                                          values=strategies, font=self.font, width=30)
        self.strategy_combo.current(0)
        self.strategy_combo.pack(side=tk.LEFT, padx=5)
        
        # دکمه اجرای استراتژی
        ttk.Button(strategy_frame, text="اجرای استراتژی", 
                  command=self.run_strategy).pack(side=tk.LEFT, padx=5)
        
        # دکمه نمایش نتایج
        ttk.Button(strategy_frame, text="نمایش نمودار", 
                  command=self.show_chart).pack(side=tk.LEFT, padx=5)
        
        # فریم پارامترهای استراتژی
        self.params_frame = ttk.LabelFrame(main_frame, text="پارامترهای استراتژی", padding="10")
        self.params_frame.pack(fill=tk.X, pady=5)
        
        # فریم نتایج
        results_frame = ttk.LabelFrame(main_frame, text="نتایج", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # جدول نتایج
        columns = ('تاریخ', 'قیمت', 'نوع سیگنال', 'حد ضرر', 'حد سود', 'نسبت ریسک/ریوارد')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        # تنظیم عناوین ستون‌ها
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100, anchor='center')
        
        # اضافه کردن اسکرول‌بار
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # وضعیت
        self.status_var = tk.StringVar()
        self.status_var.set("آماده برای کار")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, font=self.font, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    def load_csv(self):
        """بارگذاری فایل CSV"""
        file_path = filedialog.askopenfilename(
            title="انتخاب فایل CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.data, self.symbol, self.timeframe = load_csv_data(file_path)
                file_name = os.path.basename(file_path)
                self.file_label.config(text=f"فایل انتخاب شده: {file_name}")
                self.status_var.set(f"فایل {file_name} با موفقیت بارگذاری شد.")
                
                # نمایش چند ردیف اول داده‌ها
                print(f"اطلاعات فایل {file_name}:")
                print(self.data.head())
                
                messagebox.showinfo("بارگذاری موفق", f"فایل {file_name} با موفقیت بارگذاری شد.\n"
                                   f"تعداد رکوردها: {len(self.data)}")
            except Exception as e:
                self.status_var.set(f"خطا در بارگذاری فایل: {str(e)}")
                messagebox.showerror("خطا", f"خطا در بارگذاری فایل:\n{str(e)}")
    
    def run_strategy(self):
        """اجرای استراتژی انتخاب شده"""
        if self.data is None:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک فایل CSV انتخاب کنید.")
            return
        
        strategy_name = self.strategy_var.get()
        self.status_var.set(f"در حال اجرای استراتژی {strategy_name}...")
        
        try:
            # پاک کردن جدول نتایج
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # اجرای استراتژی انتخاب شده
            strategy = self.strategies[strategy_name]
            signals = strategy.run(self.data.copy())
            
            if signals.empty:
                self.status_var.set(f"هیچ سیگنالی برای استراتژی {strategy_name} یافت نشد.")
                messagebox.info("اطلاعات", "هیچ سیگنالی یافت نشد.")
                return
            
            # محاسبه مدیریت ریسک
            signals = calculate_risk_reward(signals, self.data)
            
            # نمایش نتایج در جدول
            for _, row in signals.iterrows():
                date = row['Date']
                price = row['Price']
                signal_type = "خرید" if row['Signal'] == 1 else "فروش"
                stop_loss = row['StopLoss']
                take_profit = row['TakeProfit']
                risk_reward = row['RiskReward']
                
                self.results_tree.insert('', 'end', values=(date, price, signal_type, stop_loss, take_profit, risk_reward))
            
            self.status_var.set(f"استراتژی {strategy_name} با موفقیت اجرا شد. {len(signals)} سیگنال یافت شد.")
            self.signals = signals  # ذخیره سیگنال‌ها برای نمایش نمودار
            
        except Exception as e:
            self.status_var.set(f"خطا در اجرای استراتژی: {str(e)}")
            messagebox.showerror("خطا", f"خطا در اجرای استراتژی:\n{str(e)}")
    
    def show_chart(self):
        """نمایش نمودار نتایج"""
        if not hasattr(self, 'signals') or self.signals is None or self.data is None:
            messagebox.showwarning("هشدار", "لطفاً ابتدا یک استراتژی را اجرا کنید.")
            return
        
        try:
            strategy_name = self.strategy_var.get()
            plot_strategy_results(self.data, self.signals, strategy_name, self.symbol, self.timeframe)
            self.status_var.set(f"نمودار استراتژی {strategy_name} با موفقیت نمایش داده شد.")
        except Exception as e:
            self.status_var.set(f"خطا در نمایش نمودار: {str(e)}")
            messagebox.showerror("خطا", f"خطا در نمایش نمودار:\n{str(e)}")

def main():
    """تابع اصلی برنامه"""
    # ایجاد پوشه‌های مورد نیاز
    os.makedirs('csv', exist_ok=True)
    
    # تنظیم برای نمایش صحیح متن فارسی در پایتون
    plt.rcParams['font.family'] = 'Tahoma'
    
    # شروع برنامه
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
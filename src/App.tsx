import React, { useState, useEffect } from 'react';
import { LineChart, Timer, TrendingUp, TrendingDown, Target, AlertTriangle, ArrowUp, ArrowDown, Calendar } from 'lucide-react';

interface TradeData {
  date: string;
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface Signal {
  date: string;
  price: number;
  type: 'buy' | 'sell';
  stopLoss: number;
  targets: number[];
  strategy: string;
  confirmation: string[];
  predictedTime?: string;
  probability?: number;
}

interface Strategy {
  name: string;
  timeframe: string;
  signals: Signal[];
  indicators: string[];
  futurePredictions?: Signal[];
}

function App() {
  const [selectedTimeframe, setSelectedTimeframe] = useState('M15');
  const [selectedStrategy, setSelectedStrategy] = useState('rsi-ema');
  const [data, setData] = useState<TradeData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<Signal[]>([]);

  useEffect(() => {
    // Parse CSV data
    const parseCSV = () => {
      try {
        // Sample data processing - replace with actual CSV parsing
        const csvRows = `Date,Time,Open,High,Low,Close,Volume,Openint
2025-05-19,15:15:00,4.4384,4.4857,4.4384,4.4713,105825.35994`.split('\n');

        const parsedData = csvRows.slice(1).map(row => {
          const [date, time, open, high, low, close, volume] = row.split(',');
          return {
            date: `${date} ${time}`,
            time,
            open: parseFloat(open),
            high: parseFloat(high),
            low: parseFloat(low),
            close: parseFloat(close),
            volume: parseFloat(volume)
          };
        });

        setData(parsedData);
        generatePredictions(parsedData);
        setError(null);
      } catch (err) {
        setError('خطا در پردازش داده‌ها. لطفاً فرمت فایل CSV را بررسی کنید.');
        console.error('Error parsing CSV:', err);
      }
    };

    parseCSV();
  }, []);

  const generatePredictions = (data: TradeData[]) => {
    if (!data.length) return;

    // Get last candle
    const lastCandle = data[data.length - 1];
    const lastClose = lastCandle.close;
    const lastHigh = lastCandle.high;
    const lastLow = lastCandle.low;

    // Calculate technical indicators
    const rsi = calculateRSI(data);
    const ema50 = calculateEMA(data, 50);
    const ema200 = calculateEMA(data, 200);
    const atr = calculateATR(data);

    // Generate future predictions
    const futurePredictions: Signal[] = [];

    // Predict next 3 trading sessions
    for (let i = 1; i <= 3; i++) {
      const predictedDate = new Date(lastCandle.date);
      predictedDate.setHours(predictedDate.getHours() + (4 * i));

      // Calculate predicted ranges based on ATR
      const upperRange = lastClose + (atr * 1.5);
      const lowerRange = lastClose - (atr * 1.5);

      // Determine signal type based on indicators
      const isUptrend = lastClose > ema50 && ema50 > ema200;
      const isOverSold = rsi < 30;
      const isOverBought = rsi > 70;

      let signalType: 'buy' | 'sell' = 'buy';
      let predictedPrice = lastClose;
      let probability = 0.5;

      if (isUptrend && isOverSold) {
        signalType = 'buy';
        predictedPrice = upperRange;
        probability = 0.7;
      } else if (!isUptrend && isOverBought) {
        signalType = 'sell';
        predictedPrice = lowerRange;
        probability = 0.7;
      }

      futurePredictions.push({
        date: predictedDate.toISOString(),
        price: predictedPrice,
        type: signalType,
        stopLoss: signalType === 'buy' ? predictedPrice * 0.99 : predictedPrice * 1.01,
        targets: signalType === 'buy' 
          ? [predictedPrice * 1.01, predictedPrice * 1.02, predictedPrice * 1.03]
          : [predictedPrice * 0.99, predictedPrice * 0.98, predictedPrice * 0.97],
        strategy: 'پیش‌بینی آینده',
        confirmation: [
          'تحلیل روند قیمت',
          'شاخص‌های تکنیکال',
          'الگوهای قیمتی'
        ],
        predictedTime: `${predictedDate.getHours()}:${predictedDate.getMinutes()}`,
        probability: probability
      });
    }

    setPredictions(futurePredictions);
  };

  const calculateRSI = (data: TradeData[], period = 14): number => {
    if (data.length < period) return 50;
    
    let gains = 0;
    let losses = 0;
    
    for (let i = data.length - period; i < data.length; i++) {
      const change = data[i].close - data[i-1].close;
      if (change >= 0) {
        gains += change;
      } else {
        losses -= change;
      }
    }
    
    const avgGain = gains / period;
    const avgLoss = losses / period;
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  };

  const calculateEMA = (data: TradeData[], period: number): number => {
    if (data.length < period) return data[data.length - 1].close;
    
    const multiplier = 2 / (period + 1);
    let ema = data[0].close;
    
    for (let i = 1; i < data.length; i++) {
      ema = (data[i].close - ema) * multiplier + ema;
    }
    
    return ema;
  };

  const calculateATR = (data: TradeData[], period = 14): number => {
    if (data.length < 2) return 0;
    
    const trueRanges = data.slice(1).map((candle, i) => {
      const previousClose = data[i].close;
      const high = candle.high;
      const low = candle.low;
      
      return Math.max(
        high - low,
        Math.abs(high - previousClose),
        Math.abs(low - previousClose)
      );
    });
    
    return trueRanges.reduce((sum, tr) => sum + tr, 0) / trueRanges.length;
  };

  return (
    <div className="min-h-screen bg-gray-100" dir="rtl">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <LineChart className="h-8 w-8 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">تحلیل استراتژی‌های معاملاتی</h1>
            </div>
            <div className="flex items-center gap-4">
              <Timer className="h-6 w-6 text-gray-500" />
              <select 
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="M15">M15</option>
                <option value="H1">H1</option>
                <option value="H4">H4</option>
                <option value="D1">D1</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center text-red-700">
              <AlertTriangle className="h-5 w-5 ml-2" />
              <span>{error}</span>
            </div>
          </div>
        ) : (
          <>
            {/* Current Signals */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {predictions.map((signal, index) => (
                <div key={index} className="bg-white rounded-lg shadow p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      <Calendar className="h-5 w-5 text-gray-500 ml-2" />
                      <span className="text-sm text-gray-500">پیش‌بینی برای {new Date(signal.date).toLocaleDateString('fa-IR')}</span>
                    </div>
                    <span className="text-sm text-gray-500">ساعت {signal.predictedTime}</span>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center">
                      {signal.type === 'buy' ? (
                        <ArrowUp className="h-5 w-5 text-green-500 ml-2" />
                      ) : (
                        <ArrowDown className="h-5 w-5 text-red-500 ml-2" />
                      )}
                      <span className={`px-2 py-1 rounded text-sm font-medium ${
                        signal.type === 'buy' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {signal.type === 'buy' ? 'خرید' : 'فروش'}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-gray-500">
                      احتمال: {(signal.probability || 0) * 100}%
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-sm text-gray-500">قیمت پیش‌بینی شده</div>
                      <div className="text-lg font-semibold">{signal.price.toFixed(4)}</div>
                    </div>
                    <div className="bg-red-50 p-3 rounded">
                      <div className="text-sm text-red-500">حد ضرر</div>
                      <div className="text-lg font-semibold">{signal.stopLoss.toFixed(4)}</div>
                    </div>
                  </div>

                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">اهداف قیمتی</h3>
                    <div className="grid grid-cols-3 gap-2">
                      {signal.targets.map((target, idx) => (
                        <div key={idx} className="bg-green-50 p-2 rounded">
                          <div className="text-xs text-green-600">هدف {idx + 1}</div>
                          <div className="text-sm font-semibold">{target.toFixed(4)}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">دلایل تحلیل</h3>
                    <ul className="space-y-2">
                      {signal.confirmation.map((point, idx) => (
                        <li key={idx} className="flex items-center text-sm text-gray-600">
                          <AlertTriangle className="h-4 w-4 text-yellow-500 ml-2" />
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
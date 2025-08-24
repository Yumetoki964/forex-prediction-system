import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Brain,
  AlertCircle,
  CheckCircle,
  RefreshCw,
  Download,
  Calendar,
  Target,
  Activity,
  Zap
} from "lucide-react";
import axios from 'axios';
import { format, addDays, parseISO } from 'date-fns';
import { ja } from 'date-fns/locale';

const PredictionDashboard = () => {
  const [predictions, setPredictions] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('1week');
  const [selectedPair, setSelectedPair] = useState('USD/JPY');
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8174';

  // モデルステータスを取得
  const fetchModelStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_BASE}/api/ml/model-status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setModelStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch model status:', error);
    }
  };

  // 予測を実行
  const makePrediction = async () => {
    setIsPredicting(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE}/api/ml/predict`,
        null,
        {
          params: {
            currency_pair: selectedPair,
            periods: ['1day', '1week', '2weeks', '1month']
          },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.data.status === 'success') {
        setPredictions(response.data);
        prepareChartData(response.data);
      }
    } catch (error) {
      console.error('Failed to make prediction:', error);
    } finally {
      setIsPredicting(false);
    }
  };

  // モデルを訓練
  const trainModel = async () => {
    setIsTraining(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE}/api/ml/train-sync`,
        null,
        {
          params: {
            currency_pair: selectedPair,
            force_retrain: true
          },
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.data.status === 'success') {
        await fetchModelStatus();
        await makePrediction();
      }
    } catch (error) {
      console.error('Failed to train model:', error);
    } finally {
      setIsTraining(false);
    }
  };

  // チャートデータを準備
  const prepareChartData = (predictionData) => {
    if (!predictionData || !predictionData.predictions) return;

    const currentDate = new Date();
    const currentRate = predictionData.current_rate;

    // 予測データポイントを作成
    const data = [
      {
        date: format(currentDate, 'MM/dd'),
        actual: currentRate,
        predicted: currentRate,
        lower: currentRate,
        upper: currentRate,
        type: '現在'
      }
    ];

    // 各予測期間のデータを追加
    const periods = {
      '1day': 1,
      '1week': 7,
      '2weeks': 14,
      '1month': 30
    };

    Object.entries(periods).forEach(([period, days]) => {
      if (predictionData.predictions[period]) {
        const pred = predictionData.predictions[period];
        data.push({
          date: format(addDays(currentDate, days), 'MM/dd'),
          predicted: pred.predicted_rate,
          lower: pred.confidence_interval.lower,
          upper: pred.confidence_interval.upper,
          type: period
        });
      }
    });

    setChartData(data);
  };

  // 初期データ取得
  useEffect(() => {
    fetchModelStatus();
    makePrediction();
  }, []);

  // シグナルアイコンを取得
  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'strong_buy':
      case 'buy':
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'strong_sell':
      case 'sell':
        return <TrendingDown className="h-5 w-5 text-red-500" />;
      default:
        return <Minus className="h-5 w-5 text-gray-500" />;
    }
  };

  // シグナルバッジの色を取得
  const getSignalVariant = (signal) => {
    switch (signal) {
      case 'strong_buy':
        return 'success';
      case 'buy':
        return 'outline';
      case 'strong_sell':
        return 'destructive';
      case 'sell':
        return 'secondary';
      default:
        return 'default';
    }
  };

  // 変化率の色を取得
  const getChangeColor = (change) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="h-6 w-6" />
            AI予測ダッシュボード
          </h2>
          <Badge variant={modelStatus?.is_loaded ? "success" : "secondary"}>
            {modelStatus?.is_loaded ? "モデル準備完了" : "モデル未読込"}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <Select value={selectedPair} onValueChange={setSelectedPair}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="USD/JPY">USD/JPY</SelectItem>
              <SelectItem value="EUR/USD">EUR/USD</SelectItem>
              <SelectItem value="GBP/USD">GBP/USD</SelectItem>
              <SelectItem value="EUR/JPY">EUR/JPY</SelectItem>
            </SelectContent>
          </Select>
          <Button
            onClick={trainModel}
            disabled={isTraining}
            variant="outline"
          >
            {isTraining ? (
              <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> 訓練中...</>
            ) : (
              <><Zap className="h-4 w-4 mr-2" /> モデル訓練</>
            )}
          </Button>
          <Button
            onClick={makePrediction}
            disabled={isPredicting}
          >
            {isPredicting ? (
              <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> 予測中...</>
            ) : (
              <><Target className="h-4 w-4 mr-2" /> 予測実行</>
            )}
          </Button>
        </div>
      </div>

      {/* 現在のレートと概要 */}
      {predictions && (
        <Card>
          <CardHeader>
            <CardTitle>現在の状況</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">現在レート</p>
                <p className="text-2xl font-bold">
                  ¥{predictions.current_rate?.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">1週間後予測</p>
                <div className="flex items-center gap-2">
                  <p className="text-xl font-semibold">
                    ¥{predictions.predictions?.['1week']?.predicted_rate?.toFixed(2)}
                  </p>
                  <span className={`text-sm ${getChangeColor(predictions.predictions?.['1week']?.change_percent)}`}>
                    {predictions.predictions?.['1week']?.change_percent > 0 ? '+' : ''}
                    {predictions.predictions?.['1week']?.change_percent?.toFixed(2)}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">1ヶ月後予測</p>
                <div className="flex items-center gap-2">
                  <p className="text-xl font-semibold">
                    ¥{predictions.predictions?.['1month']?.predicted_rate?.toFixed(2)}
                  </p>
                  <span className={`text-sm ${getChangeColor(predictions.predictions?.['1month']?.change_percent)}`}>
                    {predictions.predictions?.['1month']?.change_percent > 0 ? '+' : ''}
                    {predictions.predictions?.['1month']?.change_percent?.toFixed(2)}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600">推奨アクション</p>
                <div className="flex items-center gap-2 mt-1">
                  {getSignalIcon(predictions.predictions?.['1week']?.signal)}
                  <Badge variant={getSignalVariant(predictions.predictions?.['1week']?.signal)}>
                    {predictions.predictions?.['1week']?.signal?.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 予測チャート */}
      <Card>
        <CardHeader>
          <CardTitle>予測チャート</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorPrediction" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={['dataMin - 1', 'dataMax + 1']} />
              <Tooltip 
                formatter={(value) => `¥${value?.toFixed(2)}`}
                labelFormatter={(label) => `日付: ${label}`}
              />
              <Legend />
              
              {/* 信頼区間 */}
              <Area
                type="monotone"
                dataKey="upper"
                stroke="none"
                fill="#8884d8"
                fillOpacity={0.2}
                name="信頼区間上限"
              />
              <Area
                type="monotone"
                dataKey="lower"
                stroke="none"
                fill="#8884d8"
                fillOpacity={0.2}
                name="信頼区間下限"
              />
              
              {/* 予測値 */}
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="#8884d8"
                strokeWidth={3}
                dot={{ r: 6 }}
                name="予測値"
              />
              
              {/* 現在値 */}
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#82ca9d"
                strokeWidth={2}
                dot={{ r: 4 }}
                name="現在値"
              />
              
              {/* 現在値の参照線 */}
              {predictions && (
                <ReferenceLine
                  y={predictions.current_rate}
                  stroke="#666"
                  strokeDasharray="3 3"
                  label="現在レート"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* 期間別予測詳細 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {predictions?.predictions && Object.entries({
          '1day': '1日後',
          '1week': '1週間後',
          '2weeks': '2週間後',
          '1month': '1ヶ月後'
        }).map(([key, label]) => {
          const pred = predictions.predictions[key];
          if (!pred) return null;
          
          return (
            <Card key={key}>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center justify-between">
                  <span>{label}</span>
                  {getSignalIcon(pred.signal)}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">予測レート</p>
                  <p className="text-xl font-bold">
                    ¥{pred.predicted_rate?.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">変化率</p>
                  <p className={`text-lg font-semibold ${getChangeColor(pred.change_percent)}`}>
                    {pred.change_percent > 0 ? '+' : ''}
                    {pred.change_percent?.toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">信頼区間</p>
                  <p className="text-sm">
                    ¥{pred.confidence_interval?.lower?.toFixed(2)} ~ ¥{pred.confidence_interval?.upper?.toFixed(2)}
                  </p>
                </div>
                <Badge 
                  variant={getSignalVariant(pred.signal)}
                  className="w-full justify-center"
                >
                  {pred.signal?.replace('_', ' ').toUpperCase()}
                </Badge>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* モデル情報 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            モデル情報
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">モデルタイプ</p>
              <p className="font-medium">LSTM + XGBoost アンサンブル</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">ステータス</p>
              <Badge variant={modelStatus?.is_loaded ? "success" : "secondary"}>
                {modelStatus?.is_loaded ? "準備完了" : "未準備"}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-gray-600">モデルバージョン</p>
              <p className="font-medium">v1.0.0</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">最終更新</p>
              <p className="font-medium">
                {modelStatus?.last_check ? format(parseISO(modelStatus.last_check), 'MM/dd HH:mm') : '-'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PredictionDashboard;
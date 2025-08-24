import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Tooltip,
  IconButton,
  Skeleton
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Remove,
  Psychology,
  RefreshRounded,
  ModelTraining
} from '@mui/icons-material';
import {
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart,
  Line
} from 'recharts';
import { format, addDays } from 'date-fns';
import axios from 'axios';

interface MLPrediction {
  predicted_rate: number;
  confidence_interval: {
    lower: number;
    upper: number;
  };
  change_percent: number;
  signal: string;
}

interface PredictionData {
  status: string;
  currency_pair: string;
  current_rate: number;
  predictions: {
    '1day': MLPrediction;
    '1week': MLPrediction;
    '2weeks': MLPrediction;
    '1month': MLPrediction;
  };
  timestamp: string;
}

interface MLPredictionCardProps {
  currencyPair?: string;
}

export const MLPredictionCard: React.FC<MLPredictionCardProps> = ({ 
  currencyPair = 'USD/JPY' 
}) => {
  const [predictions, setPredictions] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [selectedPeriod, setSelectedPeriod] = useState<string>('1week');

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8174';

  // 予測を取得
  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE}/api/ml/predict`,
        null,
        {
          params: {
            currency_pair: currencyPair,
            periods: ['1day', '1week', '2weeks', '1month']
          },
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        }
      );
      
      if (response.data.status === 'success') {
        setPredictions(response.data);
        prepareChartData(response.data);
      } else {
        setError('予測の取得に失敗しました');
      }
    } catch (err: any) {
      setError(err.message || '予測の取得中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  // チャートデータを準備
  const prepareChartData = (data: PredictionData) => {
    const currentDate = new Date();
    const currentRate = data.current_rate;

    const chartPoints = [
      {
        date: format(currentDate, 'MM/dd'),
        actual: currentRate,
        predicted: currentRate,
        lower: currentRate,
        upper: currentRate,
        label: '現在'
      }
    ];

    const periods = {
      '1day': { days: 1, label: '1日後' },
      '1week': { days: 7, label: '1週間後' },
      '2weeks': { days: 14, label: '2週間後' },
      '1month': { days: 30, label: '1ヶ月後' }
    };

    Object.entries(periods).forEach(([key, config]) => {
      if (data.predictions[key as keyof typeof data.predictions]) {
        const pred = data.predictions[key as keyof typeof data.predictions];
        chartPoints.push({
          date: format(addDays(currentDate, config.days), 'MM/dd'),
          predicted: pred.predicted_rate,
          lower: pred.confidence_interval.lower,
          upper: pred.confidence_interval.upper,
          label: config.label
        } as any);
      }
    });

    setChartData(chartPoints);
  };

  // モデルを訓練
  const trainModel = async () => {
    setTraining(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_BASE}/api/ml/train-sync`,
        null,
        {
          params: {
            currency_pair: currencyPair,
            force_retrain: true
          },
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        }
      );
      
      // 訓練後に予測を取得
      await fetchPredictions();
    } catch (err: any) {
      setError('モデルの訓練に失敗しました');
    } finally {
      setTraining(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, [currencyPair]);

  // シグナルの色を取得
  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'strong_buy':
        return 'success';
      case 'buy':
        return 'success';
      case 'strong_sell':
        return 'error';
      case 'sell':
        return 'error';
      default:
        return 'default';
    }
  };

  // シグナルのアイコンを取得
  const getSignalIcon = (signal: string) => {
    if (signal?.includes('buy')) {
      return <TrendingUp fontSize="small" />;
    } else if (signal?.includes('sell')) {
      return <TrendingDown fontSize="small" />;
    }
    return <Remove fontSize="small" />;
  };

  // 変化率の表示色を取得
  const getChangeColor = (change: number) => {
    if (change > 0) return 'success.main';
    if (change < 0) return 'error.main';
    return 'text.secondary';
  };

  if (loading && !predictions) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Psychology sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">AI予測分析</Typography>
          </Box>
          <Skeleton variant="rectangular" height={200} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        {/* ヘッダー */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Psychology sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">AI予測分析</Typography>
            <Chip 
              label="LSTM + XGBoost" 
              size="small" 
              sx={{ ml: 1 }} 
              color="primary"
              variant="outlined"
            />
          </Box>
          <Box>
            <Tooltip title="モデルを再訓練">
              <IconButton 
                onClick={trainModel} 
                disabled={training}
                size="small"
                sx={{ mr: 1 }}
              >
                <ModelTraining />
              </IconButton>
            </Tooltip>
            <Tooltip title="予測を更新">
              <IconButton 
                onClick={fetchPredictions} 
                disabled={loading}
                size="small"
              >
                <RefreshRounded />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {predictions && (
          <>
            {/* 予測サマリー */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              {Object.entries({
                '1day': '1日後',
                '1week': '1週間後',
                '2weeks': '2週間後',
                '1month': '1ヶ月後'
              }).map(([key, label]) => {
                const pred = predictions.predictions[key as keyof typeof predictions.predictions];
                if (!pred) return null;

                return (
                  <Grid item xs={6} md={3} key={key}>
                    <Box
                      sx={{
                        p: 2,
                        border: 1,
                        borderColor: selectedPeriod === key ? 'primary.main' : 'divider',
                        borderRadius: 1,
                        cursor: 'pointer',
                        transition: 'all 0.3s',
                        '&:hover': {
                          borderColor: 'primary.main',
                          bgcolor: 'action.hover'
                        }
                      }}
                      onClick={() => setSelectedPeriod(key)}
                    >
                      <Typography variant="caption" color="text.secondary">
                        {label}
                      </Typography>
                      <Typography variant="h6">
                        ¥{pred.predicted_rate.toFixed(2)}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                        {getSignalIcon(pred.signal)}
                        <Typography
                          variant="body2"
                          sx={{ color: getChangeColor(pred.change_percent), ml: 0.5 }}
                        >
                          {pred.change_percent > 0 ? '+' : ''}
                          {pred.change_percent.toFixed(2)}%
                        </Typography>
                      </Box>
                      <Chip
                        label={pred.signal.replace('_', ' ').toUpperCase()}
                        size="small"
                        color={getSignalColor(pred.signal) as any}
                        sx={{ mt: 1, width: '100%' }}
                      />
                    </Box>
                  </Grid>
                );
              })}
            </Grid>

            {/* 予測チャート */}
            <Box sx={{ height: 300, mb: 2 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="date" 
                    style={{ fontSize: 12 }}
                  />
                  <YAxis 
                    domain={['dataMin - 0.5', 'dataMax + 0.5']}
                    style={{ fontSize: 12 }}
                  />
                  <ChartTooltip
                    formatter={(value: any) => value ? `¥${value.toFixed(2)}` : '-'}
                    labelStyle={{ color: '#000' }}
                  />
                  <Legend />
                  
                  {/* 信頼区間 */}
                  <Area
                    type="monotone"
                    dataKey="upper"
                    stackId="1"
                    stroke="none"
                    fill="#8884d8"
                    fillOpacity={0.2}
                    name="信頼区間上限"
                  />
                  <Area
                    type="monotone"
                    dataKey="lower"
                    stackId="2"
                    stroke="none"
                    fill="#8884d8"
                    fillOpacity={0.2}
                    name="信頼区間下限"
                  />
                  
                  {/* 予測線 */}
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    stroke="#8884d8"
                    strokeWidth={3}
                    dot={{ r: 5 }}
                    name="予測値"
                  />
                  
                  {/* 現在値参照線 */}
                  {predictions && (
                    <ReferenceLine
                      y={predictions.current_rate}
                      stroke="#666"
                      strokeDasharray="5 5"
                      label={{ value: "現在値", position: "left" }}
                    />
                  )}
                </ComposedChart>
              </ResponsiveContainer>
            </Box>

            {/* 選択された期間の詳細 */}
            {selectedPeriod && predictions.predictions[selectedPeriod as keyof typeof predictions.predictions] && (
              <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                  予測詳細（{selectedPeriod === '1day' ? '1日後' : 
                           selectedPeriod === '1week' ? '1週間後' :
                           selectedPeriod === '2weeks' ? '2週間後' : '1ヶ月後'}）
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      予測レート
                    </Typography>
                    <Typography variant="body1">
                      ¥{predictions.predictions[selectedPeriod as keyof typeof predictions.predictions].predicted_rate.toFixed(2)}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="text.secondary">
                      95%信頼区間
                    </Typography>
                    <Typography variant="body1">
                      ¥{predictions.predictions[selectedPeriod as keyof typeof predictions.predictions].confidence_interval.lower.toFixed(2)} 
                      ~ ¥{predictions.predictions[selectedPeriod as keyof typeof predictions.predictions].confidence_interval.upper.toFixed(2)}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            )}
          </>
        )}

        {training && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography>モデルを訓練中...</Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default MLPredictionCard;
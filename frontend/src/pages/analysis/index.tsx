import { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  Checkbox,
  FormControlLabel,
  Paper,
  Chip
} from '@mui/material';
import ReactApexChart from 'react-apexcharts';
import { 
  useHistoricalCharts, 
  useTechnicalIndicators, 
  useEconomicIndicators, 
  useDetailedPredictions,
  useCurrentRate,
  type ChartDataPoint 
} from './hooks/useAnalysisData';

const AnalysisPage = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('6m');
  const [selectedIndicators, setSelectedIndicators] = useState({
    ma: true,
    rsi: true,
    macd: false,
    bb: true,
  });

  // API Queries
  const { data: currentRateData } = useCurrentRate();
  const { data: chartData } = useHistoricalCharts(selectedPeriod);
  const { data: technicalData } = useTechnicalIndicators();
  const { data: economicData } = useEconomicIndicators();
  const { data: predictionData } = useDetailedPredictions();

  // Transform chart data for ApexCharts candlestick format
  const candlestickData = chartData?.data?.map((point: ChartDataPoint) => ({
    x: new Date(point.timestamp),
    y: [point.open, point.high, point.low, point.close]
  })) || [
    // Fallback mock data if API is not available
    { x: new Date('2024-01-01'), y: [148.50, 149.20, 148.30, 149.00] },
    { x: new Date('2024-01-02'), y: [149.00, 149.80, 148.90, 149.70] },
    { x: new Date('2024-01-03'), y: [149.70, 150.20, 149.50, 149.90] },
    { x: new Date('2024-01-04'), y: [149.90, 150.50, 149.60, 150.30] },
    { x: new Date('2024-01-05'), y: [150.30, 150.80, 150.00, 149.75] },
  ];

  const chartOptions = {
    chart: {
      type: 'candlestick' as const,
      height: 350,
      background: 'transparent',
      toolbar: {
        show: true,
        tools: {
          download: true,
          selection: true,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: true,
          reset: true
        }
      }
    },
    title: {
      text: 'USD/JPY キャンドルスティックチャート',
      align: 'left' as const,
      style: {
        color: '#00d4ff'
      }
    },
    xaxis: {
      type: 'datetime' as const,
      labels: {
        style: {
          colors: '#e1e5f0'
        }
      }
    },
    yaxis: {
      tooltip: {
        enabled: true
      },
      labels: {
        style: {
          colors: '#e1e5f0'
        }
      }
    },
    theme: {
      mode: 'dark' as const
    },
    grid: {
      borderColor: '#30363d'
    }
  };

  const periodNames = {
    '3m': '3ヶ月',
    '6m': '6ヶ月',
    '1y': '1年',
    '3y': '3年'
  };

  // Transform technical indicators data
  const technicalIndicators = technicalData?.indicators?.map(indicator => ({
    name: indicator.name,
    value: indicator.current_value.toFixed(2),
    trend: indicator.signal
  })) || [
    // Fallback mock data
    { name: '移動平均 (20日)', value: '149.23', trend: 'bullish' },
    { name: '移動平均 (50日)', value: '148.67', trend: 'bullish' },
    { name: 'RSI (14日)', value: '58.4', trend: 'neutral' },
    { name: 'MACD', value: '+0.23', trend: 'bullish' },
    { name: 'ボリンジャー上限', value: '151.45', trend: 'neutral' },
    { name: 'ボリンジャー下限', value: '147.82', trend: 'neutral' },
  ];

  // Transform economic indicators data
  const economicIndicators = economicData?.indicators?.map(indicator => ({
    name: indicator.name,
    value: `${indicator.change_percent > 0 ? '+' : ''}${indicator.change_percent.toFixed(1)}%`,
    impact: indicator.impact_level,
    color: indicator.impact_level === 'high' ? '#ef4444' : 
           indicator.impact_level === 'medium' ? '#fbbf24' : '#00ff88'
  })) || [
    // Fallback mock data
    { name: '日米金利差', value: '+1.2%', impact: 'high', color: '#ef4444' },
    { name: 'GDP成長率', value: '+0.7%', impact: 'medium', color: '#fbbf24' },
    { name: '雇用統計', value: '+0.3%', impact: 'low', color: '#00ff88' },
    { name: 'インフレ率', value: '-0.5%', impact: 'medium', color: '#fbbf24' },
    { name: '中央銀行政策', value: '+0.9%', impact: 'high', color: '#ef4444' },
  ];

  // Current rate data
  const currentRate = {
    value: currentRateData?.current_rate || 149.75,
    change: currentRateData?.change_24h || 0.38,
    changePercent: currentRateData?.change_percent_24h || 0.25,
    lastUpdate: currentRateData?.timestamp ? 
      new Date(currentRateData.timestamp).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' }) :
      new Date().toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
  };

  // Prediction confidence data
  const predictionConfidence = {
    score: predictionData?.prediction?.confidence_score || 78,
    reasoning: predictionData?.prediction?.reasoning || 
      '日米金利差拡大とテクニカル指標の強気シグナルにより、1週間後150.2円、1ヶ月後151.8円の上昇予測。RSI過熱感は限定的で、ボリンジャーバンド上限突破の可能性が高い。'
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'bullish': return '#00ff88';
      case 'bearish': return '#ef4444';
      case 'neutral': return '#fbbf24';
      default: return '#e1e5f0';
    }
  };

  const getImpactBorderColor = (impact: string) => {
    switch (impact) {
      case 'high': return '#ef4444';
      case 'medium': return '#fbbf24';
      case 'low': return '#00ff88';
      default: return '#30363d';
    }
  };


  return (
    <Box sx={{ 
      minHeight: '100vh',
      backgroundColor: '#0f1419',
      color: '#e1e5f0',
      fontFamily: 'monospace'
    }}>
      {/* Header */}
      <Paper sx={{
        backgroundColor: '#21262d',
        borderBottom: '2px solid #00d4ff',
        borderRadius: 0,
        p: 2,
        mb: 1
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 'bold' }}>
            詳細予測分析
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 'bold' }}>
              {currentRate.value}
            </Typography>
            <Chip 
              label={`${currentRate.change > 0 ? '+' : ''}${currentRate.change} (+${currentRate.changePercent}%)`}
              sx={{ 
                backgroundColor: currentRate.change > 0 ? 'rgba(0, 255, 136, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                color: currentRate.change > 0 ? '#00ff88' : '#ef4444'
              }}
            />
            <Typography variant="body2" sx={{ color: '#9ca3af' }}>
              最終更新: {currentRate.lastUpdate}
            </Typography>
          </Box>
        </Box>
      </Paper>

      <Grid container spacing={1} sx={{ height: 'calc(100vh - 120px)' }}>
        {/* Sidebar */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ 
            backgroundColor: '#21262d',
            border: '1px solid #30363d',
            p: 2,
            height: '100%'
          }}>
            {/* Time Periods */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2, textTransform: 'uppercase' }}>
                表示期間
              </Typography>
              {Object.entries(periodNames).map(([key, label]) => (
                <Button
                  key={key}
                  fullWidth
                  variant={selectedPeriod === key ? 'contained' : 'outlined'}
                  onClick={() => setSelectedPeriod(key)}
                  sx={{
                    mb: 1,
                    backgroundColor: selectedPeriod === key ? '#00d4ff' : '#161b22',
                    color: selectedPeriod === key ? '#1a1f2e' : '#e1e5f0',
                    borderColor: '#30363d',
                    '&:hover': {
                      backgroundColor: selectedPeriod === key ? '#0099cc' : '#262c36',
                      borderColor: '#00d4ff'
                    }
                  }}
                >
                  {label}
                </Button>
              ))}
            </Box>

            {/* Technical Indicators */}
            <Box>
              <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2, textTransform: 'uppercase' }}>
                テクニカル指標
              </Typography>
              {[
                { key: 'ma', label: '移動平均線 (MA)' },
                { key: 'rsi', label: 'RSI' },
                { key: 'macd', label: 'MACD' },
                { key: 'bb', label: 'ボリンジャーバンド' }
              ].map(({ key, label }) => (
                <FormControlLabel
                  key={key}
                  control={
                    <Checkbox
                      checked={selectedIndicators[key as keyof typeof selectedIndicators]}
                      onChange={(e) => setSelectedIndicators(prev => ({
                        ...prev,
                        [key]: e.target.checked
                      }))}
                      sx={{
                        color: '#00d4ff',
                        '&.Mui-checked': {
                          color: '#00d4ff'
                        }
                      }}
                    />
                  }
                  label={<Typography sx={{ fontSize: '0.875rem' }}>{label}</Typography>}
                  sx={{ display: 'block', mb: 1 }}
                />
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Main Content */}
        <Grid item xs={12} md={9}>
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 1 }}>
            {/* Chart Section */}
            <Paper sx={{
              backgroundColor: '#21262d',
              border: '1px solid #30363d',
              borderRadius: 1,
              flex: 1,
              p: 2
            }}>
              <Box sx={{ height: '100%' }}>
                <ReactApexChart
                  options={chartOptions}
                  series={[{ data: candlestickData }]}
                  type="candlestick"
                  height="100%"
                />
              </Box>
            </Paper>

            {/* Bottom Panel */}
            <Grid container spacing={1} sx={{ height: '300px' }}>
              {/* Technical Indicators Panel */}
              <Grid item xs={12} md={4}>
                <Paper sx={{
                  backgroundColor: '#21262d',
                  border: '1px solid #30363d',
                  borderRadius: 1,
                  p: 2,
                  height: '100%'
                }}>
                  <Typography variant="h6" sx={{ 
                    color: '#00d4ff', 
                    mb: 2, 
                    textTransform: 'uppercase',
                    fontSize: '0.875rem'
                  }}>
                    テクニカル指標
                  </Typography>
                  <Box sx={{ maxHeight: '240px', overflowY: 'auto' }}>
                    {technicalIndicators.map((indicator, index) => (
                      <Box key={index} sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        py: 1,
                        borderBottom: '1px solid #30363d'
                      }}>
                        <Typography sx={{ fontSize: '0.75rem', color: '#e1e5f0' }}>
                          {indicator.name}
                        </Typography>
                        <Typography sx={{
                          fontSize: '0.875rem',
                          fontWeight: 'bold',
                          color: getTrendColor(indicator.trend)
                        }}>
                          {indicator.value}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </Paper>
              </Grid>

              {/* Economic Impact Panel */}
              <Grid item xs={12} md={4}>
                <Paper sx={{
                  backgroundColor: '#21262d',
                  border: '1px solid #30363d',
                  borderRadius: 1,
                  p: 2,
                  height: '100%'
                }}>
                  <Typography variant="h6" sx={{ 
                    color: '#00d4ff', 
                    mb: 2, 
                    textTransform: 'uppercase',
                    fontSize: '0.875rem'
                  }}>
                    経済指標影響度
                  </Typography>
                  <Box sx={{ maxHeight: '240px', overflowY: 'auto' }}>
                    {economicIndicators.map((indicator, index) => (
                      <Paper key={index} sx={{
                        backgroundColor: '#161b22',
                        borderLeft: `4px solid ${getImpactBorderColor(indicator.impact)}`,
                        p: 1.5,
                        mb: 1,
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <Typography sx={{ fontSize: '0.75rem', color: '#e1e5f0' }}>
                          {indicator.name}
                        </Typography>
                        <Typography sx={{
                          fontSize: '0.875rem',
                          fontWeight: 'bold',
                          color: indicator.color
                        }}>
                          {indicator.impact === 'high' ? '高影響' : indicator.impact === 'medium' ? '中影響' : '低影響'} {indicator.value}
                        </Typography>
                      </Paper>
                    ))}
                  </Box>
                </Paper>
              </Grid>

              {/* Prediction Confidence Panel */}
              <Grid item xs={12} md={4}>
                <Paper sx={{
                  backgroundColor: '#21262d',
                  border: '1px solid #30363d',
                  borderRadius: 1,
                  p: 2,
                  height: '100%'
                }}>
                  <Typography variant="h6" sx={{ 
                    color: '#00d4ff', 
                    mb: 2, 
                    textTransform: 'uppercase',
                    fontSize: '0.875rem'
                  }}>
                    予測信頼度分析
                  </Typography>
                  
                  {/* Confidence Meter */}
                  <Box sx={{ mb: 3 }}>
                    <Typography sx={{ fontSize: '0.75rem', color: '#e1e5f0', mb: 1 }}>
                      総合信頼度
                    </Typography>
                    <Box sx={{
                      height: 8,
                      backgroundColor: '#161b22',
                      borderRadius: 1,
                      overflow: 'hidden',
                      mb: 1
                    }}>
                      <Box sx={{
                        height: '100%',
                        background: 'linear-gradient(90deg, #ef4444 0%, #fbbf24 50%, #00ff88 100%)',
                        width: `${predictionConfidence.score}%`,
                        borderRadius: 1
                      }} />
                    </Box>
                    <Typography sx={{ fontSize: '0.875rem', fontWeight: 'bold', color: '#00d4ff' }}>
                      {predictionConfidence.score}% ({predictionConfidence.score >= 70 ? '高信頼' : predictionConfidence.score >= 50 ? '中信頼' : '低信頼'})
                    </Typography>
                  </Box>

                  {/* Prediction Summary */}
                  <Paper sx={{
                    backgroundColor: '#161b22',
                    border: '1px solid #30363d',
                    p: 1.5
                  }}>
                    <Typography sx={{ 
                      fontSize: '0.75rem', 
                      color: '#00d4ff',
                      textTransform: 'uppercase',
                      mb: 1
                    }}>
                      予測根拠
                    </Typography>
                    <Typography sx={{ fontSize: '0.75rem', color: '#e1e5f0', lineHeight: 1.4 }}>
                      {predictionConfidence.reasoning}
                    </Typography>
                  </Paper>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalysisPage;
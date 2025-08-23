import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Skeleton,
  Chip,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  GpsFixed as Target,
  Speed,
  Timeline
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface PerformanceMetricsData {
  total_return?: number;
  annualized_return?: number;
  volatility?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_trades?: number;
  winning_trades?: number;
  losing_trades?: number;
  win_rate?: number;
  prediction_accuracy_1w?: number;
  prediction_accuracy_2w?: number;
  prediction_accuracy_3w?: number;
  prediction_accuracy_1m?: number;
  sortino_ratio?: number;
  calmar_ratio?: number;
  var_95?: number;
}

interface PerformanceMetricsProps {
  data?: PerformanceMetricsData;
  isLoading?: boolean;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: 'success' | 'error' | 'warning' | 'info' | 'primary';
  suffix?: string;
  description?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  icon, 
  color = 'primary', 
  suffix = '',
  description 
}) => {
  const theme = useTheme();
  
  const getColorValue = () => {
    switch (color) {
      case 'success':
        return theme.palette.success.main;
      case 'error':
        return theme.palette.error.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'info':
        return theme.palette.info.main;
      default:
        return theme.palette.primary.main;
    }
  };

  const formatValue = (val: string | number): string => {
    if (typeof val === 'number') {
      if (val >= 1000 || val <= -1000) {
        return val.toLocaleString(undefined, { maximumFractionDigits: 0 });
      }
      return val.toFixed(2);
    }
    return val;
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`,
        border: `1px solid ${theme.palette.divider}`,
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[4],
        },
        transition: 'all 0.3s ease'
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Box 
            sx={{ 
              color: getColorValue(),
              mr: 1,
              display: 'flex',
              alignItems: 'center'
            }}
          >
            {icon}
          </Box>
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ 
              fontSize: '0.75rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: 0.5
            }}
          >
            {title}
          </Typography>
        </Box>
        
        <Typography 
          variant="h5" 
          sx={{ 
            color: getColorValue(),
            fontWeight: 700,
            fontFamily: 'monospace',
            mb: description ? 0.5 : 0
          }}
        >
          {formatValue(value)}{suffix}
        </Typography>
        
        {description && (
          <Typography 
            variant="caption" 
            color="text.secondary"
            sx={{ fontSize: '0.7rem' }}
          >
            {description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ 
  data, 
  isLoading = false 
}) => {
  const theme = useTheme();

  // カラー判定のヘルパー関数
  const getReturnColor = (value?: number): 'success' | 'error' | 'primary' => {
    if (value === undefined) return 'primary';
    return value >= 0 ? 'success' : 'error';
  };

  const getRatioColor = (value?: number, threshold = 1): 'success' | 'warning' | 'error' | 'primary' => {
    if (value === undefined) return 'primary';
    if (value >= threshold * 1.5) return 'success';
    if (value >= threshold) return 'warning';
    return 'error';
  };

  const getAccuracyColor = (value?: number): 'success' | 'warning' | 'error' | 'primary' => {
    if (value === undefined) return 'primary';
    if (value >= 70) return 'success';
    if (value >= 50) return 'warning';
    return 'error';
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary" sx={{ mb: 3 }}>
            パフォーマンス指標
          </Typography>
          <Grid container spacing={2}>
            {Array.from({ length: 8 }, (_, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Card>
                  <CardContent sx={{ p: 2 }}>
                    <Skeleton variant="text" width="60%" height={20} />
                    <Skeleton variant="text" width="40%" height={32} />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary" sx={{ mb: 3 }}>
            パフォーマンス指標
          </Typography>
          <Box 
            sx={{ 
              height: 200, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              border: `1px dashed ${theme.palette.divider}`,
              borderRadius: 1,
              backgroundColor: theme.palette.background.default
            }}
          >
            <Typography variant="body2" color="text.secondary">
              バックテストを実行して指標を表示
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Typography variant="h6" color="primary">
            パフォーマンス指標
          </Typography>
          {data.total_trades && (
            <Chip 
              label={`${data.total_trades} 取引`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>

        {/* 基本収益指標 */}
        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 600 }}>
          収益性指標
        </Typography>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="総収益率"
              value={data.total_return ?? '--'}
              suffix="%"
              icon={<TrendingUp fontSize="small" />}
              color={getReturnColor(data.total_return)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="年率リターン"
              value={data.annualized_return ?? '--'}
              suffix="%"
              icon={<Timeline fontSize="small" />}
              color={getReturnColor(data.annualized_return)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="最大ドローダウン"
              value={data.max_drawdown ?? '--'}
              suffix="%"
              icon={<TrendingDown fontSize="small" />}
              color="error"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="ボラティリティ"
              value={data.volatility ?? '--'}
              suffix="%"
              icon={<Speed fontSize="small" />}
              color="info"
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* リスク調整済みリターン */}
        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 600 }}>
          リスク調整済み指標
        </Typography>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="シャープレシオ"
              value={data.sharpe_ratio ?? '--'}
              icon={<Assessment fontSize="small" />}
              color={getRatioColor(data.sharpe_ratio, 1)}
              description="1.0以上が良好"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="ソルティノレシオ"
              value={data.sortino_ratio ?? '--'}
              icon={<Assessment fontSize="small" />}
              color={getRatioColor(data.sortino_ratio, 1.5)}
              description="1.5以上が良好"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="カルマーレシオ"
              value={data.calmar_ratio ?? '--'}
              icon={<Assessment fontSize="small" />}
              color={getRatioColor(data.calmar_ratio, 0.5)}
              description="0.5以上が良好"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="VaR (95%)"
              value={data.var_95 ?? '--'}
              suffix="%"
              icon={<Target fontSize="small" />}
              color="warning"
              description="最大損失予想"
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* 取引統計 */}
        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 600 }}>
          取引統計
        </Typography>
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="勝率"
              value={data.win_rate ?? '--'}
              suffix="%"
              icon={<Target fontSize="small" />}
              color={getAccuracyColor(data.win_rate)}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="勝ちトレード"
              value={data.winning_trades ?? '--'}
              icon={<TrendingUp fontSize="small" />}
              color="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="負けトレード"
              value={data.losing_trades ?? '--'}
              icon={<TrendingDown fontSize="small" />}
              color="error"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="総取引数"
              value={data.total_trades ?? '--'}
              icon={<Assessment fontSize="small" />}
              color="info"
            />
          </Grid>
        </Grid>

        {/* 予測精度（データがある場合のみ表示） */}
        {(data.prediction_accuracy_1w || data.prediction_accuracy_2w || 
          data.prediction_accuracy_3w || data.prediction_accuracy_1m) && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2, fontWeight: 600 }}>
              予測精度
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="1週間予測精度"
                  value={data.prediction_accuracy_1w ?? '--'}
                  suffix="%"
                  icon={<Target fontSize="small" />}
                  color={getAccuracyColor(data.prediction_accuracy_1w)}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="2週間予測精度"
                  value={data.prediction_accuracy_2w ?? '--'}
                  suffix="%"
                  icon={<Target fontSize="small" />}
                  color={getAccuracyColor(data.prediction_accuracy_2w)}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="3週間予測精度"
                  value={data.prediction_accuracy_3w ?? '--'}
                  suffix="%"
                  icon={<Target fontSize="small" />}
                  color={getAccuracyColor(data.prediction_accuracy_3w)}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <MetricCard
                  title="1ヶ月予測精度"
                  value={data.prediction_accuracy_1m ?? '--'}
                  suffix="%"
                  icon={<Target fontSize="small" />}
                  color={getAccuracyColor(data.prediction_accuracy_1m)}
                />
              </Grid>
            </Grid>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default PerformanceMetrics;
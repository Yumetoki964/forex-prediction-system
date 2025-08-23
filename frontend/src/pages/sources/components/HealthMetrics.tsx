import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import {
  Speed,
  Visibility,
  Refresh,
  TrendingUp,
  ErrorOutline,
  CheckCircle,
} from '@mui/icons-material';
import { HealthMetrics as HealthMetricsType, useRunHealthCheck } from '../hooks/useSourcesData';

interface HealthMetricsProps {
  metrics: HealthMetricsType | undefined;
  isLoading?: boolean;
}

const HealthMetrics: React.FC<HealthMetricsProps> = ({ metrics, isLoading }) => {
  const runHealthCheckMutation = useRunHealthCheck();

  const formatResponseTime = (time: number) => {
    if (time < 1000) return `${time}ms`;
    return `${(time / 1000).toFixed(1)}s`;
  };

  const getHealthColor = (value: number, type: 'response_time' | 'availability' | 'error_rate') => {
    switch (type) {
      case 'response_time':
        if (value < 500) return 'success';
        if (value < 1000) return 'warning';
        return 'error';
      case 'availability':
        if (value >= 99) return 'success';
        if (value >= 95) return 'warning';
        return 'error';
      case 'error_rate':
        if (value < 1) return 'success';
        if (value < 5) return 'warning';
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (color: string) => {
    switch (color) {
      case 'success':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'warning':
        return <ErrorOutline sx={{ color: 'warning.main' }} />;
      case 'error':
        return <ErrorOutline sx={{ color: 'error.main' }} />;
      default:
        return <CheckCircle sx={{ color: 'text.secondary' }} />;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" color="primary">
              ヘルスチェック結果
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            ヘルスメトリクスを読み込み中...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!metrics) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6" color="primary">
              ヘルスチェック結果
            </Typography>
            <Button
              variant="outlined"
              size="small"
              startIcon={<Refresh />}
              onClick={() => runHealthCheckMutation.mutate()}
              disabled={runHealthCheckMutation.isPending}
            >
              チェック実行
            </Button>
          </Box>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            ヘルスチェックを実行してデータソースの状態を確認してください。
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const responseTimeColor = getHealthColor(metrics.response_time, 'response_time');
  const availabilityColor = getHealthColor(metrics.availability, 'availability');
  const errorRateColor = getHealthColor(metrics.error_rate, 'error_rate');

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" color="primary">
            ヘルスチェック結果
          </Typography>
          {runHealthCheckMutation.isPending ? (
            <Chip
              label="実行中"
              color="info"
              size="small"
              icon={<CircularProgress size={16} />}
            />
          ) : (
            <Button
              variant="outlined"
              size="small"
              startIcon={<Refresh />}
              onClick={() => runHealthCheckMutation.mutate()}
            >
              再チェック
            </Button>
          )}
        </Box>

        {runHealthCheckMutation.isPending && (
          <LinearProgress sx={{ mb: 3 }} />
        )}

        <Grid container spacing={2}>
          {/* 平均応答時間 */}
          <Grid item xs={12} sm={6}>
            <Box sx={{ 
              p: 2, 
              border: 1, 
              borderColor: `${responseTimeColor}.main`,
              borderRadius: 2,
              bgcolor: `${responseTimeColor}.light`,
              opacity: 0.1,
              position: 'relative'
            }}>
              <Box sx={{ 
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                bgcolor: 'background.paper',
                borderRadius: 2,
                p: 2
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Speed sx={{ mr: 1, color: `${responseTimeColor}.main` }} />
                  <Typography variant="body2" color="text.secondary">
                    平均応答時間
                  </Typography>
                </Box>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    fontFamily: 'monospace',
                    fontWeight: 'bold',
                    color: `${responseTimeColor}.main`
                  }}
                >
                  {formatResponseTime(metrics.response_time)}
                </Typography>
                {getStatusIcon(responseTimeColor)}
              </Box>
            </Box>
          </Grid>

          {/* 全体可用性 */}
          <Grid item xs={12} sm={6}>
            <Box sx={{ 
              p: 2, 
              border: 1, 
              borderColor: `${availabilityColor}.main`,
              borderRadius: 2,
              bgcolor: `${availabilityColor}.light`,
              opacity: 0.1,
              position: 'relative'
            }}>
              <Box sx={{ 
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                bgcolor: 'background.paper',
                borderRadius: 2,
                p: 2
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Visibility sx={{ mr: 1, color: `${availabilityColor}.main` }} />
                  <Typography variant="body2" color="text.secondary">
                    全体可用性
                  </Typography>
                </Box>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    fontFamily: 'monospace',
                    fontWeight: 'bold',
                    color: `${availabilityColor}.main`
                  }}
                >
                  {metrics.availability}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={metrics.availability}
                  sx={{
                    mt: 1,
                    height: 4,
                    borderRadius: 2,
                    '& .MuiLinearProgress-bar': {
                      bgcolor: `${availabilityColor}.main`
                    }
                  }}
                />
                {getStatusIcon(availabilityColor)}
              </Box>
            </Box>
          </Grid>

          {/* データ新鮮度 */}
          <Grid item xs={12} sm={6}>
            <Box sx={{ 
              p: 2, 
              border: 1, 
              borderColor: 'success.main',
              borderRadius: 2,
              bgcolor: 'background.paper'
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="body2" color="text.secondary">
                  データ新鮮度
                </Typography>
              </Box>
              <Typography 
                variant="h5" 
                sx={{ 
                  fontFamily: 'monospace',
                  fontWeight: 'bold',
                  color: 'success.main'
                }}
              >
                {metrics.data_freshness}
              </Typography>
              {getStatusIcon('success')}
            </Box>
          </Grid>

          {/* エラー率 */}
          <Grid item xs={12} sm={6}>
            <Box sx={{ 
              p: 2, 
              border: 1, 
              borderColor: `${errorRateColor}.main`,
              borderRadius: 2,
              bgcolor: `${errorRateColor}.light`,
              opacity: 0.1,
              position: 'relative'
            }}>
              <Box sx={{ 
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                bgcolor: 'background.paper',
                borderRadius: 2,
                p: 2
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ErrorOutline sx={{ mr: 1, color: `${errorRateColor}.main` }} />
                  <Typography variant="body2" color="text.secondary">
                    エラー率
                  </Typography>
                </Box>
                <Typography 
                  variant="h5" 
                  sx={{ 
                    fontFamily: 'monospace',
                    fontWeight: 'bold',
                    color: `${errorRateColor}.main`
                  }}
                >
                  {metrics.error_rate}%
                </Typography>
                {getStatusIcon(errorRateColor)}
              </Box>
            </Box>
          </Grid>
        </Grid>

        {/* 最終チェック時刻 */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            最終チェック: {metrics.last_check}
          </Typography>
        </Box>

        {/* 詳細診断ボタン */}
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
          <Button
            variant="outlined"
            color="warning"
            startIcon={<Speed />}
            disabled
          >
            詳細診断 (実装予定)
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default HealthMetrics;
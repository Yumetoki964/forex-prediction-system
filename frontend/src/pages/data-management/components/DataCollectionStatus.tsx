import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Box,
  Chip,
  Alert,
  Skeleton,
} from '@mui/material';
import { useDataStatus } from '../hooks/useDataManagement';

const DataCollectionStatus: React.FC = () => {
  const { data: status, isLoading, error } = useDataStatus();

  if (isLoading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3].map((item) => (
          <Grid item xs={12} md={4} key={item}>
            <Card>
              <CardContent>
                <Skeleton variant="text" height={24} />
                <Skeleton variant="text" height={40} sx={{ my: 1 }} />
                <Skeleton variant="rectangular" height={8} sx={{ mb: 1 }} />
                <Skeleton variant="text" height={20} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        データ収集状況の取得に失敗しました: {error.message}
      </Alert>
    );
  }

  if (!status) {
    return null;
  }

  const getHealthColor = (health: string): 'success' | 'warning' | 'error' | 'info' => {
    switch (health) {
      case 'healthy':
      case 'normal':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
      case 'critical':
        return 'error';
      default:
        return 'info';
    }
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Grid container spacing={3}>
      {/* データカバー率 */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography
                variant="overline"
                sx={{
                  color: 'primary.main',
                  fontWeight: 600,
                  letterSpacing: 1,
                }}
              >
                📊 データカバー率
              </Typography>
            </Box>
            <Typography
              variant="h4"
              sx={{
                fontFamily: 'monospace',
                fontWeight: 'bold',
                mb: 2,
              }}
            >
              {formatPercentage(status.coverage.coverage_rate)}
            </Typography>
            <LinearProgress
              variant="determinate"
              value={status.coverage.coverage_rate * 100}
              sx={{
                height: 8,
                borderRadius: 4,
                mb: 2,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 4,
                  background: 'linear-gradient(90deg, #00d4ff, #33ddff)',
                },
              }}
            />
            <Typography variant="body2" color="text.secondary">
              {status.coverage.earliest_date}〜現在
            </Typography>
            <Typography variant="body2" color="text.secondary">
              ({status.coverage.actual_data_days.toLocaleString()}日中
              {status.coverage.missing_days.toLocaleString()}日欠損)
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* 最終更新日時 */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography
                variant="overline"
                sx={{
                  color: 'primary.main',
                  fontWeight: 600,
                  letterSpacing: 1,
                }}
              >
                🕐 最終更新日時
              </Typography>
            </Box>
            <Typography
              variant="h5"
              sx={{
                fontFamily: 'monospace',
                fontWeight: 'bold',
                mb: 2,
              }}
            >
              {formatDate(status.coverage.last_update)}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {status.schedule.collection_frequency === 'daily' ? '毎日' : '定期'} 自動更新
            </Typography>
            <Chip
              size="small"
              label={status.schedule.auto_collection_enabled ? '自動収集有効' : '自動収集無効'}
              color={status.schedule.auto_collection_enabled ? 'success' : 'warning'}
              icon={<span>{status.schedule.auto_collection_enabled ? '✅' : '⚠️'}</span>}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* 次回更新予定 */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography
                variant="overline"
                sx={{
                  color: 'primary.main',
                  fontWeight: 600,
                  letterSpacing: 1,
                }}
              >
                ⏰ 次回更新予定
              </Typography>
            </Box>
            <Typography
              variant="h5"
              sx={{
                fontFamily: 'monospace',
                fontWeight: 'bold',
                mb: 2,
              }}
            >
              {formatDate(status.schedule.next_collection_time)}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              連続失敗回数: {status.schedule.consecutive_failures}回
            </Typography>
            <Chip
              size="small"
              label="スケジュール済み"
              color="success"
              icon={<span>📅</span>}
            />
          </CardContent>
        </Card>
      </Grid>

      {/* システム健全性とアラート */}
      {(status.system_health !== 'normal' || status.active_issues.length > 0) && (
        <Grid item xs={12}>
          <Alert
            severity={getHealthColor(status.system_health)}
            sx={{ mt: 2 }}
          >
            <Typography variant="h6" sx={{ mb: 1 }}>
              システム状態: {status.system_health}
            </Typography>
            {status.active_issues.length > 0 && (
              <Box>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  アクティブな問題:
                </Typography>
                {status.active_issues.map((issue, index) => (
                  <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                    • {issue}
                  </Typography>
                ))}
              </Box>
            )}
          </Alert>
        </Grid>
      )}
    </Grid>
  );
};

export default DataCollectionStatus;
import React from 'react';
import { Box, Typography, Grid, Alert, AlertTitle, IconButton, Tooltip } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { useDashboardData } from './hooks/useDashboardData';
import { useRealtimeUpdates } from './hooks/useRealtimeUpdates';
import { CurrentRateCard } from './components/CurrentRateCard';
import { PredictionsCard } from './components/PredictionsCard';
import { SignalCard } from './components/SignalCard';
import { RiskMetricsCard } from './components/RiskMetricsCard';
import { ModelInfoCard } from './components/ModelInfoCard';
import { AlertsSection } from './components/AlertsSection';

const DashboardPage: React.FC = () => {
  const dashboardData = useDashboardData();
  const { isConnected, reconnectAttempts, maxReconnectAttempts } = useRealtimeUpdates();

  const {
    currentRate,
    predictions,
    signal,
    riskMetrics,
    alerts,
    hasError,
    errors,
    refetch,
  } = dashboardData;

  const getLatestUpdateTime = () => {
    const times = [
      currentRate.dataUpdatedAt,
      predictions.dataUpdatedAt,
      signal.dataUpdatedAt,
      riskMetrics.dataUpdatedAt,
      alerts.dataUpdatedAt,
    ].filter(Boolean);
    
    if (times.length === 0) return new Date();
    return new Date(Math.max(...times));
  };

  return (
    <Box>
      {/* ページヘッダー */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold' }}>
            📊 予測ダッシュボード
          </Typography>
          <Tooltip title="データを手動更新">
            <IconButton onClick={refetch} color="primary" size="large">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
          <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                backgroundColor: isConnected ? 'success.main' : 'warning.main',
                borderRadius: '50%',
                animation: isConnected ? 'pulse 2s ease-in-out infinite' : 'none',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.7 },
                },
              }}
            />
            最終更新: {getLatestUpdateTime().toLocaleString('ja-JP')} JST
          </Typography>
          
          {!isConnected && (
            <Typography variant="caption" color="warning.main">
              リアルタイム更新: 切断中 ({reconnectAttempts}/{maxReconnectAttempts})
            </Typography>
          )}
        </Box>
        
        {hasError && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            <AlertTitle>一部データの取得に失敗しました</AlertTitle>
            データ取得中にエラーが発生しましたが、利用可能な情報を表示しています。
          </Alert>
        )}
      </Box>

      {/* 現在レートセクション */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <CurrentRateCard
            data={currentRate.data}
            loading={currentRate.isLoading}
            error={errors.currentRate}
          />
        </Grid>
      </Grid>

      {/* 予測・シグナルセクション */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* 予測セクション */}
        <Grid item xs={12} lg={8}>
          <PredictionsCard
            data={predictions.data}
            loading={predictions.isLoading}
            error={errors.predictions}
          />
        </Grid>

        {/* シグナルセクション */}
        <Grid item xs={12} lg={4}>
          <SignalCard
            data={signal.data}
            loading={signal.isLoading}
            error={errors.signal}
          />
        </Grid>
      </Grid>

      {/* リスク指標とモデル情報 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <RiskMetricsCard
            data={riskMetrics.data}
            loading={riskMetrics.isLoading}
            error={errors.riskMetrics}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <ModelInfoCard
            data={{
              ensemble_composition: { lstm: 0.6, xgboost: 0.4 },
              training_period: '過去3年間',
              backtest_accuracy_1w: 68.5,
              backtest_accuracy_2w: 65.2,
              model_version: predictions.data?.model_version || 'v2.1.0',
              last_training_date: '2024-08-20',
              data_points_used: 8750,
            }}
            loading={predictions.isLoading}
            error={errors.predictions}
          />
        </Grid>
      </Grid>

      {/* アラートセクション */}
      <AlertsSection
        alerts={alerts.data}
        loading={alerts.isLoading}
        error={errors.alerts}
      />
    </Box>
  );
};

export default DashboardPage;
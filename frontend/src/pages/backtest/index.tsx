import { useState } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Alert,
  Snackbar
} from '@mui/material';
import BacktestForm, { BacktestFormData } from './components/BacktestForm';
import ProfitChart from './components/ProfitChart';
import PerformanceMetrics from './components/PerformanceMetrics';
import TradeHistoryTable from './components/TradeHistoryTable';
import { useBacktest } from './hooks/useBacktest';

const BacktestPage = () => {
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });

  const {
    currentJobId,
    isRunning,
    results,
    metrics,
    trades,
    progress,
    currentStep,
    executeBacktest,
    cancelBacktest,
    executionError,
    resultsError,
    metricsError,
    tradesError
  } = useBacktest();

  // バックテスト実行ハンドラー
  const handleBacktestSubmit = async (formData: BacktestFormData) => {
    try {
      const job = await executeBacktest(formData);
      setNotification({
        open: true,
        message: `バックテストが開始されました (Job ID: ${job.job_id})`,
        severity: 'success'
      });
    } catch (error: any) {
      setNotification({
        open: true,
        message: `バックテスト開始に失敗しました: ${error.message}`,
        severity: 'error'
      });
    }
  };

  // キャンセルハンドラー
  const handleCancel = () => {
    cancelBacktest();
    setNotification({
      open: true,
      message: 'バックテストをキャンセルしました',
      severity: 'info'
    });
  };

  // 取引履歴のページング
  const handleTradesPageChange = (page: number, pageSize: number) => {
    // 実際の実装では、API呼び出しを再実行する
    console.log(`Page: ${page}, PageSize: ${pageSize}`);
  };

  // 収益曲線データの準備
  const profitChartData = results ? {
    dates: [], // 実際のAPIからのデータが必要
    profitCurve: [], // 実際のAPIからのデータが必要
    drawdownCurve: [] // オプション
  } : undefined;

  // 通知を閉じる
  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  // バックテスト完了の状態判定
  const getBacktestStatus = () => {
    if (isRunning) return 'running';
    if ((results as any)?.status === 'completed') return 'completed';
    if ((results as any)?.status === 'failed') return 'failed';
    return 'idle';
  };

  return (
    <Box>
      {/* ページヘッダー */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ mb: 1, fontWeight: 'bold' }}>
          🔍 バックテスト検証
        </Typography>
        <Typography variant="body2" color="text.secondary">
          過去データを使用した予測精度検証とリターン分析
        </Typography>
        {currentStep && (
          <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
            現在のステップ: {currentStep}
          </Typography>
        )}
      </Box>

      {/* エラーメッセージ表示 */}
      {(executionError || resultsError || metricsError || tradesError) && (
        <Alert severity="error" sx={{ mb: 3 }}>
          エラーが発生しました: {
            executionError?.message || 
            resultsError?.message || 
            metricsError?.message || 
            tradesError?.message
          }
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* 左側: バックテスト設定フォーム */}
        <Grid item xs={12} lg={4}>
          <BacktestForm
            onSubmit={handleBacktestSubmit}
            isRunning={isRunning}
            progress={progress}
            status={getBacktestStatus()}
            onCancel={handleCancel}
          />
        </Grid>

        {/* 右側: 結果表示エリア */}
        <Grid item xs={12} lg={8}>
          {/* 収益曲線グラフ */}
          <Box sx={{ mb: 3 }}>
            <ProfitChart
              data={profitChartData}
              isLoading={isRunning}
              height={360}
            />
          </Box>
        </Grid>

        {/* 下部: パフォーマンス指標と取引履歴 */}
        <Grid item xs={12}>
          <Box sx={{ mb: 3 }}>
            <PerformanceMetrics
              data={metrics}
              isLoading={isRunning && !metrics}
            />
          </Box>
        </Grid>

        <Grid item xs={12}>
          <TradeHistoryTable
            data={trades}
            isLoading={isRunning && !trades}
            onPageChange={handleTradesPageChange}
          />
        </Grid>
      </Grid>

      {/* 成功・エラー通知 */}
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={handleCloseNotification} 
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>

      {/* デバッグ情報 (開発時のみ) */}
      {process.env.NODE_ENV === 'development' && currentJobId && (
        <Box sx={{ mt: 4, p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Debug Info - Job ID: {currentJobId} | Status: {(results as any)?.status} | Progress: {progress}%
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default BacktestPage;
import { useState } from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';
import PredictionSettingsForm, { PredictionSettings } from './components/PredictionSettingsForm';
import AlertSettingsForm, { AlertSettings } from './components/AlertSettingsForm';
import NotificationSnackbar from './components/NotificationSnackbar';
import { 
  usePredictionSettings, 
  usePredictionSettingsUpdate,
  useAlertSettings,
  useAlertSettingsUpdate,
  useSettingsTest,
  SettingsTestResult
} from './hooks/useSettings';
import { useNotification } from './hooks/useNotification';

interface TestResults {
  prediction_accuracy: number;
  confidence_score: number;
}

const SettingsPage = () => {
  const [testResults, setTestResults] = useState<TestResults | null>(null);
  const { notifications, showNotification, removeNotification } = useNotification();

  // 予測設定関連
  const { data: predictionSettings, isLoading: isPredictionLoading } = usePredictionSettings();
  const predictionUpdateMutation = usePredictionSettingsUpdate();
  const settingsTestMutation = useSettingsTest();

  // アラート設定関連
  const { data: alertSettings, isLoading: isAlertLoading } = useAlertSettings();
  const alertUpdateMutation = useAlertSettingsUpdate();

  const handlePredictionSave = async (settings: PredictionSettings) => {
    try {
      await predictionUpdateMutation.mutateAsync(settings);
      showNotification('success', '設定保存完了', '予測設定が正常に保存されました');
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '予測設定の保存に失敗しました';
      showNotification('error', '設定保存エラー', errorMessage);
    }
  };

  const handlePredictionTest = async (settings: PredictionSettings) => {
    try {
      const result: SettingsTestResult = await settingsTestMutation.mutateAsync(settings);
      setTestResults(result.test_results);
      showNotification('success', 'テスト実行完了', `予測精度: ${result.test_results.prediction_accuracy.toFixed(1)}%`);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '設定テストの実行に失敗しました';
      showNotification('error', 'テスト実行エラー', errorMessage);
    }
  };

  const handleAlertSave = async (settings: AlertSettings) => {
    try {
      await alertUpdateMutation.mutateAsync(settings);
      showNotification('success', 'アラート設定保存完了', 'アラート設定が正常に保存されました');
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'アラート設定の保存に失敗しました';
      showNotification('error', 'アラート設定エラー', errorMessage);
    }
  };

  return (
    <Box>
      {/* 通知システム */}
      <NotificationSnackbar 
        notifications={notifications}
        onClose={removeNotification}
      />

      {/* ページヘッダー */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ mb: 1, fontWeight: 'bold' }}>
          ⚙️ 予測設定
        </Typography>
        <Typography variant="body2" color="text.secondary">
          予測モデルのパラメーター調整とアラート設定を管理
        </Typography>
      </Box>

      {/* 予測設定フォーム */}
      <Box sx={{ mb: 4 }}>
        <PredictionSettingsForm 
          settings={predictionSettings || null}
          isLoading={isPredictionLoading}
          onSave={handlePredictionSave}
          onTest={handlePredictionTest}
          isTestingSettings={settingsTestMutation.isPending}
          testResults={testResults}
        />
      </Box>

      {/* アラート設定フォーム */}
      <Box sx={{ mb: 4 }}>
        <AlertSettingsForm 
          settings={alertSettings || null}
          isLoading={isAlertLoading}
          onSave={handleAlertSave}
        />
      </Box>

      {/* 現在の設定状況 */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2 }}>
            現在の設定状況
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">モデル構成</Typography>
              <Typography variant="body1">
                {predictionSettings 
                  ? `LSTM ${Math.round(predictionSettings.model_weights.lstm * 100)}% + XGBoost ${Math.round(predictionSettings.model_weights.xgboost * 100)}%`
                  : 'LSTM 60% + XGBoost 40% (デフォルト)'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">予測感度</Typography>
              <Typography variant="body1">
                {predictionSettings 
                  ? predictionSettings.sensitivity === 'conservative' ? '保守的予測'
                    : predictionSettings.sensitivity === 'aggressive' ? '積極的予測'
                    : '標準予測'
                  : '標準予測 (デフォルト)'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">アラート通知</Typography>
              <Typography variant="body1">
                {alertSettings 
                  ? `メール: ${alertSettings.email_notifications ? 'ON' : 'OFF'}, ブラウザ: ${alertSettings.browser_notifications ? 'ON' : 'OFF'}`
                  : '取得中...'}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">アラート条件数</Typography>
              <Typography variant="body1">
                {alertSettings ? `${alertSettings.conditions.length}件設定済み` : '取得中...'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* API エンドポイント情報 */}
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2 }}>
            使用APIエンドポイント
          </Typography>
          <Box component="pre" sx={{ 
            backgroundColor: 'background.default',
            p: 2,
            borderRadius: 1,
            overflow: 'auto',
            fontSize: '0.875rem',
            fontFamily: 'monospace'
          }}>
{`GET  /api/settings/prediction   - 現在の予測設定を取得
PUT  /api/settings/prediction   - 予測設定を更新
GET  /api/settings/alerts       - アラート設定を取得
PUT  /api/settings/alerts       - アラート設定を更新
POST /api/settings/test         - 予測設定テスト実行`}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SettingsPage;
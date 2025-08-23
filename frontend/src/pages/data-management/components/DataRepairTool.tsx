import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Alert,
  CircularProgress,
  Snackbar,
  Chip,
} from '@mui/material';
import { useDataRepair, useDataQuality } from '../hooks/useDataManagement';
import type { DataRepairRequest } from '../hooks/useDataManagement';

const DataRepairTool: React.FC = () => {
  const [method, setMethod] = useState<DataRepairRequest['method']>('linear');
  const [period, setPeriod] = useState<DataRepairRequest['period']>('all');
  const [previewOpen, setPreviewOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [progressOpen, setProgressOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('success');
  const [repairId, setRepairId] = useState<string>('');
  const [progress, setProgress] = useState(0);

  const repairMutation = useDataRepair();
  const { data: qualityReport } = useDataQuality();

  const getMissingDaysCount = () => {
    if (!qualityReport) return 0;
    return Math.round((1 - qualityReport.quality_metrics.completeness_rate) * 8750); // 概算
  };

  const getMethodDescription = (selectedMethod: string) => {
    switch (selectedMethod) {
      case 'linear':
        return '線形補間: 前後のデータポイントを直線で結んで補完します';
      case 'spline':
        return 'スプライン補間: なめらかな曲線で補完します（より自然な補間）';
      case 'moving-average':
        return '移動平均: 前後の値の平均を使って補完します';
      default:
        return '';
    }
  };

  const getPeriodDescription = (selectedPeriod: string) => {
    switch (selectedPeriod) {
      case 'all':
        return `全期間 (約${getMissingDaysCount()}日の欠損データ)`;
      case 'recent':
        return '最近30日間の欠損データ';
      case 'custom':
        return 'カスタム期間 (開発中)';
      default:
        return '';
    }
  };

  const handlePreview = () => {
    setPreviewOpen(true);
    // 実際の実装では、プレビューAPIを呼び出し
    setSnackbarMessage('修復プレビュー機能は開発中です');
    setSnackbarSeverity('info');
    setSnackbarOpen(true);
  };

  const handleRepairStart = () => {
    setConfirmOpen(true);
  };

  const handleConfirmRepair = async () => {
    setConfirmOpen(false);
    setProgressOpen(true);
    setProgress(0);

    try {
      const response = await repairMutation.mutateAsync({
        method,
        period,
      });

      setRepairId(response.repair_id);
      
      // プログレスバーをシミュレート（実際の実装では WebSocket やポーリングを使用）
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            // 修復完了をシミュレート
            setTimeout(() => {
              setProgressOpen(false);
              setSnackbarMessage(`データ修復が完了しました (${response.affected_days}日分修復)`);
              setSnackbarSeverity('success');
              setSnackbarOpen(true);
            }, 2000);
            return 100;
          }
          return prev + Math.random() * 5;
        });
      }, 1000);

    } catch (error) {
      setProgressOpen(false);
      setSnackbarMessage(`データ修復に失敗しました: ${error instanceof Error ? error.message : '不明なエラー'}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleCancelConfirm = () => {
    setConfirmOpen(false);
  };

  const handleClosePreview = () => {
    setPreviewOpen(false);
  };

  const handleCloseProgress = () => {
    setProgressOpen(false);
    setProgress(0);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const missingDays = getMissingDaysCount();

  return (
    <>
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
            🔧 データ修復ツール（欠損補完）
          </Typography>

          {missingDays > 0 && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <span>⚠️</span>
                <Typography variant="body2">
                  {missingDays}日分の欠損データが検出されています。
                  自動修復を実行して補完できます。
                </Typography>
              </Box>
            </Alert>
          )}

          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="repair-method-label">修復方法</InputLabel>
                <Select
                  labelId="repair-method-label"
                  value={method}
                  label="修復方法"
                  onChange={(e) => setMethod(e.target.value as DataRepairRequest['method'])}
                >
                  <MenuItem value="linear">線形補間</MenuItem>
                  <MenuItem value="spline">スプライン補間</MenuItem>
                  <MenuItem value="moving-average">移動平均</MenuItem>
                </Select>
              </FormControl>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                {getMethodDescription(method)}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="repair-period-label">修復対象期間</InputLabel>
                <Select
                  labelId="repair-period-label"
                  value={period}
                  label="修復対象期間"
                  onChange={(e) => setPeriod(e.target.value as DataRepairRequest['period'])}
                >
                  <MenuItem value="all">全期間</MenuItem>
                  <MenuItem value="recent">最近30日間</MenuItem>
                  <MenuItem value="custom" disabled>カスタム期間（開発中）</MenuItem>
                </Select>
              </FormControl>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                {getPeriodDescription(period)}
              </Typography>
            </Grid>
          </Grid>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <Button
              variant="contained"
              startIcon={repairMutation.isPending ? <CircularProgress size={20} /> : <span>🔧</span>}
              onClick={handleRepairStart}
              disabled={repairMutation.isPending || missingDays === 0}
              sx={{
                background: 'linear-gradient(135deg, #00d4ff, #0099cc)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #33ddff, #00d4ff)',
                },
              }}
            >
              {repairMutation.isPending ? 'データ修復実行中...' : 'データ修復を実行'}
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<span>👁️</span>}
              onClick={handlePreview}
              disabled={missingDays === 0}
            >
              修復プレビュー
            </Button>

            {missingDays === 0 && (
              <Chip
                icon={<span>✅</span>}
                label="修復不要（欠損データなし）"
                color="success"
                variant="outlined"
              />
            )}
          </Box>

          {missingDays > 0 && (
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2">
                修復処理は大量データを扱うため、完了まで数分から数十分かかる場合があります。
                実行中はブラウザを閉じないでください。
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* プレビューダイアログ */}
      <Dialog
        open={previewOpen}
        onClose={handleClosePreview}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          修復プレビュー - {getMethodDescription(method)}
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            修復プレビュー機能は開発中です。実装後は以下の情報が表示されます：
          </Alert>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>予想される修復結果:</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">修復対象期間:</Typography>
                <Typography variant="body1">{getPeriodDescription(period)}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">修復方法:</Typography>
                <Typography variant="body1">{method}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">推定実行時間:</Typography>
                <Typography variant="body1">5-15分</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">修復予定データ数:</Typography>
                <Typography variant="body1">{missingDays}件</Typography>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePreview}>
            閉じる
          </Button>
        </DialogActions>
      </Dialog>

      {/* 確認ダイアログ */}
      <Dialog
        open={confirmOpen}
        onClose={handleCancelConfirm}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          データ修復実行の確認
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            以下の設定でデータ修復を実行しますか？
          </Typography>
          
          <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, mb: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">修復方法:</Typography>
                <Typography variant="body1" fontWeight="bold">{method}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">対象期間:</Typography>
                <Typography variant="body1" fontWeight="bold">{period}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">修復データ数:</Typography>
                <Typography variant="body1" fontWeight="bold">{missingDays}日分</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">推定時間:</Typography>
                <Typography variant="body1" fontWeight="bold">5-15分</Typography>
              </Grid>
            </Grid>
          </Box>

          <Alert severity="warning" sx={{ mb: 2 }}>
            修復処理は元に戻せません。実行前に必ず設定内容をご確認ください。
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelConfirm} color="inherit">
            キャンセル
          </Button>
          <Button
            onClick={handleConfirmRepair}
            variant="contained"
            color="primary"
          >
            実行する
          </Button>
        </DialogActions>
      </Dialog>

      {/* プログレスダイアログ */}
      <Dialog
        open={progressOpen}
        onClose={undefined}
        maxWidth="sm"
        fullWidth
        disableEscapeKeyDown
      >
        <DialogTitle>
          データ修復実行中
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CircularProgress size={24} sx={{ mr: 2 }} />
              <Typography variant="body1">
                {method}による修復処理を実行中...
              </Typography>
            </Box>
            
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 8,
                borderRadius: 4,
                mb: 2,
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #00d4ff, #33ddff)',
                },
              }}
            />
            
            <Typography variant="body2" color="text.secondary" align="center">
              進行状況: {Math.round(progress)}%
            </Typography>
            
            {repairId && (
              <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 1 }}>
                修復ID: {repairId}
              </Typography>
            )}
          </Box>

          <Alert severity="warning">
            修復中はこのダイアログを閉じずにお待ちください。処理中断により、データの整合性が損なわれる可能性があります。
          </Alert>
        </DialogContent>
        {progress >= 100 && (
          <DialogActions>
            <Button onClick={handleCloseProgress} variant="contained">
              完了
            </Button>
          </DialogActions>
        )}
      </Dialog>

      {/* スナックバー通知 */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={handleSnackbarClose}
          severity={snackbarSeverity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </>
  );
};

export default DataRepairTool;
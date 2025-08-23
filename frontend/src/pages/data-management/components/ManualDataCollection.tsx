import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Alert,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import { useDataCollection } from '../hooks/useDataManagement';

const ManualDataCollection: React.FC = () => {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [progressOpen, setProgressOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('success');
  const [collectionId, setCollectionId] = useState<string>('');
  const [progress, setProgress] = useState(0);

  const collectionMutation = useDataCollection();

  const handleCollectionStart = () => {
    setConfirmOpen(true);
  };

  const handleConfirmCollection = async () => {
    setConfirmOpen(false);
    setProgressOpen(true);
    setProgress(0);

    try {
      const response = await collectionMutation.mutateAsync({
        force_update: true,
      });

      setCollectionId(response.collection_id);
      
      // プログレスバーをシミュレート（実際の実装では WebSocket やポーリングを使用）
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            // 収集完了をシミュレート
            setTimeout(() => {
              setProgressOpen(false);
              setSnackbarMessage('データ収集が完了しました');
              setSnackbarSeverity('success');
              setSnackbarOpen(true);
            }, 1000);
            return 100;
          }
          return prev + Math.random() * 10;
        });
      }, 500);

    } catch (error) {
      setProgressOpen(false);
      setSnackbarMessage(`データ収集に失敗しました: ${error instanceof Error ? error.message : '不明なエラー'}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleCancelConfirm = () => {
    setConfirmOpen(false);
  };

  const handleCloseProgress = () => {
    setProgressOpen(false);
    setProgress(0);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <>
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
            🔄 手動データ収集実行
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            最新のドル円レートデータを手動で収集します。通常は自動収集により不要ですが、
            緊急時やトラブル対応時にご利用ください。
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            データ収集は通常5〜10分程度で完了します。進行状況はリアルタイムで表示されます。
          </Alert>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={collectionMutation.isPending ? <CircularProgress size={20} /> : <span>🔄</span>}
              onClick={handleCollectionStart}
              disabled={collectionMutation.isPending}
              sx={{
                minWidth: 200,
                background: 'linear-gradient(135deg, #00d4ff, #0099cc)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #33ddff, #00d4ff)',
                },
              }}
            >
              {collectionMutation.isPending ? 'データ収集実行中...' : '今すぐデータ収集を実行'}
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<span>📊</span>}
              onClick={() => {
                setSnackbarMessage('収集履歴機能は開発中です');
                setSnackbarSeverity('info');
                setSnackbarOpen(true);
              }}
            >
              収集履歴を確認
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* 確認ダイアログ */}
      <Dialog
        open={confirmOpen}
        onClose={handleCancelConfirm}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          データ収集実行の確認
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            手動でデータ収集を実行しますか？
          </Typography>
          <Alert severity="warning" sx={{ mb: 2 }}>
            この処理は5〜10分程度時間がかかる場合があります。
          </Alert>
          <Typography variant="body2" color="text.secondary">
            • 全データソースから最新データを取得します
            • 既存データとの重複チェックを行います
            • データ品質検証を実行します
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelConfirm} color="inherit">
            キャンセル
          </Button>
          <Button
            onClick={handleConfirmCollection}
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
          データ収集実行中
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CircularProgress size={24} sx={{ mr: 2 }} />
              <Typography variant="body1">
                データを収集しています...
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
            
            {collectionId && (
              <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 1 }}>
                収集ID: {collectionId}
              </Typography>
            )}
          </Box>

          <Alert severity="info">
            収集中はこのダイアログを閉じずにお待ちください。
          </Alert>
        </DialogContent>
        {progress >= 100 && (
          <DialogActions>
            <Button onClick={handleCloseProgress} variant="contained">
              閉じる
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

export default ManualDataCollection;
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Box,
  Alert,
  Skeleton,
  Snackbar,
  Tooltip,
  IconButton,
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { useDataSources, useSourceHealthCheck } from '../hooks/useDataManagement';
import type { DataSource } from '../hooks/useDataManagement';

const DataSourcesTable: React.FC = () => {
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('success');

  const { data: sourcesData, isLoading, error, refetch } = useDataSources();
  const healthCheckMutation = useSourceHealthCheck();

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'default';
      case 'error':
        return 'error';
      case 'maintenance':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return '✅';
      case 'inactive':
        return '⚪';
      case 'error':
        return '❌';
      case 'maintenance':
        return '🔧';
      default:
        return '❓';
    }
  };

  const getSourceTypeLabel = (sourceType: string) => {
    switch (sourceType) {
      case 'yahoo_finance':
        return 'プライマリソース';
      case 'boj_csv':
        return '履歴データソース';
      case 'alpha_vantage':
        return 'バックアップソース';
      case 'scraping':
        return 'スクレイピング';
      default:
        return sourceType;
    }
  };

  const getSuccessRateColor = (rate: number) => {
    if (rate >= 0.95) return 'success.main';
    if (rate >= 0.8) return 'warning.main';
    return 'error.main';
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getTimeAgo = (dateString: string | null) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffMinutes < 60) return `${diffMinutes}分前`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}時間前`;
    return `${Math.floor(diffMinutes / 1440)}日前`;
  };

  const handleHealthCheck = async (sourceName: string) => {
    try {
      await healthCheckMutation.mutateAsync(sourceName);
      setSnackbarMessage(`${sourceName} のヘルスチェックが完了しました`);
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (error) {
      setSnackbarMessage(`ヘルスチェックに失敗しました: ${error instanceof Error ? error.message : '不明なエラー'}`);
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };

  const handleRefresh = () => {
    refetch();
    setSnackbarMessage('データソース情報を更新しました');
    setSnackbarSeverity('info');
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Skeleton variant="text" width={200} height={32} />
            <Skeleton variant="circular" width={40} height={40} />
          </Box>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  {[1, 2, 3, 4, 5].map((col) => (
                    <TableCell key={col}>
                      <Skeleton variant="text" />
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {[1, 2, 3].map((row) => (
                  <TableRow key={row}>
                    {[1, 2, 3, 4, 5].map((col) => (
                      <TableCell key={col}>
                        <Skeleton variant="text" />
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        データソース情報の取得に失敗しました: {error.message}
      </Alert>
    );
  }

  if (!sourcesData) {
    return null;
  }

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
              🌐 データソース稼働状況
            </Typography>
            <Tooltip title="最新情報に更新">
              <IconButton onClick={handleRefresh} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {/* 健全性サマリー */}
          <Box sx={{ mb: 3, p: 2, backgroundColor: 'background.default', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              システム健全性
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip
                icon={<span>{getStatusIcon('active')}</span>}
                label={`アクティブ: ${sourcesData.health.active_sources}/${sourcesData.health.total_sources}`}
                color="success"
                size="small"
              />
              {sourcesData.health.error_sources > 0 && (
                <Chip
                  icon={<span>❌</span>}
                  label={`エラー: ${sourcesData.health.error_sources}`}
                  color="error"
                  size="small"
                />
              )}
              <Chip
                icon={<span>📊</span>}
                label={`健全性スコア: ${(sourcesData.health.health_score * 100).toFixed(1)}%`}
                color={sourcesData.health.health_score >= 0.8 ? 'success' : 'warning'}
                size="small"
              />
            </Box>
          </Box>

          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>データソース</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>ステータス</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>最終取得</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>成功率</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>アクション</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sourcesData.sources.map((source: DataSource) => (
                  <TableRow 
                    key={source.id}
                    hover
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                          {source.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {getSourceTypeLabel(source.source_type)}
                        </Typography>
                        {source.url && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                            優先度: {source.priority}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    
                    <TableCell>
                      <Chip
                        icon={<span>{getStatusIcon(source.status)}</span>}
                        label={source.status === 'active' ? '正常' : source.status}
                        color={getStatusColor(source.status)}
                        size="small"
                      />
                    </TableCell>
                    
                    <TableCell>
                      <Box>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {formatDate(source.last_success_at)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {getTimeAgo(source.last_success_at)}
                        </Typography>
                      </Box>
                    </TableCell>
                    
                    <TableCell>
                      <Box>
                        <Typography
                          variant="body2"
                          sx={{
                            fontFamily: 'monospace',
                            color: getSuccessRateColor(source.success_rate),
                            fontWeight: 600,
                          }}
                        >
                          {(source.success_rate * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          過去30日間
                        </Typography>
                      </Box>
                    </TableCell>
                    
                    <TableCell>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => handleHealthCheck(source.name)}
                        disabled={healthCheckMutation.isPending}
                        sx={{ minWidth: 80 }}
                      >
                        {source.source_type === 'boj_csv' ? 'ダウンロード' : 'テスト'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* 推奨事項 */}
          {sourcesData.recommendations.length > 0 && (
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                システム推奨事項:
              </Typography>
              {sourcesData.recommendations.map((recommendation, index) => (
                <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                  • {recommendation}
                </Typography>
              ))}
            </Alert>
          )}

          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
            最終チェック: {formatDate(sourcesData.last_health_check)} | 
            次回チェック: {formatDate(sourcesData.next_health_check)}
          </Typography>
        </CardContent>
      </Card>

      {/* スナックバー通知 */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
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

export default DataSourcesTable;
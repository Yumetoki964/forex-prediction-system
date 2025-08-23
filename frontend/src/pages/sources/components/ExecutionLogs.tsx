import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
  Info,
  Refresh,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material';

interface LogEntry {
  id: string;
  timestamp: string;
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  details?: string;
  source?: string;
}

interface ExecutionLogsProps {
  logs?: LogEntry[];
  maxLogs?: number;
  onRefresh?: () => void;
  isLoading?: boolean;
}

const ExecutionLogs: React.FC<ExecutionLogsProps> = ({
  logs = [],
  maxLogs = 20,
  onRefresh,
  isLoading = false,
}) => {
  const [expanded, setExpanded] = React.useState<string | null>(null);

  // モックデータ（APIが未実装の場合）
  const mockLogs: LogEntry[] = [
    {
      id: '1',
      timestamp: '2025-08-23 14:30:45',
      type: 'success',
      message: '日銀データ取得成功 (245件)',
      details: 'CSV形式で245件の為替レートデータを取得しました。',
      source: 'boj',
    },
    {
      id: '2',
      timestamp: '2025-08-23 14:15:22',
      type: 'success',
      message: 'Yahoo Finance スクレイピング成功',
      details: 'リアルタイムレートとテクニカル指標を正常に取得しました。',
      source: 'yahoo',
    },
    {
      id: '3',
      timestamp: '2025-08-23 14:00:10',
      type: 'warning',
      message: 'Alpha Vantage API レート制限',
      details: 'API使用量が制限に近づいています。1時間後に再試行されます。',
      source: 'alphavantage',
    },
    {
      id: '4',
      timestamp: '2025-08-23 13:45:33',
      type: 'success',
      message: 'CSV インポート完了 (1,250件)',
      details: 'ユーザーアップロードCSVから1,250件のレコードをインポートしました。',
      source: 'manual',
    },
    {
      id: '5',
      timestamp: '2025-08-23 13:30:18',
      type: 'error',
      message: '接続タイムアウト (Yahoo Finance)',
      details: 'ネットワークタイムアウトが発生しました。3分後に自動リトライされます。',
      source: 'yahoo',
    },
    {
      id: '6',
      timestamp: '2025-08-23 13:15:45',
      type: 'info',
      message: 'ヘルスチェック実行',
      details: '定期ヘルスチェックを実行しました。全システム正常です。',
      source: 'system',
    },
  ];

  const displayLogs = logs.length > 0 ? logs : mockLogs;
  const limitedLogs = displayLogs.slice(0, maxLogs);

  const getLogIcon = (type: LogEntry['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle sx={{ color: 'success.main' }} />;
      case 'warning':
        return <Warning sx={{ color: 'warning.main' }} />;
      case 'error':
        return <Error sx={{ color: 'error.main' }} />;
      case 'info':
        return <Info sx={{ color: 'info.main' }} />;
      default:
        return <Info sx={{ color: 'text.secondary' }} />;
    }
  };

  const getLogPrefix = (type: LogEntry['type']) => {
    switch (type) {
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'info':
        return 'ℹ️';
      default:
        return '•';
    }
  };

  const getSourceName = (source?: string) => {
    switch (source) {
      case 'boj':
        return '日銀';
      case 'yahoo':
        return 'Yahoo';
      case 'alphavantage':
        return 'AV';
      case 'manual':
        return 'CSV';
      case 'system':
        return 'System';
      default:
        return 'Unknown';
    }
  };

  const getSourceColor = (source?: string) => {
    switch (source) {
      case 'boj':
        return 'primary';
      case 'yahoo':
        return 'secondary';
      case 'alphavantage':
        return 'warning';
      case 'manual':
        return 'info';
      case 'system':
        return 'default';
      default:
        return 'default';
    }
  };

  const handleToggleExpand = (logId: string) => {
    setExpanded(expanded === logId ? null : logId);
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" color="primary">
            最近の実行ログ
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={`${limitedLogs.length}件表示`}
              size="small"
              variant="outlined"
            />
            <Tooltip title="ログを更新">
              <IconButton
                size="small"
                onClick={onRefresh}
                disabled={isLoading}
              >
                <Refresh sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <List sx={{ py: 0 }}>
          {limitedLogs.map((log, index) => (
            <React.Fragment key={log.id}>
              <ListItem
                sx={{
                  px: 0,
                  py: 1,
                  borderRadius: 1,
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {getLogIcon(log.type)}
                </ListItemIcon>
                
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography
                        variant="body2"
                        sx={{
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                          color: 'text.secondary',
                          minWidth: 140,
                        }}
                      >
                        {log.timestamp}
                      </Typography>
                      
                      {log.source && (
                        <Chip
                          label={getSourceName(log.source)}
                          size="small"
                          color={getSourceColor(log.source) as any}
                          variant="outlined"
                          sx={{ height: 20, '& .MuiChip-label': { fontSize: '0.7rem', px: 0.5 } }}
                        />
                      )}
                      
                      <Typography variant="body2" sx={{ flex: 1 }}>
                        {getLogPrefix(log.type)} {log.message}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    expanded === log.id && log.details ? (
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{
                          display: 'block',
                          mt: 1,
                          p: 1,
                          bgcolor: 'background.default',
                          borderRadius: 1,
                          fontFamily: 'monospace',
                          fontSize: '0.75rem',
                        }}
                      >
                        {log.details}
                      </Typography>
                    ) : null
                  }
                />
                
                {log.details && (
                  <IconButton
                    size="small"
                    onClick={() => handleToggleExpand(log.id)}
                    sx={{ ml: 1 }}
                  >
                    {expanded === log.id ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                )}
              </ListItem>
              
              {index < limitedLogs.length - 1 && (
                <Box sx={{ height: 1, bgcolor: 'divider', mx: 2 }} />
              )}
            </React.Fragment>
          ))}
        </List>

        {displayLogs.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary">
              実行ログはありません
            </Typography>
          </Box>
        )}

        {displayLogs.length > maxLogs && (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              {displayLogs.length - maxLogs}件のログが省略されています
            </Typography>
          </Box>
        )}

        {/* ログ統計 */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
            ログ統計 (直近24時間)
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                成功: {limitedLogs.filter(log => log.type === 'success').length}件
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Warning sx={{ fontSize: 16, color: 'warning.main' }} />
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                警告: {limitedLogs.filter(log => log.type === 'warning').length}件
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Error sx={{ fontSize: 16, color: 'error.main' }} />
              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                エラー: {limitedLogs.filter(log => log.type === 'error').length}件
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ExecutionLogs;
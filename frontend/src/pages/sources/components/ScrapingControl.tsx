import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Switch,
  Alert,
  LinearProgress,
  Chip,
} from '@mui/material';
import { PlayArrow, Stop, Refresh } from '@mui/icons-material';
import { useRunScraping } from '../hooks/useSourcesData';

interface ScrapingControlProps {
  onScrapingStart?: () => void;
}

const ScrapingControl: React.FC<ScrapingControlProps> = ({ onScrapingStart }) => {
  const [selectedSource, setSelectedSource] = useState<string>('all');
  const [forceMode, setForceMode] = useState<boolean>(false);
  const runScrapingMutation = useRunScraping();

  const sourceOptions = [
    { value: 'all', label: '全ソース', description: 'すべてのデータソースからスクレイピング' },
    { value: 'yahoo', label: 'Yahoo Finance', description: 'リアルタイム為替レート取得' },
    { value: 'boj', label: '日本銀行', description: 'CSVデータ取得' },
    { value: 'alphavantage', label: 'Alpha Vantage', description: 'バックアップAPIデータ取得' },
  ];

  const handleStartScraping = () => {
    const params = {
      source: selectedSource === 'all' ? undefined : selectedSource,
      force: forceMode,
    };

    runScrapingMutation.mutate(params);
    onScrapingStart?.();
  };

  const handleStopScraping = () => {
    // スクレイピング停止機能（実装予定）
    console.log('Stopping scraping...');
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Box sx={{ fontSize: '1.5rem', mr: 2 }}>🕷️</Box>
          <Typography variant="h6" color="primary">
            Webスクレイピング実行
          </Typography>
          {runScrapingMutation.isPending && (
            <Chip
              label="実行中"
              color="info"
              size="small"
              sx={{ ml: 'auto' }}
              icon={<Refresh sx={{ animation: 'spin 1s linear infinite' }} />}
            />
          )}
        </Box>

        {runScrapingMutation.isPending && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              データソースからスクレイピング中...
            </Typography>
          </Box>
        )}

        {/* データソース選択 */}
        <FormControl component="fieldset" sx={{ mb: 3, width: '100%' }}>
          <FormLabel component="legend" sx={{ mb: 2 }}>
            スクレイピング対象
          </FormLabel>
          <RadioGroup
            value={selectedSource}
            onChange={(e) => setSelectedSource(e.target.value)}
          >
            {sourceOptions.map((option) => (
              <FormControlLabel
                key={option.value}
                value={option.value}
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body1">{option.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.description}
                    </Typography>
                  </Box>
                }
                sx={{ mb: 1, alignItems: 'flex-start' }}
              />
            ))}
          </RadioGroup>
        </FormControl>

        {/* 強制実行オプション */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Switch
            checked={forceMode}
            onChange={(e) => setForceMode(e.target.checked)}
            disabled={runScrapingMutation.isPending}
          />
          <Box sx={{ ml: 2 }}>
            <Typography variant="body2">
              強制実行モード
            </Typography>
            <Typography variant="caption" color="text.secondary">
              前回の実行から間隔が短くても強制的に実行します
            </Typography>
          </Box>
        </Box>

        {/* 警告メッセージ */}
        {forceMode && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            <Typography variant="body2">
              強制実行モードは、短期間に大量のリクエストを送信する可能性があります。
              対象サイトの利用規約を遵守し、適切な間隔を空けてください。
            </Typography>
          </Alert>
        )}

        {/* 実行ボタン */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="success"
            startIcon={<PlayArrow />}
            onClick={handleStartScraping}
            disabled={runScrapingMutation.isPending}
            fullWidth
          >
            スクレイピング実行
          </Button>
          
          {runScrapingMutation.isPending && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<Stop />}
              onClick={handleStopScraping}
              sx={{ minWidth: 120 }}
            >
              停止
            </Button>
          )}
        </Box>

        {/* スクレイピング情報 */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
            スクレイピング情報
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • 実行間隔: 5分毎 (自動)
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • タイムアウト: 30秒
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • 最大リトライ: 3回
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • 対象データ: リアルタイム為替レート、経済指標
            </Typography>
          </Box>
        </Box>

        <style>
          {`
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `}
        </style>
      </CardContent>
    </Card>
  );
};

export default ScrapingControl;
import React from 'react';
import { Box, Typography, Grid, Button } from '@mui/material';
import { Refresh, TrendingUp } from '@mui/icons-material';
import SourcesList from './components/SourcesList';
import ScrapingControl from './components/ScrapingControl';
import CSVImportUpload from './components/CSVImportUpload';
import HealthMetrics from './components/HealthMetrics';
import ExecutionLogs from './components/ExecutionLogs';
import {
  useSourcesStatus,
  useHealthMetrics,
  mockSourcesData,
  mockHealthMetrics,
} from './hooks/useSourcesData';

const SourcesPage: React.FC = () => {
  // データソース状況を取得
  const {
    data: sourcesData,
    isLoading: sourcesLoading,
    refetch: refetchSources,
  } = useSourcesStatus();

  // ヘルスメトリクスを取得
  const {
    data: healthData,
    isLoading: healthLoading,
    refetch: refetchHealth,
  } = useHealthMetrics();

  // APIが未実装の場合はモックデータを使用
  const displaySources = sourcesData?.sources || mockSourcesData.sources;
  const displayHealth = healthData || mockHealthMetrics;

  const handleRefreshAll = () => {
    refetchSources();
    refetchHealth();
  };

  const handleScrapingStart = () => {
    // スクレイピング開始時にデータを更新
    setTimeout(() => {
      refetchSources();
    }, 1000);
  };

  const handleImportComplete = (result: any) => {
    // インポート完了時にデータを更新
    console.log('Import completed:', result);
    refetchSources();
  };

  return (
    <Box>
      {/* ページヘッダー */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
        <Box>
          <Typography variant="h3" component="h1" sx={{ mb: 1, fontWeight: 'bold' }}>
            🌐 データソース管理
          </Typography>
          <Typography variant="body1" color="text.secondary">
            複数データソースの統合管理・監視・優先順位設定
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefreshAll}
            disabled={sourcesLoading || healthLoading}
          >
            全体更新
          </Button>
          <Button
            variant="contained"
            startIcon={<TrendingUp />}
            disabled
          >
            自動化設定 (予定)
          </Button>
        </Box>
      </Box>

      {/* データソース一覧 */}
      <Box sx={{ mb: 4 }}>
        <SourcesList sources={displaySources} isLoading={sourcesLoading} />
      </Box>

      {/* 機能コントロール */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={4}>
          <ScrapingControl onScrapingStart={handleScrapingStart} />
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <CSVImportUpload
            onImportStart={handleScrapingStart}
            onImportComplete={handleImportComplete}
          />
        </Grid>
        
        <Grid item xs={12} lg={4}>
          <HealthMetrics metrics={displayHealth} isLoading={healthLoading} />
        </Grid>
      </Grid>

      {/* 実行ログ */}
      <ExecutionLogs onRefresh={handleRefreshAll} isLoading={sourcesLoading} />
    </Box>
  );
};

export default SourcesPage;
import React from 'react';
import { Box, Typography, Divider } from '@mui/material';
import DataCollectionStatus from './components/DataCollectionStatus';
import DataQualityReport from './components/DataQualityReport';
import ManualDataCollection from './components/ManualDataCollection';
import DataRepairTool from './components/DataRepairTool';
import DataSourcesTable from './components/DataSourcesTable';

const DataManagementPage: React.FC = () => {
  return (
    <Box>
      {/* ページヘッダー */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ mb: 1, fontWeight: 'bold' }}>
          🗄️ データ管理
        </Typography>
        <Typography variant="body1" color="text.secondary">
          データ収集・品質監視・修復の統合管理
        </Typography>
      </Box>

      {/* データ収集状況セクション */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          データ収集状況
        </Typography>
        <DataCollectionStatus />
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* データ品質レポートセクション */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          データ品質レポート
        </Typography>
        <DataQualityReport />
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* 手動データ収集セクション */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          手動データ収集実行
        </Typography>
        <ManualDataCollection />
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* データ修復ツールセクション */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          データ修復ツール（欠損補完）
        </Typography>
        <DataRepairTool />
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* データソース稼働状況セクション */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
          データソース稼働状況
        </Typography>
        <DataSourcesTable />
      </Box>
    </Box>
  );
};

export default DataManagementPage;
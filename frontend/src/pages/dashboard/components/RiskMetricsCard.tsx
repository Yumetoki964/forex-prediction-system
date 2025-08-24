import React from 'react';
import { Card, CardContent, Typography, Grid, Box, LinearProgress } from '@mui/material';
import { numericFont } from '@/theme';

// API後でRiskMetrics型を定義する予定だが、一旦仮の型を定義
interface RiskMetrics {
  volatility: number; // ボラティリティ（%）
  confidence_level: number; // 信頼水準（%）
  var_95?: number; // VaR 95%
  max_drawdown?: number; // 最大ドローダウン
  sharpe_ratio?: number; // シャープレシオ
}

interface RiskMetricsCardProps {
  data?: RiskMetrics;
  loading?: boolean;
  error?: string | null;
}

const getRiskLevel = (volatility: number): { level: string; color: string } => {
  if (volatility < 1) return { level: '低', color: 'success.main' };
  if (volatility < 2) return { level: '中', color: 'warning.main' };
  if (volatility < 3) return { level: '高', color: 'error.main' };
  return { level: '極高', color: 'error.dark' };
};

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 90) return 'success.main';
  if (confidence >= 70) return 'warning.main';
  return 'error.main';
};

export const RiskMetricsCard: React.FC<RiskMetricsCardProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            リスク指標
          </Typography>
          <Typography variant="body2" color="text.secondary">
            読み込み中...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            リスク指標
          </Typography>
          <Typography color="error.main">{error}</Typography>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            リスク指標
          </Typography>
          <Typography color="text.secondary">
            リスクデータがありません
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const volatilityRisk = getRiskLevel(data.volatility || 0);
  const confidenceColor = getConfidenceColor(data.confidence_level || 0);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
          リスク指標
        </Typography>
        
        <Grid container spacing={3} sx={{ flex: 1 }}>
          {/* ボラティリティ */}
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', display: 'block' }}>
                ボラティリティ
              </Typography>
              <Typography variant="h5" sx={{ fontFamily: numericFont.fontFamily, mt: 1, color: volatilityRisk.color }}>
                {data.volatility?.toFixed(2) || '0.00'}%
              </Typography>
              <Typography variant="caption" sx={{ color: volatilityRisk.color, fontWeight: 'medium' }}>
                リスク: {volatilityRisk.level}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((data.volatility || 0) * 20, 100)} 
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
                color={(data.volatility || 0) < 2 ? 'success' : (data.volatility || 0) < 3 ? 'warning' : 'error'}
              />
            </Box>
          </Grid>
          
          {/* 信頼区間 */}
          <Grid item xs={6}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', display: 'block' }}>
                信頼水準
              </Typography>
              <Typography variant="h5" sx={{ fontFamily: numericFont.fontFamily, mt: 1, color: confidenceColor }}>
                {Math.round(data.confidence_level || 0)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={data.confidence_level || 0} 
                sx={{ mt: 1, height: 4, borderRadius: 2 }}
                color={(data.confidence_level || 0) >= 90 ? 'success' : (data.confidence_level || 0) >= 70 ? 'warning' : 'error'}
              />
            </Box>
          </Grid>
        </Grid>

        {/* 追加指標 */}
        {(data.var_95 || data.max_drawdown || data.sharpe_ratio) && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Grid container spacing={2}>
              {data.var_95 && (
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                    VaR 95%
                  </Typography>
                  <Typography variant="body2" sx={{ fontFamily: numericFont.fontFamily, fontWeight: 'medium' }}>
                    {data.var_95?.toFixed(2) || '0.00'}%
                  </Typography>
                </Grid>
              )}
              {data.max_drawdown && (
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                    最大DD
                  </Typography>
                  <Typography variant="body2" sx={{ fontFamily: numericFont.fontFamily, fontWeight: 'medium' }}>
                    {data.max_drawdown?.toFixed(2) || '0.00'}%
                  </Typography>
                </Grid>
              )}
              {data.sharpe_ratio && (
                <Grid item xs={4}>
                  <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase' }}>
                    シャープ
                  </Typography>
                  <Typography variant="body2" sx={{ fontFamily: numericFont.fontFamily, fontWeight: 'medium' }}>
                    {data.sharpe_ratio?.toFixed(2) || '0.00'}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default RiskMetricsCard;
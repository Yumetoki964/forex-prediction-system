import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Box,
  Alert,
  Chip,
  Skeleton,
} from '@mui/material';
import { useDataQuality } from '../hooks/useDataManagement';

const DataQualityReport: React.FC = () => {
  const { data: report, isLoading, error } = useDataQuality();

  if (isLoading) {
    return (
      <Grid container spacing={3}>
        {[1, 2].map((item) => (
          <Grid item xs={12} md={6} key={item}>
            <Card>
              <CardContent>
                <Skeleton variant="text" height={24} />
                <Skeleton variant="text" height={40} sx={{ my: 1 }} />
                <Skeleton variant="rectangular" height={8} sx={{ mb: 1 }} />
                <Skeleton variant="text" height={20} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 3 }}>
        データ品質レポートの取得に失敗しました: {error.message}
      </Alert>
    );
  }

  if (!report) {
    return null;
  }

  const getHealthStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'excellent':
        return 'success';
      case 'good':
        return 'primary';
      case 'fair':
      case 'warning':
        return 'warning';
      case 'poor':
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
      case 'critical':
        return 'error';
      case 'medium':
      case 'warning':
        return 'warning';
      case 'low':
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatTrend = (change: number) => {
    if (change > 0) return `+${formatPercentage(change)}`;
    if (change < 0) return formatPercentage(change);
    return '変化なし';
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) return '📈';
    if (change < 0) return '📉';
    return '➡️';
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* データ欠損率 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography
                  variant="overline"
                  sx={{
                    color: 'warning.main',
                    fontWeight: 600,
                    letterSpacing: 1,
                  }}
                >
                  ⚠️ データ欠損率
                </Typography>
              </Box>
              <Typography
                variant="h4"
                sx={{
                  fontFamily: 'monospace',
                  fontWeight: 'bold',
                  mb: 2,
                  color: 'warning.main',
                }}
              >
                {formatPercentage(1 - report.quality_metrics.completeness_rate)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(1 - report.quality_metrics.completeness_rate) * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  mb: 2,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    backgroundColor: 'warning.main',
                  },
                }}
              />
              <Typography variant="body2" color="text.secondary">
                分析期間: {formatDate(report.analysis_period.start)} 〜 {formatDate(report.analysis_period.end)}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="body2" sx={{ mr: 1 }}>
                  トレンド:
                </Typography>
                <Chip
                  size="small"
                  label={formatTrend(report.quality_trends.completeness_change)}
                  icon={<span>{getTrendIcon(report.quality_trends.completeness_change)}</span>}
                  color={report.quality_trends.completeness_change <= 0 ? 'success' : 'warning'}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 異常値検出 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography
                  variant="overline"
                  sx={{
                    color: 'primary.main',
                    fontWeight: 600,
                    letterSpacing: 1,
                  }}
                >
                  🔍 異常値検出
                </Typography>
              </Box>
              <Typography
                variant="h4"
                sx={{
                  fontFamily: 'monospace',
                  fontWeight: 'bold',
                  mb: 2,
                }}
              >
                {report.quality_metrics.outlier_count}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                分析期間内で{report.quality_metrics.outlier_count}件の異常値を検出
              </Typography>
              
              {/* 品質スコア */}
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  総合品質スコア: {formatPercentage(report.overall_quality_score)}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={report.overall_quality_score * 100}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: 'grey.200',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 3,
                      background: 'linear-gradient(90deg, #00d4ff, #33ddff)',
                    },
                  }}
                />
              </Box>

              <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                <Chip
                  size="small"
                  label={report.data_health_status}
                  color={getHealthStatusColor(report.data_health_status)}
                  sx={{ textTransform: 'capitalize' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 品質問題アラート */}
        {report.quality_issues.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="warning">
              <Typography variant="h6" sx={{ mb: 1 }}>
                検出された品質問題
              </Typography>
              {report.quality_issues.slice(0, 3).map((issue) => (
                <Box key={issue.issue_id} sx={{ mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      size="small"
                      label={issue.severity}
                      color={getSeverityColor(issue.severity)}
                    />
                    <Typography variant="body2">
                      {issue.description}
                    </Typography>
                  </Box>
                  {issue.affected_dates.length > 0 && (
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                      影響期間: {issue.affected_dates[0]}
                      {issue.affected_dates.length > 1 && ` 他${issue.affected_dates.length - 1}件`}
                    </Typography>
                  )}
                </Box>
              ))}
              {report.quality_issues.length > 3 && (
                <Typography variant="body2" color="text.secondary">
                  他 {report.quality_issues.length - 3} 件の問題があります
                </Typography>
              )}
            </Alert>
          </Grid>
        )}

        {/* 推奨事項 */}
        {report.recommendations.length > 0 && (
          <Grid item xs={12}>
            <Card sx={{ backgroundColor: 'info.light', color: 'info.contrastText' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  💡 改善提案
                </Typography>
                {report.recommendations.map((recommendation, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                    • {recommendation}
                  </Typography>
                ))}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* 詳細指標 */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3 }}>
            詳細品質指標
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  完全性
                </Typography>
                <Typography variant="h6" sx={{ fontFamily: 'monospace' }}>
                  {formatPercentage(report.quality_metrics.completeness_rate)}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  正確性
                </Typography>
                <Typography variant="h6" sx={{ fontFamily: 'monospace' }}>
                  {formatPercentage(report.quality_metrics.accuracy_rate)}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  一貫性
                </Typography>
                <Typography variant="h6" sx={{ fontFamily: 'monospace' }}>
                  {formatPercentage(report.quality_metrics.consistency_rate)}
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  重複数
                </Typography>
                <Typography variant="h6" sx={{ fontFamily: 'monospace' }}>
                  {report.quality_metrics.duplicate_count}
                </Typography>
              </Box>
            </Grid>
          </Grid>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
            最終チェック: {formatDate(report.quality_metrics.last_quality_check)}
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DataQualityReport;
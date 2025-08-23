import React from 'react';
import { Card, CardContent, Typography, Box, Chip, LinearProgress } from '@mui/material';

// API後でModelInfo型を定義する予定だが、一旦仮の型を定義
interface ModelInfo {
  ensemble_composition: Record<string, number>; // アンサンブル構成
  training_period: string; // 学習期間
  backtest_accuracy_1w?: number; // 1週間予測精度
  backtest_accuracy_2w?: number; // 2週間予測精度
  model_version: string; // モデルバージョン
  last_training_date?: string; // 最終学習日
  data_points_used?: number; // 使用データポイント数
}

interface ModelInfoCardProps {
  data?: ModelInfo;
  loading?: boolean;
  error?: string | null;
}

const getAccuracyColor = (accuracy: number): string => {
  if (accuracy >= 75) return 'success.main';
  if (accuracy >= 65) return 'warning.main';
  return 'error.main';
};

const getModelTypeColor = (modelType: string): string => {
  switch (modelType.toLowerCase()) {
    case 'lstm': return '#9c27b0'; // 紫
    case 'xgboost': return '#ff9800'; // オレンジ
    case 'ensemble': return '#2196f3'; // 青
    default: return '#757575'; // グレー
  }
};

export const ModelInfoCard: React.FC<ModelInfoCardProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            モデル情報
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
            モデル情報
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
            モデル情報
          </Typography>
          <Typography color="text.secondary">
            モデルデータがありません
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
          モデル情報
        </Typography>
        
        <Box sx={{ '& > div': { mb: 2 }, flex: 1 }}>
          {/* アンサンブル構成 */}
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 'medium', mb: 1 }}>
              アンサンブル構成:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
              {Object.entries(data.ensemble_composition).map(([model, weight]) => (
                <Chip
                  key={model}
                  label={`${model.toUpperCase()} ${Math.round(weight * 100)}%`}
                  size="small"
                  sx={{
                    backgroundColor: getModelTypeColor(model),
                    color: 'white',
                    fontSize: '0.75rem',
                  }}
                />
              ))}
            </Box>
            {/* アンサンブル重みの視覚的表示 */}
            {Object.entries(data.ensemble_composition).map(([model, weight]) => (
              <Box key={model} sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                  <Typography variant="caption" color="text.secondary">
                    {model.toUpperCase()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {Math.round(weight * 100)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={weight * 100}
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getModelTypeColor(model),
                    },
                  }}
                />
              </Box>
            ))}
          </Box>

          {/* 学習期間 */}
          <Box>
            <Typography variant="body2">
              <strong>学習期間:</strong> {data.training_period}
            </Typography>
          </Box>

          {/* バックテスト精度 */}
          {data.backtest_accuracy_1w && (
            <Box>
              <Typography variant="body2">
                <strong>バックテスト精度:</strong>{' '}
                <Typography 
                  component="span" 
                  sx={{ color: getAccuracyColor(data.backtest_accuracy_1w) }}
                >
                  {data.backtest_accuracy_1w.toFixed(1)}%
                </Typography>{' '}
                (1週間予測)
              </Typography>
              {data.backtest_accuracy_2w && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                  2週間予測: {data.backtest_accuracy_2w.toFixed(1)}%
                </Typography>
              )}
            </Box>
          )}

          {/* モデルバージョン */}
          <Box>
            <Typography variant="body2">
              <strong>モデルバージョン:</strong> {data.model_version}
            </Typography>
          </Box>

          {/* 追加情報 */}
          {(data.last_training_date || data.data_points_used) && (
            <Box sx={{ pt: 1, borderTop: 1, borderColor: 'divider', mt: 'auto' }}>
              {data.last_training_date && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                  最終学習: {new Date(data.last_training_date).toLocaleDateString('ja-JP')}
                </Typography>
              )}
              {data.data_points_used && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                  使用データ: {data.data_points_used.toLocaleString()}ポイント
                </Typography>
              )}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ModelInfoCard;
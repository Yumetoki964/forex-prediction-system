import React from 'react';
import { Card, CardContent, Typography, Grid, Skeleton } from '@mui/material';
import { LatestPredictionsResponse } from '@/generated/Api';
import { numericFont } from '@/theme';

interface PredictionsCardProps {
  data?: LatestPredictionsResponse;
  loading?: boolean;
  error?: string | null;
}

export const PredictionsCard: React.FC<PredictionsCardProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            予測レート
          </Typography>
          <Grid container spacing={2}>
            {[1, 2, 3, 4].map((index) => (
              <Grid item xs={6} md={3} key={index}>
                <Card variant="outlined">
                  <CardContent sx={{ p: 2 }}>
                    <Skeleton variant="text" width="60%" height={20} />
                    <Skeleton variant="text" width="80%" height={32} sx={{ my: 1 }} />
                    <Skeleton variant="text" width="100%" height={16} />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            予測レート
          </Typography>
          <Typography color="error.main">{error}</Typography>
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.predictions.length) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            予測レート
          </Typography>
          <Typography color="text.secondary">予測データがありません</Typography>
        </CardContent>
      </Card>
    );
  }

  const getPeriodLabel = (period: string): string => {
    switch (period) {
      case '1week': return '1週間後';
      case '2weeks': return '2週間後';
      case '3weeks': return '3週間後';
      case '1month': return '1ヶ月後';
      default: return period;
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" color="primary.main" sx={{ mb: 3, textTransform: 'uppercase', fontSize: '0.875rem' }}>
          予測レート
        </Typography>
        <Grid container spacing={2}>
          {data.predictions.map((prediction, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Card 
                variant="outlined"
                sx={{
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    boxShadow: '0 0 0 2px rgba(0, 212, 255, 0.2)',
                  },
                }}
              >
                <CardContent sx={{ p: 2 }}>
                  <Typography variant="caption" color="text.disabled" sx={{ textTransform: 'uppercase' }}>
                    {getPeriodLabel(prediction.period)}
                  </Typography>
                  <Typography variant="h6" sx={{ fontFamily: numericFont.fontFamily, my: 1 }}>
                    {prediction.predicted_rate.toFixed(2)}
                  </Typography>
                  {prediction.confidence_interval_lower && prediction.confidence_interval_upper ? (
                    <Typography variant="caption" color="text.secondary" sx={{ fontFamily: numericFont.fontFamily }}>
                      {prediction.confidence_interval_lower.toFixed(2)} - {prediction.confidence_interval_upper.toFixed(2)}
                    </Typography>
                  ) : null}
                  {prediction.prediction_strength && (
                    <Typography variant="caption" color="primary.main" sx={{ display: 'block', mt: 0.5 }}>
                      強度: {Math.round(prediction.prediction_strength * 100)}%
                    </Typography>
                  )}
                  <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 0.5 }}>
                    予測日: {new Date(prediction.target_date).toLocaleDateString('ja-JP')}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
          予測実行日: {new Date(data.prediction_date).toLocaleDateString('ja-JP')} |
          モデルバージョン: {data.model_version} |
          信頼水準: {Math.round((data.confidence_level || 0.95) * 100)}%
        </Typography>
      </CardContent>
    </Card>
  );
};

export default PredictionsCard;
import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { CurrentRateResponse } from '@/generated/Api';
import { numericFont } from '@/theme';

interface CurrentRateCardProps {
  data?: CurrentRateResponse;
  loading?: boolean;
  error?: string | null;
}

export const CurrentRateCard: React.FC<CurrentRateCardProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <Card
        sx={{
          background: 'linear-gradient(135deg, #2d3748, rgba(0, 212, 255, 0.05))',
          border: '2px solid #00d4ff',
          p: 2,
        }}
      >
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            USD/JPY 現在レート
          </Typography>
          <Typography
            variant="h2"
            sx={{
              color: 'text.disabled',
              fontFamily: numericFont.fontFamily,
              mb: 1,
            }}
          >
            読み込み中...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card
        sx={{
          background: 'linear-gradient(135deg, #2d3748, rgba(239, 68, 68, 0.05))',
          border: '2px solid #ef4444',
          p: 2,
        }}
      >
        <CardContent>
          <Typography variant="h6" color="error.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            USD/JPY 現在レート
          </Typography>
          <Typography variant="body2" color="error.main">
            {error}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card
        sx={{
          background: 'linear-gradient(135deg, #2d3748, rgba(0, 212, 255, 0.05))',
          border: '2px solid #00d4ff',
          p: 2,
        }}
      >
        <CardContent>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            USD/JPY 現在レート
          </Typography>
          <Typography variant="body2" color="text.secondary">
            データがありません
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const changeColor = data.change_24h > 0 ? 'success.main' : data.change_24h < 0 ? 'error.main' : 'warning.main';
  const changePrefix = data.change_24h > 0 ? '+' : '';

  return (
    <Card
      sx={{
        background: 'linear-gradient(135deg, #2d3748, rgba(0, 212, 255, 0.05))',
        border: '2px solid #00d4ff',
        p: 2,
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)',
        },
        transition: 'all 0.3s ease',
      }}
    >
      <CardContent>
        <Typography variant="h6" color="primary.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
          USD/JPY 現在レート
        </Typography>
        <Typography
          variant="h2"
          sx={{
            color: 'primary.main',
            fontFamily: numericFont.fontFamily,
            mb: 1,
          }}
        >
          {data.rate.toFixed(2)}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
          <Typography color={changeColor} sx={{ fontFamily: numericFont.fontFamily }}>
            {changePrefix}{data.change_24h.toFixed(2)}
          </Typography>
          <Typography color={changeColor} sx={{ fontFamily: numericFont.fontFamily }}>
            ({changePrefix}{data.change_percentage_24h.toFixed(2)}%)
          </Typography>
          <Typography variant="caption" color="text.secondary">
            24時間変化
          </Typography>
          {data.is_market_open ? (
            <Box
              sx={{
                width: 8,
                height: 8,
                backgroundColor: 'success.main',
                borderRadius: '50%',
                ml: 1,
                animation: 'pulse 2s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.7 },
                },
              }}
            />
          ) : (
            <Typography variant="caption" color="text.disabled" sx={{ ml: 1 }}>
              市場クローズ
            </Typography>
          )}
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          最終更新: {new Date(data.timestamp).toLocaleString('ja-JP')} | ソース: {data.source}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default CurrentRateCard;
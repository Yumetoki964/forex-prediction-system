import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { CurrentSignalResponse, SignalType } from '@/generated/Api';

interface SignalCardProps {
  data?: CurrentSignalResponse;
  loading?: boolean;
  error?: string | null;
}

const getSignalConfig = (signalType: SignalType) => {
  switch (signalType) {
    case SignalType.StrongBuy:
      return { label: '強い買い', color: 'success.main', bgColor: 'rgba(0, 255, 136, 0.1)' };
    case SignalType.Buy:
      return { label: '買い', color: 'success.main', bgColor: 'rgba(0, 255, 136, 0.05)' };
    case SignalType.Hold:
      return { label: '保持', color: 'warning.main', bgColor: 'rgba(251, 191, 36, 0.1)' };
    case SignalType.Sell:
      return { label: '売り', color: 'error.main', bgColor: 'rgba(239, 68, 68, 0.05)' };
    case SignalType.StrongSell:
      return { label: '強い売り', color: 'error.main', bgColor: 'rgba(239, 68, 68, 0.1)' };
    default:
      return { label: '不明', color: 'text.secondary', bgColor: 'rgba(156, 163, 175, 0.1)' };
  }
};

export const SignalCard: React.FC<SignalCardProps> = ({ data, loading, error }) => {
  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ textAlign: 'center', p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            売買シグナル
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
        <CardContent sx={{ textAlign: 'center', p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            売買シグナル
          </Typography>
          <Typography color="error.main" variant="body2">{error}</Typography>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ textAlign: 'center', p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            売買シグナル
          </Typography>
          <Typography color="text.secondary" variant="body2">
            シグナルデータがありません
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const signalConfig = getSignalConfig(data.signal.signal_type);

  return (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, rgba(45, 55, 72, 0.8), ${signalConfig.bgColor})`,
        border: `1px solid ${signalConfig.color}`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)',
        },
      }}
    >
      <CardContent sx={{ textAlign: 'center', p: 3, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h6" color="primary.main" sx={{ mb: 2, textTransform: 'uppercase', fontSize: '0.875rem' }}>
            売買シグナル
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 2 }}>
            <Typography variant="h4" sx={{ color: signalConfig.color, fontWeight: 'bold' }}>
              {signalConfig.label}
            </Typography>
            <Typography variant="h5" color="text.secondary">
              {data.trend_arrow}
            </Typography>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            信頼度: {Math.round(data.signal.confidence * 100)}%
          </Typography>

          {data.signal.strength && (
            <Chip 
              label={`強度: ${Math.round(data.signal.strength * 100)}%`}
              size="small"
              sx={{ mb: 2, backgroundColor: signalConfig.bgColor, color: signalConfig.color }}
            />
          )}

          {data.signal_changed && (
            <Chip 
              label="シグナル変更"
              color="warning"
              size="small"
              sx={{ mb: 2 }}
            />
          )}
        </Box>

        <Box>
          {data.signal.reasoning && (
            <Typography variant="caption" color="text.disabled" sx={{ lineHeight: 1.4, display: 'block', mb: 1 }}>
              {JSON.parse(data.signal.reasoning)?.summary || data.signal.reasoning}
            </Typography>
          )}
          
          <Typography variant="caption" color="text.secondary">
            最終更新: {new Date(data.last_updated).toLocaleString('ja-JP')}
          </Typography>
          
          {data.next_update_at && (
            <Typography variant="caption" color="text.disabled" sx={{ display: 'block', mt: 0.5 }}>
              次回更新: {new Date(data.next_update_at).toLocaleString('ja-JP')}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default SignalCard;
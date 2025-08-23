import React from 'react';
import { Box, Typography, Alert, AlertTitle, Skeleton } from '@mui/material';

// API後でAlert型を定義する予定だが、一旦仮の型を定義
interface AlertItem {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  created_at: string;
  title?: string;
}

interface AlertsSectionProps {
  alerts?: AlertItem[];
  loading?: boolean;
  error?: string | null;
}

const getAlertIcon = (type: AlertItem['type']): string => {
  switch (type) {
    case 'success': return '✅';
    case 'warning': return '⚠️';
    case 'error': return '❌';
    case 'info': return 'ℹ️';
    default: return 'ℹ️';
  }
};

const getAlertSeverity = (type: AlertItem['type']): 'success' | 'warning' | 'error' | 'info' => {
  return type;
};

export const AlertsSection: React.FC<AlertsSectionProps> = ({ alerts, loading, error }) => {
  if (loading) {
    return (
      <Box>
        <Typography variant="h6" color="text.primary" sx={{ mb: 2, fontWeight: 'medium' }}>
          アクティブアラート
        </Typography>
        {[1, 2].map((index) => (
          <Box key={index} sx={{ mb: 1 }}>
            <Skeleton variant="rectangular" height={60} sx={{ borderRadius: 1 }} />
          </Box>
        ))}
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography variant="h6" color="text.primary" sx={{ mb: 2, fontWeight: 'medium' }}>
          アクティブアラート
        </Typography>
        <Alert severity="error">
          <AlertTitle>アラートデータの読み込みでエラーが発生しました</AlertTitle>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <Box>
        <Typography variant="h6" color="text.primary" sx={{ mb: 2, fontWeight: 'medium' }}>
          アクティブアラート
        </Typography>
        <Alert severity="info">
          <AlertTitle>アラートはありません</AlertTitle>
          現在、アクティブなアラートはありません。
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h6" color="text.primary" sx={{ mb: 2, fontWeight: 'medium' }}>
        アクティブアラート ({alerts.length})
      </Typography>
      
      {alerts.map((alert) => (
        <Alert 
          key={alert.id} 
          severity={getAlertSeverity(alert.type)}
          sx={{ 
            mb: 1,
            '& .MuiAlert-message': {
              width: '100%',
            },
          }}
        >
          <Box sx={{ width: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
              <Typography component="span" sx={{ fontSize: '1.1em' }}>
                {getAlertIcon(alert.type)}
              </Typography>
              <Box sx={{ flex: 1 }}>
                {alert.title && (
                  <Typography component="div" sx={{ fontWeight: 'medium', mb: 0.5 }}>
                    {alert.title}
                  </Typography>
                )}
                <Typography component="div" sx={{ fontSize: '0.875rem' }}>
                  {alert.message}
                </Typography>
                <Typography 
                  variant="caption" 
                  color="text.secondary" 
                  sx={{ display: 'block', mt: 0.5 }}
                >
                  {new Date(alert.created_at).toLocaleString('ja-JP')}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Alert>
      ))}
    </Box>
  );
};

export default AlertsSection;
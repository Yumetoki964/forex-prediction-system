import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Circle,
  Schedule,
  Speed,
} from '@mui/icons-material';
import { DataSource, useUpdatePriority } from '../hooks/useSourcesData';

interface SourcesListProps {
  sources: DataSource[];
  isLoading?: boolean;
}

const SourcesList: React.FC<SourcesListProps> = ({ sources, isLoading }) => {
  const updatePriorityMutation = useUpdatePriority();

  const getStatusColor = (status: DataSource['status']) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'warning':
        return 'warning';
      case 'offline':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: DataSource['status']) => {
    switch (status) {
      case 'online':
        return '稼働中';
      case 'warning':
        return '警告';
      case 'offline':
        return 'オフライン';
      default:
        return '不明';
    }
  };

  const getSourceIcon = (id: string) => {
    switch (id) {
      case 'boj':
        return '🏛️';
      case 'yahoo':
        return '📈';
      case 'alphavantage':
        return '🔑';
      default:
        return '🌐';
    }
  };

  const handlePriorityChange = (sourceId: string, currentPriority: number, delta: number) => {
    const newPriority = Math.max(1, Math.min(3, currentPriority + delta));
    if (newPriority !== currentPriority) {
      updatePriorityMutation.mutate({ sourceId, priority: newPriority });
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            データソース一覧
          </Typography>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            データソース情報を読み込み中...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" color="primary">
            データソース一覧
          </Typography>
          <Typography variant="body2" color="text.secondary">
            全 {sources.length} ソース
          </Typography>
        </Box>

        <Grid container spacing={2}>
          {sources.map((source) => (
            <Grid item xs={12} key={source.id}>
              <Card
                variant="outlined"
                sx={{
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: 3,
                    transform: 'translateY(-2px)',
                  },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {/* ソースアイコンと基本情報 */}
                    <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                      <Box
                        sx={{
                          width: 48,
                          height: 48,
                          bgcolor: 'background.paper',
                          borderRadius: 2,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '1.5rem',
                          mr: 2,
                          border: 1,
                          borderColor: 'divider',
                        }}
                      >
                        {getSourceIcon(source.id)}
                      </Box>
                      
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" sx={{ mb: 0.5 }}>
                          {source.name}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}
                        >
                          {source.url}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {source.type}
                        </Typography>
                      </Box>
                    </Box>

                    {/* ステータス */}
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Circle
                        sx={{
                          fontSize: 12,
                          mr: 1,
                          color: 
                            source.status === 'online' ? 'success.main' :
                            source.status === 'warning' ? 'warning.main' : 'error.main'
                        }}
                      />
                      <Chip
                        label={getStatusLabel(source.status)}
                        color={getStatusColor(source.status)}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  </Box>

                  {/* メトリクス */}
                  <Grid container spacing={3} sx={{ mt: 1 }}>
                    {/* 成功率 */}
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          成功率
                        </Typography>
                        <Typography 
                          variant="h6" 
                          sx={{ 
                            fontFamily: 'monospace', 
                            fontWeight: 'bold',
                            color: source.success_rate >= 95 ? 'success.main' : 
                                   source.success_rate >= 80 ? 'warning.main' : 'error.main'
                          }}
                        >
                          {source.success_rate}%
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={source.success_rate}
                          sx={{
                            mt: 0.5,
                            height: 4,
                            borderRadius: 2,
                            bgcolor: 'grey.300',
                            '& .MuiLinearProgress-bar': {
                              bgcolor: source.success_rate >= 95 ? 'success.main' : 
                                       source.success_rate >= 80 ? 'warning.main' : 'error.main'
                            }
                          }}
                        />
                      </Box>
                    </Grid>

                    {/* 最終更新 */}
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          最終更新
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 0.5 }}>
                          <Schedule sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                          <Typography variant="body2" fontFamily="monospace">
                            {source.last_update}
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>

                    {/* 応答時間 */}
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          応答時間
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 0.5 }}>
                          <Speed sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                          <Typography 
                            variant="body2" 
                            fontFamily="monospace"
                            color={
                              (source.response_time || 0) < 500 ? 'success.main' :
                              (source.response_time || 0) < 1000 ? 'warning.main' : 'error.main'
                            }
                          >
                            {source.response_time || 'N/A'}ms
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>

                    {/* 優先順位 */}
                    <Grid item xs={12} sm={3}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          優先順位
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mt: 0.5 }}>
                          <Tooltip title="優先順位を下げる">
                            <IconButton
                              size="small"
                              onClick={() => handlePriorityChange(source.id, source.priority, 1)}
                              disabled={source.priority >= 3 || updatePriorityMutation.isPending}
                              sx={{ p: 0.5 }}
                            >
                              <TrendingDown sx={{ fontSize: 16 }} />
                            </IconButton>
                          </Tooltip>
                          
                          <Typography 
                            variant="h6" 
                            sx={{ 
                              mx: 2, 
                              minWidth: 24, 
                              textAlign: 'center',
                              fontFamily: 'monospace',
                              color: 'primary.main',
                              fontWeight: 'bold'
                            }}
                          >
                            {source.priority}
                          </Typography>
                          
                          <Tooltip title="優先順位を上げる">
                            <IconButton
                              size="small"
                              onClick={() => handlePriorityChange(source.id, source.priority, -1)}
                              disabled={source.priority <= 1 || updatePriorityMutation.isPending}
                              sx={{ p: 0.5 }}
                            >
                              <TrendingUp sx={{ fontSize: 16 }} />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SourcesList;
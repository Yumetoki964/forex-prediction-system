import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Box,
  Chip,
  Skeleton,
  Paper
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Info,
  KeyboardArrowUp,
  KeyboardArrowDown
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface TradeRecord {
  trade_date: string;
  signal_type: string;
  entry_rate: number;
  exit_rate?: number;
  position_size: number;
  profit_loss?: number;
  holding_period?: number;
  confidence: number;
  market_volatility?: number;
}

interface TradeHistoryData {
  job_id: string;
  total_trades: number;
  page: number;
  page_size: number;
  total_pages: number;
  trades: TradeRecord[];
  profit_trades: number;
  loss_trades: number;
  average_profit: number;
  average_loss: number;
  largest_profit: number;
  largest_loss: number;
}

interface TradeHistoryTableProps {
  data?: TradeHistoryData;
  isLoading?: boolean;
  onPageChange?: (page: number, pageSize: number) => void;
}

const TradeHistoryTable: React.FC<TradeHistoryTableProps> = ({
  data,
  isLoading = false,
  onPageChange
}) => {
  const theme = useTheme();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [sortField, setSortField] = useState<keyof TradeRecord>('trade_date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  // ソート処理
  const handleSort = (field: keyof TradeRecord) => {
    const isAsc = sortField === field && sortDirection === 'asc';
    setSortDirection(isAsc ? 'desc' : 'asc');
    setSortField(field);
  };

  // ページング処理
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
    if (onPageChange) {
      onPageChange(newPage + 1, rowsPerPage); // API は1ベースのページング
    }
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPage(newRowsPerPage);
    setPage(0);
    if (onPageChange) {
      onPageChange(1, newRowsPerPage);
    }
  };

  // シグナルタイプの表示
  const formatSignalType = (signalType: string) => {
    const signalMap: Record<string, { label: string; color: 'success' | 'error' | 'info' }> = {
      'BUY': { label: 'Buy', color: 'success' },
      'SELL': { label: 'Sell', color: 'error' },
      'HOLD': { label: 'Hold', color: 'info' },
      'buy': { label: 'Buy', color: 'success' },
      'sell': { label: 'Sell', color: 'error' },
      'hold': { label: 'Hold', color: 'info' }
    };

    const signal = signalMap[signalType] || { label: signalType, color: 'info' as const };
    return (
      <Chip
        label={signal.label}
        color={signal.color}
        size="small"
        variant="outlined"
        icon={signal.color === 'success' ? <TrendingUp fontSize="small" /> : 
              signal.color === 'error' ? <TrendingDown fontSize="small" /> : 
              <Info fontSize="small" />}
      />
    );
  };

  // 損益の表示色
  const getProfitLossColor = (value?: number) => {
    if (value === undefined) return theme.palette.text.secondary;
    return value >= 0 ? theme.palette.success.main : theme.palette.error.main;
  };

  // 信頼度の表示
  const formatConfidence = (confidence: number) => {
    const getConfidenceColor = () => {
      if (confidence >= 80) return 'success';
      if (confidence >= 60) return 'warning';
      return 'error';
    };

    return (
      <Chip
        label={`${confidence.toFixed(0)}%`}
        color={getConfidenceColor()}
        size="small"
        variant="filled"
      />
    );
  };

  // 日付フォーマット
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  // 数値フォーマット
  const formatNumber = (value: number | undefined, decimals = 2, suffix = '') => {
    if (value === undefined) return '--';
    return `${value.toFixed(decimals)}${suffix}`;
  };

  // ソートされたデータ
  const sortedTrades = data?.trades ? [...data.trades].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    // 未定義値の処理
    if (aValue === undefined) aValue = 0;
    if (bValue === undefined) bValue = 0;

    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortDirection === 'asc' 
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    }

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    }

    return 0;
  }) : [];

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
            仮想取引履歴
          </Typography>
          <Box>
            {Array.from({ length: 10 }, (_, i) => (
              <Box key={i} sx={{ display: 'flex', gap: 2, mb: 1 }}>
                <Skeleton variant="text" width="15%" height={40} />
                <Skeleton variant="text" width="10%" height={40} />
                <Skeleton variant="text" width="10%" height={40} />
                <Skeleton variant="text" width="10%" height={40} />
                <Skeleton variant="text" width="10%" height={40} />
                <Skeleton variant="text" width="15%" height={40} />
                <Skeleton variant="text" width="10%" height={40} />
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.trades.length) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
            仮想取引履歴
          </Typography>
          <Box 
            sx={{ 
              height: 200, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              border: `1px dashed ${theme.palette.divider}`,
              borderRadius: 1,
              backgroundColor: theme.palette.background.default
            }}
          >
            <Typography variant="body2" color="text.secondary">
              バックテストを実行して取引履歴を表示
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" color="primary">
            仮想取引履歴
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip 
              label={`総取引: ${data.total_trades}`}
              size="small"
              variant="outlined"
            />
            <Chip 
              label={`利益取引: ${data.profit_trades}`}
              size="small"
              color="success"
              variant="outlined"
            />
            <Chip 
              label={`損失取引: ${data.loss_trades}`}
              size="small"
              color="error"
              variant="outlined"
            />
          </Box>
        </Box>

        {/* 統計サマリー */}
        <Box sx={{ 
          display: 'flex', 
          gap: 2, 
          mb: 2, 
          p: 2, 
          backgroundColor: theme.palette.background.default,
          borderRadius: 1 
        }}>
          <Typography variant="body2" color="text.secondary">
            <strong>平均利益:</strong> {formatNumber(data.average_profit, 2, ' USD')}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>平均損失:</strong> {formatNumber(data.average_loss, 2, ' USD')}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>最大利益:</strong> {formatNumber(data.largest_profit, 2, ' USD')}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>最大損失:</strong> {formatNumber(data.largest_loss, 2, ' USD')}
          </Typography>
        </Box>

        <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell>
                  <Box 
                    sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
                    onClick={() => handleSort('trade_date')}
                  >
                    取引日
                    {sortField === 'trade_date' && (
                      sortDirection === 'asc' ? <KeyboardArrowUp /> : <KeyboardArrowDown />
                    )}
                  </Box>
                </TableCell>
                <TableCell>売買</TableCell>
                <TableCell align="right">
                  <Box 
                    sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer', justifyContent: 'flex-end' }}
                    onClick={() => handleSort('entry_rate')}
                  >
                    エントリー
                    {sortField === 'entry_rate' && (
                      sortDirection === 'asc' ? <KeyboardArrowUp /> : <KeyboardArrowDown />
                    )}
                  </Box>
                </TableCell>
                <TableCell align="right">エグジット</TableCell>
                <TableCell align="right">
                  <Box 
                    sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer', justifyContent: 'flex-end' }}
                    onClick={() => handleSort('profit_loss')}
                  >
                    損益 (USD)
                    {sortField === 'profit_loss' && (
                      sortDirection === 'asc' ? <KeyboardArrowUp /> : <KeyboardArrowDown />
                    )}
                  </Box>
                </TableCell>
                <TableCell align="center">保有日数</TableCell>
                <TableCell align="center">信頼度</TableCell>
                <TableCell align="right">ボラティリティ</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedTrades.map((trade, index) => (
                <TableRow 
                  key={`${trade.trade_date}-${index}`}
                  hover
                  sx={{
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover
                    }
                  }}
                >
                  <TableCell sx={{ fontFamily: 'monospace' }}>
                    {formatDate(trade.trade_date)}
                  </TableCell>
                  <TableCell>
                    {formatSignalType(trade.signal_type)}
                  </TableCell>
                  <TableCell align="right" sx={{ fontFamily: 'monospace' }}>
                    {formatNumber(trade.entry_rate, 4)}
                  </TableCell>
                  <TableCell align="right" sx={{ fontFamily: 'monospace' }}>
                    {formatNumber(trade.exit_rate, 4)}
                  </TableCell>
                  <TableCell 
                    align="right" 
                    sx={{ 
                      fontFamily: 'monospace',
                      color: getProfitLossColor(trade.profit_loss),
                      fontWeight: 600
                    }}
                  >
                    {trade.profit_loss !== undefined && trade.profit_loss >= 0 && '+'}
                    {formatNumber(trade.profit_loss, 2)}
                  </TableCell>
                  <TableCell align="center" sx={{ fontFamily: 'monospace' }}>
                    {trade.holding_period ? `${trade.holding_period}日` : '--'}
                  </TableCell>
                  <TableCell align="center">
                    {formatConfidence(trade.confidence)}
                  </TableCell>
                  <TableCell align="right" sx={{ fontFamily: 'monospace' }}>
                    {formatNumber(trade.market_volatility, 3, '%')}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={data.total_trades}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="表示件数:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}-${to} / ${count !== -1 ? count : `${to}以上`}`
          }
        />
      </CardContent>
    </Card>
  );
};

export default TradeHistoryTable;
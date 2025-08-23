import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient, { API_ENDPOINTS } from '@/services/api/client';
import { WS_CONFIG } from '@/config/api.config';

// 型定義
export interface BacktestConfig {
  period: '1Y' | '3Y' | '5Y' | '10Y';
  initial_capital: number;
  risk_per_trade: number;
  stop_loss_pips: number;
}

export interface BacktestJob {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_date: string;
  end_date: string;
  created_at: string;
  estimated_completion_time?: number;
}

export interface BacktestResults {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  start_date: string;
  end_date: string;
  initial_capital: number;
  execution_time?: number;
  completed_at?: string;
  error_message?: string;
  total_return?: number;
  annualized_return?: number;
  volatility?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  total_trades?: number;
  winning_trades?: number;
  losing_trades?: number;
  win_rate?: number;
}

export interface BacktestMetrics {
  job_id: string;
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe_ratio: number;
  max_drawdown: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  win_rate: number;
  prediction_accuracy_1w?: number;
  prediction_accuracy_2w?: number;
  prediction_accuracy_3w?: number;
  prediction_accuracy_1m?: number;
  sortino_ratio?: number;
  calmar_ratio?: number;
  var_95?: number;
  monthly_returns?: number[];
  rolling_sharpe?: number[];
}

export interface TradeRecord {
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

export interface BacktestTrades {
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

// WebSocket進捗監視フック
export const useBacktestProgress = (_jobId: string | null) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);

  const startProgressMonitoring = useCallback((jobIdToMonitor: string) => {
    if (wsConnection) {
      wsConnection.close();
    }

    const wsUrl = `${WS_CONFIG.url}/ws/backtest/${jobIdToMonitor}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgress(data.progress || 0);
        setCurrentStep(data.current_step || '');
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    setWsConnection(ws);

    return () => {
      ws.close();
    };
  }, [wsConnection]);

  const stopProgressMonitoring = useCallback(() => {
    if (wsConnection) {
      wsConnection.close();
      setWsConnection(null);
    }
    setProgress(0);
    setCurrentStep('');
  }, [wsConnection]);

  return {
    progress,
    currentStep,
    startProgressMonitoring,
    stopProgressMonitoring
  };
};

// バックテスト実行フック
export const useRunBacktest = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (config: BacktestConfig): Promise<BacktestJob> => {
      // 期間を日付に変換
      const endDate = new Date();
      const startDate = new Date(endDate);
      
      switch (config.period) {
        case '1Y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        case '3Y':
          startDate.setFullYear(endDate.getFullYear() - 3);
          break;
        case '5Y':
          startDate.setFullYear(endDate.getFullYear() - 5);
          break;
        case '10Y':
          startDate.setFullYear(endDate.getFullYear() - 10);
          break;
      }

      const requestData = {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
        initial_capital: config.initial_capital,
        prediction_model_type: 'ensemble',
        prediction_model_config: {
          risk_per_trade: config.risk_per_trade / 100, // パーセントから小数に変換
          stop_loss_pips: config.stop_loss_pips
        }
      };

      const response = await apiClient.post(API_ENDPOINTS.backtest.run, requestData);
      return response.data;
    },
    onSuccess: (data) => {
      // キャッシュを更新
      queryClient.setQueryData(['backtest', 'job', data.job_id], data);
    },
    onError: (error) => {
      console.error('Backtest execution error:', error);
    }
  });
};

// バックテスト結果取得フック
export const useBacktestResults = (jobId: string | null) => {
  return useQuery({
    queryKey: ['backtest', 'results', jobId],
    queryFn: async (): Promise<BacktestResults> => {
      if (!jobId) throw new Error('Job ID is required');
      
      const response = await apiClient.get(API_ENDPOINTS.backtest.results(jobId));
      return response.data;
    },
    enabled: !!jobId,
    refetchInterval: (query) => {
      // まだ実行中の場合は5秒間隔で更新
      const data = query.state.data as BacktestResults | undefined;
      return data?.status === 'running' ? 5000 : false;
    },
    staleTime: 30000, // 30秒間キャッシュを有効とする
  });
};

// バックテスト評価指標取得フック
export const useBacktestMetrics = (jobId: string | null) => {
  return useQuery({
    queryKey: ['backtest', 'metrics', jobId],
    queryFn: async (): Promise<BacktestMetrics> => {
      if (!jobId) throw new Error('Job ID is required');
      
      const response = await apiClient.get(API_ENDPOINTS.backtest.metrics(jobId));
      return response.data;
    },
    enabled: !!jobId,
    staleTime: 60000, // 1分間キャッシュを有効とする
  });
};

// バックテスト取引履歴取得フック
export const useBacktestTrades = (jobId: string | null, page: number = 1, pageSize: number = 100) => {
  return useQuery({
    queryKey: ['backtest', 'trades', jobId, page, pageSize],
    queryFn: async (): Promise<BacktestTrades> => {
      if (!jobId) throw new Error('Job ID is required');
      
      const response = await apiClient.get(API_ENDPOINTS.backtest.trades(jobId), {
        params: { page, page_size: pageSize }
      });
      return response.data;
    },
    enabled: !!jobId,
    staleTime: 60000, // 1分間キャッシュを有効とする
  });
};

// 統合バックテストフック - すべての機能をまとめたもの
export const useBacktest = () => {
  const queryClient = useQueryClient();
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  
  const runBacktest = useRunBacktest();
  const results = useBacktestResults(currentJobId);
  const metrics = useBacktestMetrics(currentJobId);
  const trades = useBacktestTrades(currentJobId);
  const progress = useBacktestProgress(currentJobId);

  const executeBacktest = useCallback(async (config: BacktestConfig) => {
    try {
      const job = await runBacktest.mutateAsync(config);
      setCurrentJobId(job.job_id);
      
      // WebSocket監視開始
      progress.startProgressMonitoring(job.job_id);
      
      return job;
    } catch (error) {
      console.error('Failed to execute backtest:', error);
      throw error;
    }
  }, [runBacktest, progress]);

  const cancelBacktest = useCallback(() => {
    progress.stopProgressMonitoring();
    setCurrentJobId(null);
    
    // 関連クエリをクリア
    queryClient.removeQueries({ queryKey: ['backtest', 'results', currentJobId] });
    queryClient.removeQueries({ queryKey: ['backtest', 'metrics', currentJobId] });
    queryClient.removeQueries({ queryKey: ['backtest', 'trades', currentJobId] });
  }, [currentJobId, progress, queryClient]);

  return {
    // 状態
    currentJobId,
    isRunning: runBacktest.isPending || (results.data as BacktestResults)?.status === 'running',
    
    // データ
    results: results.data,
    metrics: metrics.data,
    trades: trades.data,
    
    // 進捗
    progress: progress.progress,
    currentStep: progress.currentStep,
    
    // アクション
    executeBacktest,
    cancelBacktest,
    
    // ローディング状態
    isExecuting: runBacktest.isPending,
    isLoadingResults: results.isLoading,
    isLoadingMetrics: metrics.isLoading,
    isLoadingTrades: trades.isLoading,
    
    // エラー状態
    executionError: runBacktest.error,
    resultsError: results.error,
    metricsError: metrics.error,
    tradesError: trades.error,
  };
};
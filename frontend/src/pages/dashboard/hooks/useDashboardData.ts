import { useQuery } from '@tanstack/react-query';
import apiClient, { API_ENDPOINTS } from '@/services/api/client';
import type { 
  CurrentRateResponse,
  LatestPredictionsResponse,
  CurrentSignalResponse
} from '@/generated/Api';

// 現在レート取得
export const useCurrentRate = () => {
  return useQuery({
    queryKey: ['rates', 'current'],
    queryFn: async (): Promise<CurrentRateResponse> => {
      const response = await apiClient.get(API_ENDPOINTS.rates.current);
      return response.data;
    },
    refetchInterval: 5 * 60 * 1000, // 5分毎に更新
    staleTime: 2 * 60 * 1000, // 2分間はフレッシュとみなす
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// 最新予測取得
export const useLatestPredictions = () => {
  return useQuery({
    queryKey: ['predictions', 'latest'],
    queryFn: async (): Promise<LatestPredictionsResponse> => {
      const response = await apiClient.get(API_ENDPOINTS.predictions.latest);
      return response.data;
    },
    refetchInterval: 30 * 60 * 1000, // 30分毎に更新
    staleTime: 15 * 60 * 1000, // 15分間はフレッシュとみなす
    retry: 2,
  });
};

// 現在の売買シグナル取得
export const useCurrentSignal = () => {
  return useQuery({
    queryKey: ['signals', 'current'],
    queryFn: async (): Promise<CurrentSignalResponse> => {
      const response = await apiClient.get(API_ENDPOINTS.signals.current);
      return response.data;
    },
    refetchInterval: 15 * 60 * 1000, // 15分毎に更新
    staleTime: 10 * 60 * 1000, // 10分間はフレッシュとみなす
    retry: 2,
  });
};

// リスク指標取得
export const useRiskMetrics = () => {
  return useQuery({
    queryKey: ['metrics', 'risk'],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.metrics.risk);
      return response.data;
    },
    refetchInterval: 60 * 60 * 1000, // 1時間毎に更新
    staleTime: 30 * 60 * 1000, // 30分間はフレッシュとみなす
    retry: 2,
  });
};

// アクティブアラート取得
export const useActiveAlerts = () => {
  return useQuery({
    queryKey: ['alerts', 'active'],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.alerts.active);
      return response.data;
    },
    refetchInterval: 10 * 60 * 1000, // 10分毎に更新
    staleTime: 5 * 60 * 1000, // 5分間はフレッシュとみなす
    retry: 2,
  });
};

// ダッシュボードの全データを取得する統合フック
export const useDashboardData = () => {
  const currentRate = useCurrentRate();
  const predictions = useLatestPredictions();
  const signal = useCurrentSignal();
  const riskMetrics = useRiskMetrics();
  const alerts = useActiveAlerts();

  return {
    currentRate,
    predictions,
    signal,
    riskMetrics,
    alerts,
    // 全体のローディング状態
    isLoading: currentRate.isLoading || predictions.isLoading || signal.isLoading || riskMetrics.isLoading || alerts.isLoading,
    // 一つでもエラーがあればエラー状態
    hasError: currentRate.isError || predictions.isError || signal.isError || riskMetrics.isError || alerts.isError,
    // エラー情報をまとめて取得
    errors: {
      currentRate: currentRate.error?.message,
      predictions: predictions.error?.message,
      signal: signal.error?.message,
      riskMetrics: riskMetrics.error?.message,
      alerts: alerts.error?.message,
    },
    // 手動リフレッシュ関数
    refetch: () => {
      currentRate.refetch();
      predictions.refetch();
      signal.refetch();
      riskMetrics.refetch();
      alerts.refetch();
    },
  };
};
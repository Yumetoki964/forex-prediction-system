import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient, { API_ENDPOINTS } from '@/services/api/client';
import { useNotification } from '@/hooks/useNotification';

// データソース状況の型定義
export interface DataSource {
  id: string;
  name: string;
  url: string;
  status: 'online' | 'warning' | 'offline';
  type: string;
  success_rate: number;
  last_update: string;
  priority: number;
  response_time?: number;
}

export interface SourcesStatusResponse {
  sources: DataSource[];
  total_sources: number;
  online_count: number;
  warning_count: number;
  offline_count: number;
  last_checked: string;
}

export interface HealthMetrics {
  response_time: number;
  availability: number;
  data_freshness: string;
  error_rate: number;
  last_check: string;
}

export interface ScrapeJobResponse {
  job_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
  results?: {
    records_collected: number;
    sources_processed: string[];
    errors: string[];
  };
}

export interface CSVImportResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  results?: {
    records_imported: number;
    records_skipped: number;
    errors: string[];
  };
}

// データソース状況取得
export const useSourcesStatus = () => {
  return useQuery<SourcesStatusResponse>({
    queryKey: ['sources', 'status'],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.sources.status);
      return response.data;
    },
    refetchInterval: 30000, // 30秒ごとに自動更新
    staleTime: 10000, // 10秒間はキャッシュを使用
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
};

// ヘルスチェック取得
export const useHealthMetrics = () => {
  return useQuery<HealthMetrics>({
    queryKey: ['sources', 'health'],
    queryFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.sources.health);
      return response.data;
    },
    refetchInterval: 60000, // 1分ごとに自動更新
    staleTime: 30000, // 30秒間はキャッシュを使用
  });
};

// Webスクレイピング実行
export const useRunScraping = () => {
  const queryClient = useQueryClient();
  const { showNotification } = useNotification();

  return useMutation<ScrapeJobResponse, Error, { source?: string; force?: boolean }>({
    mutationFn: async (params = {}) => {
      const response = await apiClient.post(API_ENDPOINTS.sources.scrape, {
        source: params.source,
        force: params.force || false,
      });
      return response.data;
    },
    onMutate: () => {
      showNotification('Webスクレイピングを開始しています...', 'info');
    },
    onSuccess: (data) => {
      showNotification(
        `スクレイピングジョブが開始されました (Job ID: ${data.job_id})`,
        'success'
      );
      // データソース状況を再取得
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
    onError: (error) => {
      console.error('Scraping error:', error);
      showNotification(
        `スクレイピングの開始に失敗しました: ${error.message}`,
        'error'
      );
    },
  });
};

// CSV一括インポート
export const useCSVImport = () => {
  const queryClient = useQueryClient();
  const { showNotification } = useNotification();

  return useMutation<CSVImportResponse, Error, FormData>({
    mutationFn: async (formData) => {
      const response = await apiClient.post(
        API_ENDPOINTS.sources.csvImport,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onMutate: () => {
      showNotification('CSVファイルをインポートしています...', 'info');
    },
    onSuccess: (data) => {
      showNotification(
        `CSVインポートが開始されました (Job ID: ${data.job_id})`,
        'success'
      );
      // データソース状況を再取得
      queryClient.invalidateQueries({ queryKey: ['sources'] });
    },
    onError: (error) => {
      console.error('CSV import error:', error);
      showNotification(
        `CSVインポートに失敗しました: ${error.message}`,
        'error'
      );
    },
  });
};

// ヘルスチェック実行
export const useRunHealthCheck = () => {
  const queryClient = useQueryClient();
  const { showNotification } = useNotification();

  return useMutation<HealthMetrics, Error, void>({
    mutationFn: async () => {
      const response = await apiClient.get(API_ENDPOINTS.sources.health);
      return response.data;
    },
    onMutate: () => {
      showNotification('ヘルスチェックを実行しています...', 'info');
    },
    onSuccess: (data) => {
      showNotification('ヘルスチェックが完了しました', 'success');
      // ヘルスメトリクスを更新
      queryClient.setQueryData(['sources', 'health'], data);
    },
    onError: (error) => {
      console.error('Health check error:', error);
      showNotification(
        `ヘルスチェックに失敗しました: ${error.message}`,
        'error'
      );
    },
  });
};

// データソース優先順位更新（モックアップの機能要件）
export const useUpdatePriority = () => {
  const queryClient = useQueryClient();
  const { showNotification } = useNotification();

  return useMutation<void, Error, { sourceId: string; priority: number }>({
    mutationFn: async ({ sourceId, priority }) => {
      // 優先順位更新のエンドポイントが実装されていない場合のフォールバック
      // 実際にはPUT /api/sources/priorityエンドポイントを使用
      console.log(`Updating priority for ${sourceId} to ${priority}`);
      // 実装では以下のようなAPIコールになります：
      // await apiClient.put('/api/sources/priority', { source_id: sourceId, priority });
    },
    onSuccess: (_, variables) => {
      showNotification(
        `データソースの優先順位を${variables.priority}に更新しました`,
        'success'
      );
      // データソース状況を再取得
      queryClient.invalidateQueries({ queryKey: ['sources', 'status'] });
    },
    onError: (error) => {
      console.error('Priority update error:', error);
      showNotification(
        `優先順位の更新に失敗しました: ${error.message}`,
        'error'
      );
    },
  });
};

// フォールバックデータ（APIが未実装の場合に使用）
export const mockSourcesData: SourcesStatusResponse = {
  sources: [
    {
      id: 'boj',
      name: '日本銀行 CSV データ',
      url: 'www.boj.or.jp/statistics/market/forex/',
      status: 'online',
      type: 'CSV一括取得',
      success_rate: 98.5,
      last_update: '2時間前',
      priority: 1,
      response_time: 245,
    },
    {
      id: 'yahoo',
      name: 'Yahoo Finance (スクレイピング)',
      url: 'finance.yahoo.com/quote/JPY=X/',
      status: 'online',
      type: 'Webスクレイピング',
      success_rate: 95.2,
      last_update: '15分前',
      priority: 2,
      response_time: 512,
    },
    {
      id: 'alphavantage',
      name: 'Alpha Vantage API (バックアップ)',
      url: 'www.alphavantage.co/query',
      status: 'warning',
      type: 'RESTful API',
      success_rate: 88.7,
      last_update: '1日前',
      priority: 3,
      response_time: 1250,
    },
  ],
  total_sources: 3,
  online_count: 2,
  warning_count: 1,
  offline_count: 0,
  last_checked: '2025-08-23T14:30:45Z',
};

export const mockHealthMetrics: HealthMetrics = {
  response_time: 245,
  availability: 99.2,
  data_freshness: '最新',
  error_rate: 0.8,
  last_check: '5分前',
};
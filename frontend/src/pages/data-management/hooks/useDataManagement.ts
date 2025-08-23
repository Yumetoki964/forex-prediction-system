import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/services/api-client';

// 型定義 - モックアップから抽出した構造に基づく
export interface DataStatus {
  coverage: {
    total_expected_days: number;
    actual_data_days: number;
    missing_days: number;
    coverage_rate: number;
    interpolated_days: number;
    earliest_date: string;
    latest_date: string;
    last_update: string;
  };
  quality: {
    completeness_rate: number;
    accuracy_rate: number;
    consistency_rate: number;
    outlier_count: number;
    duplicate_count: number;
    last_quality_check: string;
    quality_score: number;
  };
  schedule: {
    auto_collection_enabled: boolean;
    next_collection_time: string;
    collection_frequency: string;
    last_successful_collection: string;
    last_failed_collection: string | null;
    consecutive_failures: number;
  };
  system_health: string;
  active_issues: string[];
  status_generated_at: string;
}

export interface DataQualityReport {
  report_id: string;
  report_date: string;
  analysis_period: {
    start: string;
    end: string;
  };
  overall_quality_score: number;
  data_health_status: string;
  quality_metrics: {
    completeness_rate: number;
    accuracy_rate: number;
    consistency_rate: number;
    outlier_count: number;
    duplicate_count: number;
    last_quality_check: string;
    quality_score: number;
  };
  source_scores: Array<{
    source_name: string;
    completeness_score: number;
    accuracy_score: number;
    last_update: string;
  }>;
  quality_issues: Array<{
    issue_id: string;
    issue_type: string;
    severity: string;
    description: string;
    affected_dates: string[];
    detected_at: string;
  }>;
  quality_trends: {
    completeness_change: number;
    accuracy_change: number;
    consistency_change: number;
    overall_change: number;
  };
  recommendations: string[];
  next_analysis_scheduled: string;
}

export interface DataSource {
  id: number;
  name: string;
  source_type: string;
  status: string;
  url: string | null;
  priority: number;
  success_rate: number;
  avg_response_time: number;
  last_success_at: string;
  last_failure_at: string | null;
  failure_count: number;
  rate_limit_requests: number | null;
  rate_limit_period: number | null;
  daily_request_count: number;
  remaining_requests: number | null;
  created_at: string;
  updated_at: string;
}

export interface DataSourcesResponse {
  sources: DataSource[];
  health: {
    total_sources: number;
    active_sources: number;
    error_sources: number;
    maintenance_sources: number;
    overall_health: string;
    health_score: number;
    has_backup_sources: boolean;
    primary_source_available: boolean;
  };
  last_health_check: string;
  next_health_check: string;
  recommendations: string[];
  response_generated_at: string;
}

export interface DataCollectionRequest {
  sources?: string[] | null;
  force_update?: boolean;
  source_priority?: string[] | null;
}

export interface DataCollectionResponse {
  collection_id: string;
  status: string;
  estimated_duration: number;
  sources_to_collect: string[];
  started_at: string;
}

export interface DataRepairRequest {
  method: 'linear' | 'spline' | 'moving-average';
  period: 'all' | 'recent' | 'custom';
  custom_start_date?: string;
  custom_end_date?: string;
}

export interface DataRepairResponse {
  repair_id: string;
  affected_days: number;
  estimated_duration: number;
  repair_method: string;
  started_at: string;
  status: string;
}

// データ収集状況取得
export const useDataStatus = () => {
  return useQuery<DataStatus>({
    queryKey: ['data', 'status'],
    queryFn: async () => {
      const response = await apiClient.get<DataStatus>('/api/data/status');
      return response.data;
    },
    refetchInterval: 5 * 60 * 1000, // 5分間隔で自動更新
    staleTime: 2 * 60 * 1000, // 2分間はキャッシュを使用
  });
};

// データ品質レポート取得
export const useDataQuality = (periodDays: number = 7) => {
  return useQuery<DataQualityReport>({
    queryKey: ['data', 'quality', periodDays],
    queryFn: async () => {
      const response = await apiClient.get<DataQualityReport>('/api/data/quality', {
        params: { period_days: periodDays },
      });
      return response.data;
    },
    refetchInterval: 5 * 60 * 1000, // 5分間隔で自動更新
    staleTime: 2 * 60 * 1000, // 2分間はキャッシュを使用
  });
};

// データソース状況取得
export const useDataSources = (includeInactive: boolean = false) => {
  return useQuery<DataSourcesResponse>({
    queryKey: ['data', 'sources', includeInactive],
    queryFn: async () => {
      const response = await apiClient.get<DataSourcesResponse>('/api/data/sources', {
        params: { include_inactive: includeInactive },
      });
      return response.data;
    },
    refetchInterval: 2 * 60 * 1000, // 2分間隔で自動更新
    staleTime: 60 * 1000, // 1分間はキャッシュを使用
  });
};

// 手動データ収集実行
export const useDataCollection = () => {
  const queryClient = useQueryClient();

  return useMutation<DataCollectionResponse, Error, DataCollectionRequest>({
    mutationFn: async (request: DataCollectionRequest) => {
      const response = await apiClient.post<DataCollectionResponse>('/api/data/collect', request);
      return response.data;
    },
    onSuccess: () => {
      // データ収集後、関連データを無効化して再取得
      queryClient.invalidateQueries({ queryKey: ['data', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['data', 'quality'] });
      queryClient.invalidateQueries({ queryKey: ['data', 'sources'] });
    },
    onError: (error) => {
      console.error('データ収集エラー:', error);
    },
  });
};

// データ修復実行
export const useDataRepair = () => {
  const queryClient = useQueryClient();

  return useMutation<DataRepairResponse, Error, DataRepairRequest>({
    mutationFn: async (request: DataRepairRequest) => {
      const response = await apiClient.post<DataRepairResponse>('/api/data/repair', request);
      return response.data;
    },
    onSuccess: () => {
      // データ修復後、関連データを無効化して再取得
      queryClient.invalidateQueries({ queryKey: ['data', 'status'] });
      queryClient.invalidateQueries({ queryKey: ['data', 'quality'] });
    },
    onError: (error) => {
      console.error('データ修復エラー:', error);
    },
  });
};

// データソースヘルスチェック
export const useSourceHealthCheck = () => {
  const queryClient = useQueryClient();

  return useMutation<any, Error, string>({
    mutationFn: async (sourceName: string) => {
      const response = await apiClient.post(`/api/sources/health/${sourceName}`);
      return response.data;
    },
    onSuccess: () => {
      // ヘルスチェック後、データソース情報を更新
      queryClient.invalidateQueries({ queryKey: ['data', 'sources'] });
    },
    onError: (error) => {
      console.error('ヘルスチェックエラー:', error);
    },
  });
};
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_CONFIG } from '@/config/api.config';

// APIクライアントの作成
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  withCredentials: API_CONFIG.withCredentials,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// リクエストインターセプター
apiClient.interceptors.request.use(
  (config) => {
    // リクエスト前に実行される処理
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // レスポンス成功時の処理
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error: AxiosError) => {
    // レスポンスエラー時の処理
    console.error('API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      message: error.message,
    });

    // エラーの分類と処理
    if (error.response) {
      // サーバーがエラーレスポンスを返した場合
      const { status } = error.response;
      
      switch (status) {
        case 401:
          console.error('認証エラー: ログインが必要です');
          break;
        case 403:
          console.error('権限エラー: アクセス権限がありません');
          break;
        case 404:
          console.error('リソースが見つかりません');
          break;
        case 500:
          console.error('サーバー内部エラーが発生しました');
          break;
        default:
          console.error(`サーバーエラー: ${status} ${error.response.statusText}`);
      }
    } else if (error.request) {
      // リクエストは送信されたがレスポンスがない場合
      console.error('ネットワークエラー: サーバーに接続できません');
    } else {
      // その他のエラー
      console.error('リクエスト設定エラー:', error.message);
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// API エンドポイント定義
export const API_ENDPOINTS = {
  // 現在レートと予測関連
  rates: {
    current: '/api/rates/current',
  },
  predictions: {
    latest: '/api/predictions/latest',
    detailed: '/api/predictions/detailed',
  },
  signals: {
    current: '/api/signals/current',
  },
  metrics: {
    risk: '/api/metrics/risk',
  },
  alerts: {
    active: '/api/alerts/active',
  },
  
  // チャートと分析
  charts: {
    historical: '/api/charts/historical',
  },
  indicators: {
    technical: '/api/indicators/technical',
    economic: '/api/indicators/economic',
  },
  
  // バックテスト
  backtest: {
    run: '/api/backtest/run',
    results: (jobId: string) => `/api/backtest/results/${jobId}`,
    metrics: (jobId: string) => `/api/backtest/metrics/${jobId}`,
    trades: (jobId: string) => `/api/backtest/trades/${jobId}`,
  },
  
  // データ管理
  data: {
    status: '/api/data/status',
    collect: '/api/data/collect',
    quality: '/api/data/quality',
    repair: '/api/data/repair',
    sources: '/api/data/sources',
  },
  
  // 設定
  settings: {
    prediction: '/api/settings/prediction',
    alerts: '/api/settings/alerts',
    test: '/api/settings/test',
  },
  
  // データソース管理
  sources: {
    status: '/api/sources/status',
    scrape: '/api/sources/scrape',
    csvImport: '/api/sources/csv-import',
    health: '/api/sources/health',
  },
} as const;
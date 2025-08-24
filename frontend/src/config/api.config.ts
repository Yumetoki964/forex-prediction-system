// API設定
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  withCredentials: false,
} as const;

// WebSocket設定
export const WS_CONFIG = {
  url: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  reconnectInterval: 3000,
  maxReconnectAttempts: 5,
} as const;

// アプリ設定
export const APP_CONFIG = {
  name: import.meta.env.VITE_APP_NAME || 'Forex Prediction System',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  updateInterval: 5 * 60 * 1000, // 5分間隔での自動更新
} as const;

// 環境変数の検証
if (!API_CONFIG.baseURL) {
  console.error('VITE_API_URL環境変数が設定されていません。.env.localファイルを確認してください。');
}

console.log('API Configuration:', {
  baseURL: API_CONFIG.baseURL,
  wsURL: WS_CONFIG.url,
  appName: APP_CONFIG.name,
});
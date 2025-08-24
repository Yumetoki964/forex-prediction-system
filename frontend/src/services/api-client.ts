/**
 * API接続テスト用クライアント
 */
import axios from 'axios';

// API基底URL
const API_BASE_URL = 'http://localhost:8000';

// APIクライアントインスタンス
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * 基本的なAPI接続テスト
 */
export const testApiConnection = async () => {
  try {
    console.log('🔌 API接続テスト開始...');
    console.log('API Base URL:', API_BASE_URL);
    
    // ヘルスチェック
    const healthResponse = await apiClient.get('/health');
    console.log('✅ ヘルスチェック成功:', healthResponse.data);
    
    // ルートエンドポイント
    const rootResponse = await apiClient.get('/');
    console.log('✅ ルートエンドポイント成功:', rootResponse.data);
    
    console.log('🎉 API接続テスト完了');
    return { success: true, message: 'API接続テスト成功' };
    
  } catch (error) {
    console.error('❌ API接続テストでエラー:', error);
    return { success: false, error };
  }
};

export default apiClient;
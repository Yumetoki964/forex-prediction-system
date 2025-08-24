import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { PredictionSettings } from '../components/PredictionSettingsForm';
import { AlertSettings } from '../components/AlertSettingsForm';

// API設定
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 設定テストの結果型
export interface SettingsTestResult {
  success: boolean;
  message: string;
  test_results: {
    prediction_accuracy: number;
    confidence_score: number;
  };
}

// 予測設定取得
export const usePredictionSettings = () => {
  return useQuery({
    queryKey: ['settings', 'prediction'],
    queryFn: async (): Promise<PredictionSettings> => {
      const response = await fetch(`${API_BASE_URL}/api/settings/prediction`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch prediction settings');
      }
      
      return response.json();
    },
    staleTime: 1000 * 60 * 5, // 5分間キャッシュ
    retry: 3,
  });
};

// 予測設定更新
export const usePredictionSettingsUpdate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (settings: PredictionSettings): Promise<{ success: boolean; message: string }> => {
      const response = await fetch(`${API_BASE_URL}/api/settings/prediction`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to update prediction settings');
      }
      
      return response.json();
    },
    onSuccess: () => {
      // 設定更新後にキャッシュを無効化
      queryClient.invalidateQueries({ queryKey: ['settings', 'prediction'] });
    },
    onError: (error) => {
      console.error('Prediction settings update error:', error);
    },
  });
};

// アラート設定取得
export const useAlertSettings = () => {
  return useQuery({
    queryKey: ['settings', 'alerts'],
    queryFn: async (): Promise<AlertSettings> => {
      const response = await fetch(`${API_BASE_URL}/api/settings/alerts`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch alert settings');
      }
      
      return response.json();
    },
    staleTime: 1000 * 60 * 5, // 5分間キャッシュ
    retry: 3,
  });
};

// アラート設定更新
export const useAlertSettingsUpdate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (settings: AlertSettings): Promise<{ success: boolean; message: string }> => {
      const response = await fetch(`${API_BASE_URL}/api/settings/alerts`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to update alert settings');
      }
      
      return response.json();
    },
    onSuccess: () => {
      // 設定更新後にキャッシュを無効化
      queryClient.invalidateQueries({ queryKey: ['settings', 'alerts'] });
    },
    onError: (error) => {
      console.error('Alert settings update error:', error);
    },
  });
};

// 設定テスト実行
export const useSettingsTest = () => {
  return useMutation({
    mutationFn: async (settings: PredictionSettings): Promise<SettingsTestResult> => {
      const response = await fetch(`${API_BASE_URL}/api/settings/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prediction_settings: settings,
        }),
      });
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to test settings');
      }
      
      return response.json();
    },
    onError: (error) => {
      console.error('Settings test error:', error);
    },
  });
};
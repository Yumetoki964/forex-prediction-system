import { useEffect, useCallback, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { WS_CONFIG } from '@/config/api.config';

interface RealtimeMessage {
  type: 'rate_update' | 'signal_update' | 'alert_created' | 'prediction_update';
  data: any;
  timestamp: string;
}

export const useRealtimeUpdates = () => {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    try {
      // 既存の接続をクリーンアップ
      if (wsRef.current) {
        wsRef.current.close();
      }

      wsRef.current = new WebSocket(`${WS_CONFIG.url}/ws/dashboard`);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected to dashboard updates');
        reconnectAttemptsRef.current = 0;
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: RealtimeMessage = JSON.parse(event.data);
          
          switch (message.type) {
            case 'rate_update':
              // 現在レートのキャッシュを更新
              queryClient.setQueryData(['rates', 'current'], message.data);
              break;
              
            case 'signal_update':
              // シグナルのキャッシュを更新
              queryClient.setQueryData(['signals', 'current'], message.data);
              break;
              
            case 'prediction_update':
              // 予測のキャッシュを無効化（再取得をトリガー）
              queryClient.invalidateQueries({ queryKey: ['predictions', 'latest'] });
              break;
              
            case 'alert_created':
              // アラートのキャッシュを無効化
              queryClient.invalidateQueries({ queryKey: ['alerts', 'active'] });
              // ブラウザ通知（ユーザーが許可した場合）
              if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('新しいアラート', {
                  body: message.data.message || 'アラートが発生しました',
                  icon: '/favicon.ico',
                });
              }
              break;
              
            default:
              console.log('Unknown message type:', message.type);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        
        // リコネクトを試行（最大試行回数内で）
        if (reconnectAttemptsRef.current < WS_CONFIG.maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          console.log(`Attempting to reconnect... (${reconnectAttemptsRef.current}/${WS_CONFIG.maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, WS_CONFIG.reconnectInterval);
        } else {
          console.error('Max reconnection attempts reached. Giving up.');
        }
      };
    } catch (error) {
      console.error('Failed to establish WebSocket connection:', error);
    }
  }, [queryClient]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    reconnectAttemptsRef.current = 0;
  }, []);

  const requestNotificationPermission = useCallback(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        console.log('Notification permission:', permission);
      });
    }
  }, []);

  useEffect(() => {
    // コンポーネントマウント時にWebSocket接続を開始
    connect();
    
    // ブラウザ通知の許可をリクエスト
    requestNotificationPermission();

    // クリーンアップ
    return () => {
      disconnect();
    };
  }, [connect, disconnect, requestNotificationPermission]);

  // ページの可視性が変わった時の処理
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        // ページがアクティブになった時、データを更新
        queryClient.invalidateQueries({ queryKey: ['rates', 'current'] });
        queryClient.invalidateQueries({ queryKey: ['signals', 'current'] });
        queryClient.invalidateQueries({ queryKey: ['alerts', 'active'] });
        
        // WebSocket接続が切れている場合は再接続
        if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
          connect();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [connect, queryClient]);

  return {
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
    reconnectAttempts: reconnectAttemptsRef.current,
    maxReconnectAttempts: WS_CONFIG.maxReconnectAttempts,
    connect,
    disconnect,
  };
};
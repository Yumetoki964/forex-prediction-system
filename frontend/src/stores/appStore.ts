import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// アプリケーション全体の状態の型定義
interface Notification {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  timestamp: Date;
  autoClose?: boolean;
}

interface AppState {
  // UI状態
  sidebarOpen: boolean;
  loading: boolean;
  
  // 通知システム
  notifications: Notification[];
  
  // 最終更新時刻
  lastUpdated: Date | null;
  
  // オートリフレッシュ設定
  autoRefresh: boolean;
  refreshInterval: number; // ミリ秒
  
  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setLoading: (loading: boolean) => void;
  
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  updateLastUpdated: () => void;
  
  setAutoRefresh: (enabled: boolean) => void;
  setRefreshInterval: (interval: number) => void;
}

// Zustandストアの作成
export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      // 初期状態
      sidebarOpen: false,
      loading: false,
      notifications: [],
      lastUpdated: null,
      autoRefresh: true,
      refreshInterval: 5 * 60 * 1000, // 5分間隔

      // UI アクション
      toggleSidebar: () => 
        set((state) => ({ sidebarOpen: !state.sidebarOpen }), false, 'toggleSidebar'),
      
      setSidebarOpen: (open: boolean) => 
        set({ sidebarOpen: open }, false, 'setSidebarOpen'),
      
      setLoading: (loading: boolean) => 
        set({ loading }, false, 'setLoading'),

      // 通知アクション
      addNotification: (notification) => {
        const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newNotification: Notification = {
          ...notification,
          id,
          timestamp: new Date(),
          autoClose: notification.autoClose ?? true,
        };
        
        set(
          (state) => ({
            notifications: [newNotification, ...state.notifications],
          }),
          false,
          'addNotification'
        );

        // 自動削除設定
        if (newNotification.autoClose) {
          setTimeout(() => {
            get().removeNotification(id);
          }, 5000); // 5秒後に自動削除
        }
      },

      removeNotification: (id: string) =>
        set(
          (state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }),
          false,
          'removeNotification'
        ),

      clearNotifications: () =>
        set({ notifications: [] }, false, 'clearNotifications'),

      // 更新時刻管理
      updateLastUpdated: () =>
        set({ lastUpdated: new Date() }, false, 'updateLastUpdated'),

      // オートリフレッシュ設定
      setAutoRefresh: (enabled: boolean) =>
        set({ autoRefresh: enabled }, false, 'setAutoRefresh'),

      setRefreshInterval: (interval: number) =>
        set({ refreshInterval: interval }, false, 'setRefreshInterval'),
    }),
    {
      name: 'forex-app-store', // デバッグ用の名前
    }
  )
);

// セレクタ関数（パフォーマンス最適化）
export const selectNotifications = (state: AppState) => state.notifications;
export const selectSidebarOpen = (state: AppState) => state.sidebarOpen;
export const selectLoading = (state: AppState) => state.loading;
export const selectLastUpdated = (state: AppState) => state.lastUpdated;
export const selectAutoRefresh = (state: AppState) => state.autoRefresh;
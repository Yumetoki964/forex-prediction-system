import { ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// React Query クライアントの設定
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5分間はフレッシュとみなす
      gcTime: 10 * 60 * 1000, // 10分間キャッシュを保持
      refetchOnWindowFocus: false, // ウィンドウフォーカス時の自動リフェッチを無効化
      refetchOnMount: true, // マウント時にリフェッチ
      refetchOnReconnect: true, // 再接続時にリフェッチ
    },
    mutations: {
      retry: 1,
      onError: (error) => {
        console.error('Mutation Error:', error);
      },
    },
  },
});

interface QueryProviderProps {
  children: ReactNode;
}

export const QueryProvider = ({ children }: QueryProviderProps) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

export { queryClient };
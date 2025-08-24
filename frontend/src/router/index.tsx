import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import MainLayout from '@/layouts/MainLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { CircularProgress, Box } from '@mui/material';

// ページの遅延読み込み
const DashboardPage = lazy(() => import('@/pages/dashboard'));
const AnalysisPage = lazy(() => import('@/pages/analysis'));
const BacktestPage = lazy(() => import('@/pages/backtest'));
const DataManagementPage = lazy(() => import('@/pages/data-management'));
const SettingsPage = lazy(() => import('@/pages/settings'));
const SourcesPage = lazy(() => import('@/pages/sources'));

// 認証ページ
const LoginPage = lazy(() => import('@/pages/auth/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/auth/RegisterPage'));

// ローディングコンポーネント
const PageLoader = () => (
  <Box
    display="flex"
    justifyContent="center"
    alignItems="center"
    minHeight="200px"
    sx={{ color: 'primary.main' }}
  >
    <CircularProgress />
  </Box>
);

// ページの型定義（メニューアイコンと情報用）
export interface PageInfo {
  id: string;
  title: string;
  path: string;
  icon: string;
  requiresAuth?: boolean;
  section: 'main' | 'management';
}

// ページ情報の定義（SCOPE_PROGRESS.mdの統合ページ管理表から）
export const pages: PageInfo[] = [
  {
    id: 'P-001',
    title: '予測ダッシュボード',
    path: '/dashboard',
    icon: '📊',
    section: 'main',
  },
  {
    id: 'P-002',
    title: '詳細予測分析',
    path: '/analysis',
    icon: '📈',
    section: 'main',
  },
  {
    id: 'P-003',
    title: 'バックテスト検証',
    path: '/backtest',
    icon: '🔍',
    section: 'main',
  },
  {
    id: 'P-004',
    title: 'データ管理',
    path: '/data-management',
    icon: '🗄️',
    section: 'management',
  },
  {
    id: 'P-005',
    title: '予測設定',
    path: '/settings',
    icon: '⚙️',
    section: 'management',
  },
  {
    id: 'P-006',
    title: 'データソース管理',
    path: '/sources',
    icon: '🔗',
    section: 'management',
  },
];

// ルーター設定
export const router = createBrowserRouter([
  // 認証ページ（レイアウトなし）
  {
    path: '/login',
    element: (
      <Suspense fallback={<PageLoader />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: '/register',
    element: (
      <Suspense fallback={<PageLoader />}>
        <RegisterPage />
      </Suspense>
    ),
  },
  
  // メインアプリケーション（認証保護）
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/dashboard" replace />,
      },
      {
        path: 'dashboard',
        element: (
          <Suspense fallback={<PageLoader />}>
            <DashboardPage />
          </Suspense>
        ),
      },
      {
        path: 'analysis',
        element: (
          <Suspense fallback={<PageLoader />}>
            <AnalysisPage />
          </Suspense>
        ),
      },
      {
        path: 'backtest',
        element: (
          <Suspense fallback={<PageLoader />}>
            <BacktestPage />
          </Suspense>
        ),
      },
      {
        path: 'data-management',
        element: (
          <ProtectedRoute requireAdmin={true}>
            <Suspense fallback={<PageLoader />}>
              <DataManagementPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
      {
        path: 'settings',
        element: (
          <Suspense fallback={<PageLoader />}>
            <SettingsPage />
          </Suspense>
        ),
      },
      {
        path: 'sources',
        element: (
          <ProtectedRoute requireAdmin={true}>
            <Suspense fallback={<PageLoader />}>
              <SourcesPage />
            </Suspense>
          </ProtectedRoute>
        ),
      },
    ],
    errorElement: (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        sx={{ color: 'text.primary', textAlign: 'center' }}
      >
        <h1>404 - ページが見つかりません</h1>
        <p>お探しのページは存在しません。</p>
        <a href="/dashboard" style={{ color: '#00d4ff', textDecoration: 'none' }}>
          ダッシュボードに戻る
        </a>
      </Box>
    ),
  },
]);

// メニューアイテムをセクション別に分けるヘルパー関数
export const getPagesBySection = (section: 'main' | 'management') =>
  pages.filter((page) => page.section === section);

// パスからページ情報を取得するヘルパー関数
export const getPageByPath = (path: string) =>
  pages.find((page) => page.path === path);

// ページIDからページ情報を取得するヘルパー関数
export const getPageById = (id: string) =>
  pages.find((page) => page.id === id);
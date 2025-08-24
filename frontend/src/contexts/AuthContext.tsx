/**
 * 認証コンテキスト
 */

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { 
  AuthContextType, 
  AuthState, 
  User, 
  UserLogin, 
  UserRegister, 
  PasswordChange 
} from '../types/auth.types';
import AuthApiClient from '../services/authApi';
import { useNotification } from '../hooks/useNotification';

// 初期状態
const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
};

// アクションタイプ
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: User }
  | { type: 'AUTH_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean };

// リデューサー
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true };
    case 'AUTH_SUCCESS':
      return {
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'AUTH_FAILURE':
      return {
        user: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'LOGOUT':
      return {
        user: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
};

// コンテキスト作成
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// プロバイダーコンポーネント
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const { showNotification } = useNotification();

  // 初期認証チェック
  useEffect(() => {
    checkAuth();
  }, []);

  /**
   * 認証状態チェック
   */
  const checkAuth = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      // 初期チェックをスキップして、すぐにログイン画面を表示
      dispatch({ type: 'AUTH_FAILURE' });
    } catch (error) {
      dispatch({ type: 'AUTH_FAILURE' });
    }
  };

  /**
   * ログイン
   */
  const login = async (credentials: UserLogin) => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const response = await AuthApiClient.login(credentials);
      dispatch({ type: 'AUTH_SUCCESS', payload: response.user });
      showNotification('ログインしました', 'success');
    } catch (error: any) {
      dispatch({ type: 'AUTH_FAILURE' });
      showNotification(error.message || 'ログインに失敗しました', 'error');
      throw error;
    }
  };

  /**
   * ユーザー登録
   */
  const register = async (userData: UserRegister) => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const response = await AuthApiClient.register(userData);
      dispatch({ type: 'AUTH_SUCCESS', payload: response.user });
      showNotification('ユーザー登録が完了しました', 'success');
    } catch (error: any) {
      dispatch({ type: 'AUTH_FAILURE' });
      showNotification(error.message || 'ユーザー登録に失敗しました', 'error');
      throw error;
    }
  };

  /**
   * ログアウト
   */
  const logout = async () => {
    try {
      await AuthApiClient.logout();
      dispatch({ type: 'LOGOUT' });
      showNotification('ログアウトしました', 'info');
    } catch (error: any) {
      // ログアウトはクライアント側でも処理
      dispatch({ type: 'LOGOUT' });
      showNotification('ログアウトしました', 'info');
    }
  };

  /**
   * パスワード変更
   */
  const changePassword = async (data: PasswordChange) => {
    try {
      await AuthApiClient.changePassword(data);
      showNotification('パスワードが変更されました', 'success');
    } catch (error: any) {
      showNotification(error.message || 'パスワード変更に失敗しました', 'error');
      throw error;
    }
  };

  const contextValue: AuthContextType = {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    login,
    register,
    logout,
    changePassword,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// カスタムフック
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
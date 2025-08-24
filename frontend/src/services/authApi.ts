/**
 * 認証API クライアント
 */

import axios from 'axios';
import { 
  User, 
  UserLogin, 
  UserRegister, 
  PasswordChange,
  LoginResponse,
  RegisterResponse,
  LogoutResponse,
  PasswordChangeResponse 
} from '../types/auth.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// 認証用のaxiosインスタンスを作成
const authApi = axios.create({
  baseURL: `${API_BASE_URL}/api/auth`,
  withCredentials: true, // HttpOnly Cookieのため必須
  headers: {
    'Content-Type': 'application/json',
  },
});

export class AuthApiClient {
  /**
   * ユーザーログイン
   */
  static async login(credentials: UserLogin): Promise<LoginResponse> {
    try {
      const response = await authApi.post<LoginResponse>('/login', credentials);
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('ログインに失敗しました');
    }
  }

  /**
   * ユーザー登録
   */
  static async register(userData: UserRegister): Promise<RegisterResponse> {
    try {
      const response = await authApi.post<RegisterResponse>('/register', userData);
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('ユーザー登録に失敗しました');
    }
  }

  /**
   * ログアウト
   */
  static async logout(): Promise<LogoutResponse> {
    try {
      const response = await authApi.post<LogoutResponse>('/logout');
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('ログアウトに失敗しました');
    }
  }

  /**
   * 現在のユーザー情報取得
   */
  static async getCurrentUser(): Promise<User> {
    try {
      const response = await authApi.get<User>('/me');
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('認証されていません');
      }
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('ユーザー情報の取得に失敗しました');
    }
  }

  /**
   * パスワード変更
   */
  static async changePassword(data: PasswordChange): Promise<PasswordChangeResponse> {
    try {
      const response = await authApi.put<PasswordChangeResponse>('/change-password', data);
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('パスワード変更に失敗しました');
    }
  }
}

export default AuthApiClient;
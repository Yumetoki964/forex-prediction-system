/**
 * ログインページ
 */

import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { UserLogin } from '../../types/auth.types';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading } = useAuth();

  const [formData, setFormData] = useState<UserLogin>({
    username: '',
    password: '',
  });
  const [error, setError] = useState<string>('');
  const [validationErrors, setValidationErrors] = useState<{
    username?: string;
    password?: string;
  }>({});

  // リダイレクト先を取得（デフォルトはダッシュボード）
  const from = location.state?.from?.pathname || '/dashboard';

  /**
   * フォーム入力変更処理
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // バリデーションエラークリア
    if (validationErrors[name as keyof typeof validationErrors]) {
      setValidationErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  /**
   * バリデーション
   */
  const validateForm = (): boolean => {
    const errors: typeof validationErrors = {};

    if (!formData.username.trim()) {
      errors.username = 'ユーザー名またはメールアドレスを入力してください';
    }

    if (!formData.password) {
      errors.password = 'パスワードを入力してください';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * ログイン処理
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || 'ログインに失敗しました');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        py={4}
      >
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            {/* ヘッダー */}
            <Box textAlign="center" mb={4}>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                ログイン
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Forex Prediction System
              </Typography>
            </Box>

            {/* エラー表示 */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* ログインフォーム */}
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                name="username"
                label="ユーザー名またはメールアドレス"
                value={formData.username}
                onChange={handleChange}
                error={!!validationErrors.username}
                helperText={validationErrors.username}
                margin="normal"
                autoComplete="username"
                autoFocus
              />

              <TextField
                fullWidth
                name="password"
                label="パスワード"
                type="password"
                value={formData.password}
                onChange={handleChange}
                error={!!validationErrors.password}
                helperText={validationErrors.password}
                margin="normal"
                autoComplete="current-password"
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isLoading}
                sx={{ mt: 3, mb: 2 }}
              >
                {isLoading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  'ログイン'
                )}
              </Button>
            </form>

            <Divider sx={{ my: 3 }} />

            {/* 新規登録リンク */}
            <Box textAlign="center">
              <Typography variant="body2" color="textSecondary">
                アカウントをお持ちでない方は{' '}
                <Link to="/register" style={{ color: 'inherit', textDecoration: 'none' }}>
                  <Typography
                    component="span"
                    variant="body2"
                    color="primary"
                    sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                  >
                    新規登録
                  </Typography>
                </Link>
              </Typography>
            </Box>

            {/* デモ用ログイン情報 */}
            <Box mt={3} p={2} bgcolor="grey.50" borderRadius={1}>
              <Typography variant="caption" color="textSecondary">
                <strong>デモ用アカウント:</strong><br />
                管理者: admin / password<br />
                一般ユーザー: user / password
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default LoginPage;
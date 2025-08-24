/**
 * ユーザー登録ページ
 */

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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
import { UserRegister } from '../../types/auth.types';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();

  const [formData, setFormData] = useState<UserRegister>({
    username: '',
    email: '',
    password: '',
    full_name: '',
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string>('');
  const [validationErrors, setValidationErrors] = useState<{
    username?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  /**
   * フォーム入力変更処理
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (name === 'confirmPassword') {
      setConfirmPassword(value);
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
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

    // ユーザー名チェック
    if (!formData.username.trim()) {
      errors.username = 'ユーザー名を入力してください';
    } else if (formData.username.length < 3) {
      errors.username = 'ユーザー名は3文字以上で入力してください';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(formData.username)) {
      errors.username = 'ユーザー名は英数字、アンダースコア、ハイフンのみ使用可能です';
    }

    // メールアドレスチェック
    if (!formData.email.trim()) {
      errors.email = 'メールアドレスを入力してください';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = '有効なメールアドレスを入力してください';
    }

    // パスワードチェック
    if (!formData.password) {
      errors.password = 'パスワードを入力してください';
    } else if (formData.password.length < 8) {
      errors.password = 'パスワードは8文字以上で入力してください';
    } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = 'パスワードは英字と数字を含む必要があります';
    }

    // パスワード確認チェック
    if (!confirmPassword) {
      errors.confirmPassword = 'パスワード（確認）を入力してください';
    } else if (formData.password !== confirmPassword) {
      errors.confirmPassword = 'パスワードが一致しません';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * 登録処理
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    try {
      // full_nameが空の場合は除外
      const submitData: UserRegister = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
      };

      if (formData.full_name?.trim()) {
        submitData.full_name = formData.full_name.trim();
      }

      await register(submitData);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'ユーザー登録に失敗しました');
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
                新規登録
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

            {/* 登録フォーム */}
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                name="username"
                label="ユーザー名"
                value={formData.username}
                onChange={handleChange}
                error={!!validationErrors.username}
                helperText={validationErrors.username || '3文字以上、英数字・アンダースコア・ハイフンのみ'}
                margin="normal"
                autoComplete="username"
                autoFocus
              />

              <TextField
                fullWidth
                name="email"
                label="メールアドレス"
                type="email"
                value={formData.email}
                onChange={handleChange}
                error={!!validationErrors.email}
                helperText={validationErrors.email}
                margin="normal"
                autoComplete="email"
              />

              <TextField
                fullWidth
                name="full_name"
                label="フルネーム（任意）"
                value={formData.full_name}
                onChange={handleChange}
                margin="normal"
                autoComplete="name"
              />

              <TextField
                fullWidth
                name="password"
                label="パスワード"
                type="password"
                value={formData.password}
                onChange={handleChange}
                error={!!validationErrors.password}
                helperText={validationErrors.password || '8文字以上、英字と数字を含む'}
                margin="normal"
                autoComplete="new-password"
              />

              <TextField
                fullWidth
                name="confirmPassword"
                label="パスワード（確認）"
                type="password"
                value={confirmPassword}
                onChange={handleChange}
                error={!!validationErrors.confirmPassword}
                helperText={validationErrors.confirmPassword}
                margin="normal"
                autoComplete="new-password"
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
                  '新規登録'
                )}
              </Button>
            </form>

            <Divider sx={{ my: 3 }} />

            {/* ログインリンク */}
            <Box textAlign="center">
              <Typography variant="body2" color="textSecondary">
                既にアカウントをお持ちの方は{' '}
                <Link to="/login" style={{ color: 'inherit', textDecoration: 'none' }}>
                  <Typography
                    component="span"
                    variant="body2"
                    color="primary"
                    sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                  >
                    ログイン
                  </Typography>
                </Link>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default RegisterPage;
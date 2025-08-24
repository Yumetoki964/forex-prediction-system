/**
 * ユーザーメニューコンポーネント
 */

import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Typography,
  Box,
  Divider,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Person as PersonIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const UserMenu: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  /**
   * メニューを開く
   */
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  /**
   * メニューを閉じる
   */
  const handleClose = () => {
    setAnchorEl(null);
  };

  /**
   * ログアウト処理
   */
  const handleLogout = async () => {
    handleClose();
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  /**
   * 設定ページに移動
   */
  const handleSettings = () => {
    handleClose();
    navigate('/settings');
  };

  if (!user) {
    return null;
  }

  // ユーザー名の初期文字を取得（アバターに表示）
  const getInitials = (name: string): string => {
    return name.charAt(0).toUpperCase();
  };

  const displayName = user.full_name || user.username;

  return (
    <>
      {/* ユーザーアバターボタン */}
      <IconButton
        onClick={handleClick}
        size="small"
        sx={{ ml: 2 }}
        aria-controls={open ? 'user-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
      >
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: user.role === 'admin' ? 'error.main' : 'primary.main',
          }}
        >
          {getInitials(displayName)}
        </Avatar>
      </IconButton>

      {/* ユーザーメニュー */}
      <Menu
        id="user-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        PaperProps={{
          elevation: 3,
          sx: {
            overflow: 'visible',
            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
            mt: 1.5,
            minWidth: 200,
            '& .MuiAvatar-root': {
              width: 24,
              height: 24,
              ml: -0.5,
              mr: 1,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        {/* ユーザー情報表示 */}
        <Box sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Typography variant="subtitle2" fontWeight="bold">
            {displayName}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            {user.email}
          </Typography>
          <Box display="flex" alignItems="center" mt={0.5}>
            {user.role === 'admin' && (
              <>
                <AdminIcon fontSize="small" color="error" />
                <Typography variant="caption" color="error.main" sx={{ ml: 0.5 }}>
                  管理者
                </Typography>
              </>
            )}
            {user.role === 'user' && (
              <Typography variant="caption" color="textSecondary">
                一般ユーザー
              </Typography>
            )}
          </Box>
        </Box>

        <Divider />

        {/* プロフィール */}
        <MenuItem onClick={() => navigate('/profile')}>
          <ListItemIcon>
            <PersonIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>プロフィール</ListItemText>
        </MenuItem>

        {/* 設定 */}
        <MenuItem onClick={handleSettings}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>設定</ListItemText>
        </MenuItem>

        <Divider />

        {/* ログアウト */}
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>ログアウト</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default UserMenu;
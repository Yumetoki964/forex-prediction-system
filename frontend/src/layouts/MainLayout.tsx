import { useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  useTheme,
  useMediaQuery,
  Divider,
  ListSubheader,
} from '@mui/material';
import { Menu as MenuIcon } from '@mui/icons-material';
import { useAppStore, selectSidebarOpen } from '@/stores/appStore';
import { getPagesBySection } from '@/router';
import { APP_CONFIG } from '@/config/api.config';

const DRAWER_WIDTH = 280;

const MainLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const navigate = useNavigate();
  
  const sidebarOpen = useAppStore(selectSidebarOpen);
  const { setSidebarOpen } = useAppStore();

  // モバイル環境でのサイドバー制御
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    } else {
      setSidebarOpen(true);
    }
  }, [isMobile, setSidebarOpen]);

  const handleDrawerToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleMenuItemClick = (path: string) => {
    navigate(path);
    // モバイルでは選択後にサイドバーを閉じる
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  // 現在のページを取得 (使用時にコメントアウト解除)
  // const currentPage = getPageByPath(location.pathname);

  // サイドバーコンテンツ
  const drawerContent = (
    <Box>
      {/* ブランドロゴ */}
      <Box
        sx={{
          p: 3,
          borderBottom: '1px solid',
          borderBottomColor: 'divider',
        }}
      >
        <Typography
          variant="h5"
          sx={{
            background: 'linear-gradient(135deg, #00d4ff, #0099cc)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 'bold',
          }}
        >
          {APP_CONFIG.name}
        </Typography>
      </Box>

      {/* メインメニュー */}
      <List
        subheader={
          <ListSubheader
            sx={{
              backgroundColor: 'transparent',
              color: 'text.disabled',
              fontSize: '0.75rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              px: 3,
              py: 2,
            }}
          >
            メイン機能
          </ListSubheader>
        }
      >
        {getPagesBySection('main').map((page) => (
          <ListItem
            key={page.id}
            button
            selected={location.pathname === page.path}
            onClick={() => handleMenuItemClick(page.path)}
            sx={{
              mx: 1,
              borderRadius: 1,
              '&.Mui-selected': {
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                borderLeft: '3px solid #00d4ff',
                '&:hover': {
                  backgroundColor: 'rgba(0, 212, 255, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 40,
                fontSize: '1.25rem',
              }}
            >
              {page.icon}
            </ListItemIcon>
            <ListItemText
              primary={page.title}
              primaryTypographyProps={{
                fontSize: '0.9rem',
                fontWeight: location.pathname === page.path ? 600 : 500,
              }}
            />
          </ListItem>
        ))}
      </List>

      <Divider sx={{ my: 1 }} />

      {/* 管理メニュー */}
      <List
        subheader={
          <ListSubheader
            sx={{
              backgroundColor: 'transparent',
              color: 'text.disabled',
              fontSize: '0.75rem',
              fontWeight: 600,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              px: 3,
              py: 2,
            }}
          >
            管理機能
          </ListSubheader>
        }
      >
        {getPagesBySection('management').map((page) => (
          <ListItem
            key={page.id}
            button
            selected={location.pathname === page.path}
            onClick={() => handleMenuItemClick(page.path)}
            sx={{
              mx: 1,
              borderRadius: 1,
              '&.Mui-selected': {
                backgroundColor: 'rgba(0, 212, 255, 0.1)',
                borderLeft: '3px solid #00d4ff',
                '&:hover': {
                  backgroundColor: 'rgba(0, 212, 255, 0.15)',
                },
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 40,
                fontSize: '1.25rem',
              }}
            >
              {page.icon}
            </ListItemIcon>
            <ListItemText
              primary={page.title}
              primaryTypographyProps={{
                fontSize: '0.9rem',
                fontWeight: location.pathname === page.path ? 600 : 500,
              }}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* モバイル用ハンバーガーメニューボタン */}
      {isMobile && (
        <IconButton
          onClick={handleDrawerToggle}
          sx={{
            position: 'fixed',
            top: 16,
            left: 16,
            zIndex: theme.zIndex.drawer + 1,
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            '&:hover': {
              backgroundColor: 'primary.dark',
            },
          }}
        >
          <MenuIcon />
        </IconButton>
      )}

      {/* サイドバー */}
      <Drawer
        variant={isMobile ? 'temporary' : 'persistent'}
        open={sidebarOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            backgroundColor: 'background.paper',
            borderRight: '1px solid',
            borderRightColor: 'divider',
            backgroundImage: 'none',
          },
        }}
      >
        {drawerContent}
      </Drawer>

      {/* メインコンテンツエリア */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minHeight: '100vh',
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: isMobile ? 0 : sidebarOpen ? 0 : `-${DRAWER_WIDTH}px`,
          pt: isMobile ? 8 : 0, // モバイル時はハンバーガーメニュー分のパディング
        }}
      >
        {/* ページコンテンツ */}
        <Box sx={{ p: 3 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
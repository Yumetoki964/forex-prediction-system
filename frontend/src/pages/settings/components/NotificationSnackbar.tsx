import React from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  IconButton,
  Box,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { Notification } from '../hooks/useNotification';

interface NotificationSnackbarProps {
  notifications: Notification[];
  onClose: (id: string) => void;
}

const NotificationSnackbar: React.FC<NotificationSnackbarProps> = ({
  notifications,
  onClose,
}) => {
  return (
    <Box>
      {notifications.map((notification, index) => (
        <Snackbar
          key={notification.id}
          open={true}
          anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          sx={{
            position: 'fixed',
            top: 20 + index * 70, // 複数通知を縦に並べる
            right: 20,
            zIndex: 9999,
          }}
        >
          <Alert
            severity={notification.type}
            action={
              <IconButton
                size="small"
                aria-label="close"
                color="inherit"
                onClick={() => onClose(notification.id)}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            }
            sx={{
              width: '100%',
              '& .MuiAlert-icon': {
                alignItems: 'center',
              },
            }}
          >
            <AlertTitle>{notification.title}</AlertTitle>
            {notification.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};

export default NotificationSnackbar;
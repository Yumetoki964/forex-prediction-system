import { useCallback } from 'react';

type VariantType = 'default' | 'error' | 'success' | 'warning' | 'info';

export const useNotification = () => {
  const showNotification = useCallback(
    (message: string, variant: VariantType = 'default', _options?: object) => {
      // シンプルなconsole.logベースの通知（後でnotistack等に置き換え可能）
      const prefix = variant === 'success' ? '✅' : 
                    variant === 'error' ? '❌' : 
                    variant === 'warning' ? '⚠️' : 
                    variant === 'info' ? 'ℹ️' : '📢';
      console.log(`${prefix} ${message}`);
      return message;
    },
    []
  );

  const hideNotification = useCallback(
    (key?: string | number) => {
      console.log(`Hiding notification: ${key}`);
    },
    []
  );

  // 便利なヘルパーメソッド
  const showSuccess = useCallback(
    (message: string, options?: object) => 
      showNotification(message, 'success', options),
    [showNotification]
  );

  const showError = useCallback(
    (message: string, options?: object) => 
      showNotification(message, 'error', options),
    [showNotification]
  );

  const showWarning = useCallback(
    (message: string, options?: object) => 
      showNotification(message, 'warning', options),
    [showNotification]
  );

  const showInfo = useCallback(
    (message: string, options?: object) => 
      showNotification(message, 'info', options),
    [showNotification]
  );

  return {
    showNotification,
    hideNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
};

export default useNotification;
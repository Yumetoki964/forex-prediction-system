import { createTheme, ThemeOptions } from '@mui/material/styles';
import { PaletteOptions } from '@mui/material/styles/createPalette';

// デザインシステムから変換したカラーパレット
const paletteOptions: PaletteOptions = {
  mode: 'dark',
  primary: {
    main: '#00d4ff', // --primary
    dark: '#0099cc', // --primary-dark
    light: '#33ddff', // --primary-light
    contrastText: '#0f1419', // --background
  },
  secondary: {
    main: '#1a1f2e', // --secondary
    light: '#2d3748', // --secondary-light
    dark: '#4a5568', // --secondary-lighter
    contrastText: '#e6e8eb', // --text-primary
  },
  background: {
    default: '#0f1419', // --background
    paper: '#1a1f2e', // --surface
  },
  // Custom surface colors (defined separately)
  // surface: {
  //   main: '#1a1f2e', // --surface
  //   dark: '#2d3748', // --surface-elevated
  // },
  success: {
    main: '#00ff88', // --success
    light: 'rgba(0, 255, 136, 0.1)', // --success-bg
  },
  warning: {
    main: '#fbbf24', // --warning
    light: 'rgba(251, 191, 36, 0.1)', // --warning-bg
  },
  error: {
    main: '#ef4444', // --error
    light: 'rgba(239, 68, 68, 0.1)', // --error-bg
  },
  text: {
    primary: '#e6e8eb', // --text-primary
    secondary: '#9ca3af', // --text-secondary
    disabled: '#6b7280', // --text-muted
  },
  divider: '#4a5568', // --border
};

const themeOptions: ThemeOptions = {
  palette: paletteOptions,
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      "'Segoe UI'",
      "'SF Pro Display'",
      'Roboto',
      'Oxygen',
      'Ubuntu',
      'Cantarell',
      'sans-serif',
    ].join(','),
    fontWeightLight: 400, // --font-normal
    fontWeightRegular: 500, // --font-medium
    fontWeightMedium: 600, // --font-semibold
    fontWeightBold: 700, // --font-bold
    h1: {
      fontSize: '3rem', // --text-5xl
      fontWeight: 700,
      lineHeight: 1.25,
    },
    h2: {
      fontSize: '2.5rem', // --text-4xl
      fontWeight: 700,
      lineHeight: 1.25,
    },
    h3: {
      fontSize: '2rem', // --text-3xl
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h4: {
      fontSize: '1.5rem', // --text-2xl
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h5: {
      fontSize: '1.25rem', // --text-xl
      fontWeight: 600,
      lineHeight: 1.25,
    },
    h6: {
      fontSize: '1.125rem', // --text-lg
      fontWeight: 600,
      lineHeight: 1.25,
    },
    body1: {
      fontSize: '1rem', // --text-base
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem', // --text-sm
      lineHeight: 1.5,
    },
    caption: {
      fontSize: '0.75rem', // --text-xs
      lineHeight: 1.4,
    },
  },
  spacing: 4, // 基準: 4px (--spacing-xs)
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#0f1419',
          color: '#e6e8eb',
          fontFamily: [
            '-apple-system',
            'BlinkMacSystemFont',
            "'Segoe UI'",
            "'SF Pro Display'",
            'Roboto',
            'Oxygen',
            'Ubuntu',
            'Cantarell',
            'sans-serif',
          ].join(','),
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          padding: '16px 24px', // --spacing-md --spacing-lg
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #00d4ff, #0099cc)',
          color: '#0f1419',
          boxShadow: 'none',
          '&:hover': {
            background: 'linear-gradient(135deg, #33ddff, #00d4ff)',
            boxShadow: '0 4px 12px rgba(0, 212, 255, 0.3)',
          },
        },
        outlined: {
          backgroundColor: '#2d3748',
          color: '#e6e8eb',
          borderColor: '#4a5568',
          '&:hover': {
            backgroundColor: '#4a5568',
            borderColor: '#00d4ff',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #2d3748, #4a5568)',
          borderRadius: 12,
          border: '1px solid #4a5568',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1f2e',
          borderRadius: 8,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: '#1a1f2e',
            borderRadius: 8,
            '& fieldset': {
              borderColor: '#4a5568',
            },
            '&:hover fieldset': {
              borderColor: '#4a5568',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#00d4ff',
              boxShadow: '0 0 0 2px rgba(0, 212, 255, 0.2)',
            },
          },
          '& .MuiInputLabel-root': {
            color: '#e6e8eb',
            fontWeight: 500,
          },
          '& .MuiOutlinedInput-input': {
            color: '#e6e8eb',
          },
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1a1f2e',
          borderRight: '1px solid #4a5568',
          backgroundImage: 'none',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          margin: '2px 0',
          '&:hover': {
            backgroundColor: '#2d3748',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(0, 212, 255, 0.1)',
            borderLeft: '3px solid #00d4ff',
            '&:hover': {
              backgroundColor: 'rgba(0, 212, 255, 0.15)',
            },
          },
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        standardSuccess: {
          backgroundColor: 'rgba(0, 255, 136, 0.1)',
          color: '#00ff88',
          borderLeft: '4px solid #00ff88',
          borderRadius: 8,
        },
        standardWarning: {
          backgroundColor: 'rgba(251, 191, 36, 0.1)',
          color: '#fbbf24',
          borderLeft: '4px solid #fbbf24',
          borderRadius: 8,
        },
        standardError: {
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          color: '#ef4444',
          borderLeft: '4px solid #ef4444',
          borderRadius: 8,
        },
      },
    },
  },
  transitions: {
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195,
    },
    easing: {
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
    },
  },
};

export const theme = createTheme(themeOptions);

// 数値フォント（等幅フォント）用のスタイル
export const numericFont = {
  fontFamily: [
    "'Courier New'",
    "'SF Mono'",
    'Monaco',
    'Menlo',
    'Consolas',
    'monospace',
  ].join(','),
};

// アニメーション用のキーフレーム
export const animations = {
  pulse: {
    '@keyframes pulse': {
      '0%, 100%': {
        opacity: 1,
      },
      '50%': {
        opacity: 0.7,
      },
    },
    animation: 'pulse 2s ease-in-out infinite',
  },
  numberUpdate: {
    '@keyframes numberUpdate': {
      '0%': {
        color: '#e6e8eb',
      },
      '50%': {
        color: '#00d4ff',
        transform: 'scale(1.05)',
      },
      '100%': {
        color: '#e6e8eb',
        transform: 'scale(1)',
      },
    },
    animation: 'numberUpdate 0.8s ease-out',
  },
};
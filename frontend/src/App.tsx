import { RouterProvider } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryProvider } from '@/providers/QueryProvider';
import { theme } from '@/theme';
import { router } from '@/router';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <QueryProvider>
        <RouterProvider router={router} />
      </QueryProvider>
    </ThemeProvider>
  );
}

export default App;
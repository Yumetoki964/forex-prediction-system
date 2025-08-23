import React, { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ChartOptions,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Card, CardContent, Typography, Box, Skeleton } from '@mui/material';
import { useTheme } from '@mui/material/styles';

// Chart.jsの必要なコンポーネントを登録
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface ProfitChartProps {
  data?: {
    dates: string[];
    profitCurve: number[];
    drawdownCurve?: number[];
  };
  isLoading?: boolean;
  height?: number;
}

const ProfitChart: React.FC<ProfitChartProps> = ({ 
  data, 
  isLoading = false, 
  height = 320 
}) => {
  const theme = useTheme();
  const chartRef = useRef<ChartJS<'line'>>(null);

  // グラデーションを作成する関数
  const createGradient = (ctx: CanvasRenderingContext2D, chartArea: any) => {
    const gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
    gradient.addColorStop(0, 'rgba(0, 212, 255, 0.05)');
    gradient.addColorStop(1, 'rgba(0, 212, 255, 0.2)');
    return gradient;
  };

  // チャートデータを準備
  const chartData = {
    labels: data?.dates || [],
    datasets: [
      {
        label: '累積収益',
        data: data?.profitCurve || [],
        borderColor: theme.palette.primary.main,
        backgroundColor: (context: any) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          if (!chartArea) return 'transparent';
          return createGradient(ctx, chartArea);
        },
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 5,
        pointHoverBackgroundColor: theme.palette.primary.main,
        pointHoverBorderColor: theme.palette.background.paper,
        pointHoverBorderWidth: 2,
      },
      ...(data?.drawdownCurve ? [
        {
          label: 'ドローダウン',
          data: data.drawdownCurve,
          borderColor: theme.palette.error.main,
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderWidth: 1,
          fill: false,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: theme.palette.error.main,
          pointHoverBorderColor: theme.palette.background.paper,
          pointHoverBorderWidth: 2,
        }
      ] : [])
    ],
  };

  // チャートオプション
  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index',
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          color: theme.palette.text.primary,
          font: {
            size: 12,
          },
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: theme.palette.background.paper,
        titleColor: theme.palette.text.primary,
        bodyColor: theme.palette.text.primary,
        borderColor: theme.palette.divider,
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
        displayColors: false,
        callbacks: {
          title: (context) => {
            return `日付: ${context[0].label}`;
          },
          label: (context) => {
            const value = context.parsed.y;
            const label = context.dataset.label;
            const sign = value >= 0 ? '+' : '';
            return `${label}: ${sign}${value.toFixed(2)}%`;
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: theme.palette.divider,
          drawOnChartArea: true,
        },
        ticks: {
          color: theme.palette.text.secondary,
          font: {
            size: 11,
          },
          maxTicksLimit: 8,
        },
        title: {
          display: false,
        },
      },
      y: {
        display: true,
        grid: {
          color: theme.palette.divider,
          drawOnChartArea: true,
        },
        ticks: {
          color: theme.palette.text.secondary,
          font: {
            size: 11,
          },
          callback: (value) => `${value}%`,
        },
        title: {
          display: true,
          text: '収益率 (%)',
          color: theme.palette.text.secondary,
          font: {
            size: 12,
          },
        },
      },
    },
    elements: {
      line: {
        borderJoinStyle: 'round',
        borderCapStyle: 'round',
      },
    },
    animation: {
      duration: 1000,
      easing: 'easeInOutQuart',
    },
  };

  // チャートの更新処理
  useEffect(() => {
    const chart = chartRef.current;
    if (chart) {
      chart.update();
    }
  }, [data]);

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
            収益曲線
          </Typography>
          <Box sx={{ height }}>
            <Skeleton variant="rectangular" width="100%" height="100%" />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.dates.length) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
            収益曲線
          </Typography>
          <Box 
            sx={{ 
              height, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              border: `1px dashed ${theme.palette.divider}`,
              borderRadius: 1,
              backgroundColor: theme.palette.background.default
            }}
          >
            <Typography variant="body2" color="text.secondary">
              バックテストを実行して収益曲線を表示
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
          収益曲線
        </Typography>
        <Box sx={{ height }}>
          <Line 
            ref={chartRef}
            data={chartData} 
            options={options} 
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default ProfitChart;
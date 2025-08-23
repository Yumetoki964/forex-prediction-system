import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  Button,
  Box,
  LinearProgress,
  Alert,
  Chip
} from '@mui/material';
import { PlayArrow, Stop } from '@mui/icons-material';

export interface BacktestFormData {
  period: '1Y' | '3Y' | '5Y' | '10Y';
  initial_capital: number;
  risk_per_trade: number;
  stop_loss_pips: number;
}

interface BacktestFormProps {
  onSubmit: (data: BacktestFormData) => void;
  isRunning: boolean;
  progress?: number;
  status?: 'idle' | 'running' | 'completed' | 'failed';
  onCancel?: () => void;
}

const BacktestForm: React.FC<BacktestFormProps> = ({
  onSubmit,
  isRunning,
  progress = 0,
  status = 'idle',
  onCancel
}) => {
  const [formData, setFormData] = useState<BacktestFormData>({
    period: '1Y',
    initial_capital: 10000,
    risk_per_trade: 2,
    stop_loss_pips: 20
  });

  const [errors, setErrors] = useState<Partial<BacktestFormData>>({});

  const validateForm = (): boolean => {
    const newErrors: Partial<BacktestFormData> = {};

    if (formData.initial_capital < 1000) {
      newErrors.initial_capital = 1000;
    }
    if (formData.risk_per_trade < 0.5 || formData.risk_per_trade > 10) {
      newErrors.risk_per_trade = 0.5;
    }
    if (formData.stop_loss_pips < 5 || formData.stop_loss_pips > 100) {
      newErrors.stop_loss_pips = 5;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleInputChange = (field: keyof BacktestFormData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'running':
        return 'info';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'running':
        return '実行中';
      case 'completed':
        return '完了';
      case 'failed':
        return 'エラー';
      default:
        return '待機中';
    }
  };

  return (
    <Card sx={{ height: 'fit-content' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <Typography variant="h6" color="primary">
            バックテスト設定
          </Typography>
          <Chip 
            label={getStatusText()}
            color={getStatusColor() as any}
            size="small"
          />
        </Box>

        <form onSubmit={handleSubmit}>
          {/* 検証期間 */}
          <FormControl component="fieldset" sx={{ mb: 3 }}>
            <FormLabel component="legend" sx={{ color: 'text.secondary', fontSize: '0.875rem', mb: 1 }}>
              検証期間
            </FormLabel>
            <RadioGroup
              value={formData.period}
              onChange={(e) => handleInputChange('period', e.target.value as any)}
              sx={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(2, 1fr)', 
                gap: 1 
              }}
            >
              <FormControlLabel 
                value="1Y" 
                control={<Radio size="small" />} 
                label="1年"
                sx={{
                  margin: 0,
                  padding: 1,
                  borderRadius: 1,
                  border: 1,
                  borderColor: formData.period === '1Y' ? 'primary.main' : 'divider',
                  backgroundColor: formData.period === '1Y' ? 'primary.light' : 'transparent',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'primary.light'
                  }
                }}
              />
              <FormControlLabel 
                value="3Y" 
                control={<Radio size="small" />} 
                label="3年"
                sx={{
                  margin: 0,
                  padding: 1,
                  borderRadius: 1,
                  border: 1,
                  borderColor: formData.period === '3Y' ? 'primary.main' : 'divider',
                  backgroundColor: formData.period === '3Y' ? 'primary.light' : 'transparent',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'primary.light'
                  }
                }}
              />
              <FormControlLabel 
                value="5Y" 
                control={<Radio size="small" />} 
                label="5年"
                sx={{
                  margin: 0,
                  padding: 1,
                  borderRadius: 1,
                  border: 1,
                  borderColor: formData.period === '5Y' ? 'primary.main' : 'divider',
                  backgroundColor: formData.period === '5Y' ? 'primary.light' : 'transparent',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'primary.light'
                  }
                }}
              />
              <FormControlLabel 
                value="10Y" 
                control={<Radio size="small" />} 
                label="10年"
                sx={{
                  margin: 0,
                  padding: 1,
                  borderRadius: 1,
                  border: 1,
                  borderColor: formData.period === '10Y' ? 'primary.main' : 'divider',
                  backgroundColor: formData.period === '10Y' ? 'primary.light' : 'transparent',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'primary.light'
                  }
                }}
              />
            </RadioGroup>
          </FormControl>

          {/* 初期資金 */}
          <TextField
            fullWidth
            label="初期資金 (USD)"
            type="number"
            value={formData.initial_capital}
            onChange={(e) => handleInputChange('initial_capital', parseInt(e.target.value) || 0)}
            error={!!errors.initial_capital}
            helperText={errors.initial_capital ? `最小値: ${errors.initial_capital}` : ''}
            inputProps={{ min: 1000, step: 1000 }}
            sx={{ mb: 3 }}
          />

          {/* 1取引リスク */}
          <TextField
            fullWidth
            label="1取引リスク (%)"
            type="number"
            value={formData.risk_per_trade}
            onChange={(e) => handleInputChange('risk_per_trade', parseFloat(e.target.value) || 0)}
            error={!!errors.risk_per_trade}
            helperText={errors.risk_per_trade ? `範囲: ${errors.risk_per_trade} - 10%` : ''}
            inputProps={{ min: 0.5, max: 10, step: 0.5 }}
            sx={{ mb: 3 }}
          />

          {/* ストップロス */}
          <TextField
            fullWidth
            label="ストップロス (pips)"
            type="number"
            value={formData.stop_loss_pips}
            onChange={(e) => handleInputChange('stop_loss_pips', parseInt(e.target.value) || 0)}
            error={!!errors.stop_loss_pips}
            helperText={errors.stop_loss_pips ? `範囲: ${errors.stop_loss_pips} - 100 pips` : ''}
            inputProps={{ min: 5, max: 100, step: 5 }}
            sx={{ mb: 3 }}
          />

          {/* 実行ボタン */}
          <Button
            fullWidth
            variant="contained"
            size="large"
            type="submit"
            disabled={isRunning}
            startIcon={isRunning ? <Stop /> : <PlayArrow />}
            sx={{ mb: 2 }}
          >
            {isRunning ? '実行中...' : 'バックテスト実行'}
          </Button>

          {/* キャンセルボタン */}
          {isRunning && onCancel && (
            <Button
              fullWidth
              variant="outlined"
              onClick={onCancel}
              sx={{ mb: 2 }}
            >
              キャンセル
            </Button>
          )}

          {/* 進捗バー */}
          {isRunning && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                進捗: {Math.round(progress)}%
              </Typography>
            </Box>
          )}

          {/* 注意事項 */}
          <Alert severity="info" sx={{ fontSize: '0.875rem' }}>
            <strong>注意:</strong> 大規模データの検証には数分かかる場合があります。
          </Alert>
        </form>
      </CardContent>
    </Card>
  );
};

export default BacktestForm;
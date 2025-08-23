import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Button,
  CircularProgress,
  
} from '@mui/material';

// 設定系の型定義
export interface PredictionSettings {
  model_weights: {
    lstm: number;
    xgboost: number;
  };
  sensitivity: 'conservative' | 'standard' | 'aggressive';
  custom_parameters?: Record<string, any>;
}

interface PredictionSettingsFormProps {
  settings: PredictionSettings | null;
  isLoading: boolean;
  onSave: (settings: PredictionSettings) => void;
  onTest: (settings: PredictionSettings) => void;
  isTestingSettings: boolean;
  testResults?: {
    prediction_accuracy: number;
    confidence_score: number;
  } | null;
}

const PredictionSettingsForm: React.FC<PredictionSettingsFormProps> = ({
  settings,
  isLoading,
  onSave,
  onTest,
  isTestingSettings,
  testResults,
}) => {
  
  const [formData, setFormData] = useState<PredictionSettings>({
    model_weights: { lstm: 0.6, xgboost: 0.4 },
    sensitivity: 'standard',
  });

  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  const handleLstmWeightChange = (_: Event, value: number | number[]) => {
    const lstmWeight = Array.isArray(value) ? value[0] : value;
    const xgboostWeight = 100 - lstmWeight;
    
    setFormData(prev => ({
      ...prev,
      model_weights: {
        lstm: lstmWeight / 100,
        xgboost: xgboostWeight / 100,
      }
    }));
  };

  const handleXgboostWeightChange = (_: Event, value: number | number[]) => {
    const xgboostWeight = Array.isArray(value) ? value[0] : value;
    const lstmWeight = 100 - xgboostWeight;
    
    setFormData(prev => ({
      ...prev,
      model_weights: {
        lstm: lstmWeight / 100,
        xgboost: xgboostWeight / 100,
      }
    }));
  };

  const handleSensitivityChange = (event: any) => {
    setFormData(prev => ({
      ...prev,
      sensitivity: event.target.value as 'conservative' | 'standard' | 'aggressive',
    }));
  };

  const handleSave = () => {
    onSave(formData);
  };

  const handleTest = () => {
    onTest(formData);
  };

  const lstmPercentage = Math.round(formData.model_weights.lstm * 100);
  const xgboostPercentage = Math.round(formData.model_weights.xgboost * 100);

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography 
          variant="h5" 
          sx={{ 
            mb: 3, 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1,
            color: 'primary.main'
          }}
        >
          🤖 予測モデル設定
        </Typography>
        
        <Alert 
          severity="info" 
          sx={{ 
            mb: 3, 
            backgroundColor: 'rgba(0, 212, 255, 0.05)',
            border: '1px solid rgba(0, 212, 255, 0.2)',
            '& .MuiAlert-icon': {
              color: 'primary.main',
            },
          }}
        >
          <Typography variant="subtitle2" color="primary.main" sx={{ mb: 1 }}>
            アンサンブルモデルについて
          </Typography>
          <Typography variant="body2" color="text.secondary">
            LSTM（長短期記憶）ニューラルネットワークとXGBoost（勾配ブースティング）を組み合わせたアンサンブルモデルを使用しています。
            LSTMは時系列パターンの学習に優れ、XGBoostは非線形関係の捉え方に長けているため、両者の強みを活かした高精度な予測が可能です。
          </Typography>
        </Alert>

        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            モデル比重調整
          </Typography>
          
          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>
              LSTMモデル比重: {lstmPercentage}%
            </Typography>
            <Slider
              value={lstmPercentage}
              onChange={handleLstmWeightChange}
              min={0}
              max={100}
              valueLabelDisplay="auto"
              sx={{
                color: 'primary.main',
                '& .MuiSlider-thumb': {
                  backgroundColor: 'primary.main',
                },
                '& .MuiSlider-track': {
                  backgroundColor: 'primary.main',
                },
                '& .MuiSlider-rail': {
                  backgroundColor: 'grey.700',
                },
              }}
            />
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                fontSize: '0.75rem', 
                color: 'text.secondary',
                mt: 1 
              }}
            >
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </Box>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography gutterBottom>
              XGBoostモデル比重: {xgboostPercentage}%
            </Typography>
            <Slider
              value={xgboostPercentage}
              onChange={handleXgboostWeightChange}
              min={0}
              max={100}
              valueLabelDisplay="auto"
              sx={{
                color: 'success.main',
                '& .MuiSlider-thumb': {
                  backgroundColor: 'success.main',
                },
                '& .MuiSlider-track': {
                  backgroundColor: 'success.main',
                },
                '& .MuiSlider-rail': {
                  backgroundColor: 'grey.700',
                },
              }}
            />
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                fontSize: '0.75rem', 
                color: 'text.secondary',
                mt: 1 
              }}
            >
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </Box>
          </Box>

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>予測感度</InputLabel>
            <Select
              value={formData.sensitivity}
              onChange={handleSensitivityChange}
              label="予測感度"
            >
              <MenuItem value="conservative">保守的 - 確実性を重視した予測</MenuItem>
              <MenuItem value="standard">標準 - バランスの取れた予測</MenuItem>
              <MenuItem value="aggressive">積極的 - 変動を敏感に捉える予測</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {testResults && (
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              設定テスト結果
            </Typography>
            <Typography variant="body2">
              予測精度: {testResults.prediction_accuracy.toFixed(1)}% | 
              信頼度スコア: {testResults.confidence_score.toFixed(3)}
            </Typography>
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Button
            variant="outlined"
            onClick={handleTest}
            disabled={isTestingSettings}
            startIcon={
              isTestingSettings ? <CircularProgress size={20} /> : <span>🧪</span>
            }
          >
            {isTestingSettings ? 'テスト実行中...' : '設定テスト実行'}
          </Button>
          
          <Button
            variant="contained"
            onClick={handleSave}
            startIcon={<span>💾</span>}
          >
            設定を保存
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PredictionSettingsForm;
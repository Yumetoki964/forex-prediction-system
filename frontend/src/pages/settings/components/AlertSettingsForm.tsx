import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControlLabel,
  Checkbox,
  Radio,
  RadioGroup,
  TextField,
  Button,
  Chip,
  CircularProgress,
  
} from '@mui/material';

// アラート設定の型定義
export interface AlertCondition {
  type: string;
  threshold: number;
  priority: 'high' | 'medium' | 'low';
}

export interface AlertSettings {
  email_notifications: boolean;
  browser_notifications: boolean;
  conditions: AlertCondition[];
}

interface AlertSettingsFormProps {
  settings: AlertSettings | null;
  isLoading: boolean;
  onSave: (settings: AlertSettings) => void;
}

const AlertSettingsForm: React.FC<AlertSettingsFormProps> = ({
  settings,
  isLoading,
  onSave,
}) => {
  
  const [formData, setFormData] = useState<AlertSettings>({
    email_notifications: true,
    browser_notifications: true,
    conditions: [
      { type: 'price_change', threshold: 2.5, priority: 'medium' },
      { type: 'prediction_accuracy', threshold: 85, priority: 'high' },
      { type: 'risk_indicator', threshold: 1.5, priority: 'medium' },
    ],
  });

  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  const handleNotificationChange = (field: 'email_notifications' | 'browser_notifications') => 
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setFormData(prev => ({
        ...prev,
        [field]: event.target.checked,
      }));
    };

  const handleConditionThresholdChange = (index: number) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseFloat(event.target.value);
    if (!isNaN(value)) {
      setFormData(prev => ({
        ...prev,
        conditions: prev.conditions.map((condition, i) =>
          i === index ? { ...condition, threshold: value } : condition
        ),
      }));
    }
  };

  const handleConditionPriorityChange = (index: number) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const priority = event.target.value as 'high' | 'medium' | 'low';
    setFormData(prev => ({
      ...prev,
      conditions: prev.conditions.map((condition, i) =>
        i === index ? { ...condition, priority } : condition
      ),
    }));
  };

  const handleSave = () => {
    onSave(formData);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getConditionTitle = (type: string) => {
    switch (type) {
      case 'price_change': return '価格変動アラート';
      case 'prediction_accuracy': return '予測精度アラート';
      case 'risk_indicator': return 'リスク指標アラート';
      default: return type;
    }
  };

  const getThresholdUnit = (type: string) => {
    switch (type) {
      case 'price_change': return '%';
      case 'prediction_accuracy': return '%';
      case 'risk_indicator': return '';
      default: return '';
    }
  };

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
          🚨 アラート設定
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          重要な変動予測時の通知方法と条件を設定します
        </Typography>

        {/* 通知方法設定 */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            通知方法
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.email_notifications}
                  onChange={handleNotificationChange('email_notifications')}
                  sx={{ 
                    color: 'primary.main',
                    '&.Mui-checked': {
                      color: 'primary.main',
                    },
                  }}
                />
              }
              label="メール通知"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.browser_notifications}
                  onChange={handleNotificationChange('browser_notifications')}
                  sx={{ 
                    color: 'primary.main',
                    '&.Mui-checked': {
                      color: 'primary.main',
                    },
                  }}
                />
              }
              label="ブラウザ通知"
            />
          </Box>
        </Box>

        {/* アラート条件設定 */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            アラート条件
          </Typography>
          
          {formData.conditions.map((condition, index) => (
            <Card 
              key={condition.type}
              variant="outlined"
              sx={{ 
                mb: 2, 
                backgroundColor: 'background.default',
                border: '1px solid',
                borderColor: 'divider',
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                    {getConditionTitle(condition.type)}
                  </Typography>
                  <Chip
                    label={condition.priority.toUpperCase()}
                    color={getPriorityColor(condition.priority) as any}
                    size="small"
                    variant="outlined"
                  />
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, flexWrap: 'wrap' }}>
                  <TextField
                    label="閾値"
                    type="number"
                    value={condition.threshold}
                    onChange={handleConditionThresholdChange(index)}
                    size="small"
                    sx={{ width: '120px' }}
                    InputProps={{
                      endAdornment: getThresholdUnit(condition.type) && (
                        <Typography variant="body2" color="text.secondary">
                          {getThresholdUnit(condition.type)}
                        </Typography>
                      ),
                    }}
                  />
                  
                  <Box>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      優先度:
                    </Typography>
                    <RadioGroup
                      row
                      value={condition.priority}
                      onChange={handleConditionPriorityChange(index)}
                    >
                      <FormControlLabel
                        value="high"
                        control={<Radio size="small" />}
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <span>高</span>
                            <Chip label="HIGH" color="error" size="small" variant="outlined" />
                          </Box>
                        }
                      />
                      <FormControlLabel
                        value="medium"
                        control={<Radio size="small" />}
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <span>中</span>
                            <Chip label="MED" color="warning" size="small" variant="outlined" />
                          </Box>
                        }
                      />
                      <FormControlLabel
                        value="low"
                        control={<Radio size="small" />}
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <span>低</span>
                            <Chip label="LOW" color="success" size="small" variant="outlined" />
                          </Box>
                        }
                      />
                    </RadioGroup>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>

        <Box sx={{ display: 'flex', gap: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Button
            variant="contained"
            onClick={handleSave}
            startIcon={<span>💾</span>}
          >
            アラート設定を保存
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AlertSettingsForm;
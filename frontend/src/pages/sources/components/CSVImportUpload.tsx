import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
} from '@mui/material';
import {
  CloudUpload,
  Description,
  Clear,
  CheckCircle,
  Error,
  InfoOutlined,
} from '@mui/icons-material';
import { useCSVImport } from '../hooks/useSourcesData';

interface CSVImportUploadProps {
  onImportStart?: () => void;
  onImportComplete?: (result: any) => void;
}

const CSVImportUpload: React.FC<CSVImportUploadProps> = ({ 
  onImportStart, 
  onImportComplete 
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [fileValidated, setFileValidated] = useState<boolean | null>(null);
  const [validationMessage, setValidationMessage] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const csvImportMutation = useCSVImport();

  // ファイル検証
  const validateFile = useCallback((file: File) => {
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = ['text/csv', 'application/csv', 'text/plain'];
    
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.csv')) {
      setFileValidated(false);
      setValidationMessage('CSVファイルを選択してください');
      return false;
    }
    
    if (file.size > maxSize) {
      setFileValidated(false);
      setValidationMessage('ファイルサイズは50MB以下にしてください');
      return false;
    }
    
    setFileValidated(true);
    setValidationMessage('ファイルは有効です');
    return true;
  }, []);

  // ファイル選択処理
  const handleFileSelect = useCallback((file: File) => {
    if (validateFile(file)) {
      setSelectedFile(file);
    } else {
      setSelectedFile(null);
    }
  }, [validateFile]);

  // ドラッグ&ドロップ処理
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // ファイル入力変更
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // ファイルクリア
  const handleClearFile = useCallback(() => {
    setSelectedFile(null);
    setFileValidated(null);
    setValidationMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  // インポート実行
  const handleImport = useCallback(async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('source', 'manual_upload');

    try {
      onImportStart?.();
      const result = await csvImportMutation.mutateAsync(formData);
      onImportComplete?.(result);
      // 成功時はファイルをクリア
      handleClearFile();
    } catch (error) {
      console.error('CSV import failed:', error);
    }
  }, [selectedFile, csvImportMutation, onImportStart, onImportComplete, handleClearFile]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Box sx={{ fontSize: '1.5rem', mr: 2 }}>📁</Box>
          <Typography variant="h6" color="primary">
            CSV一括インポート
          </Typography>
          {csvImportMutation.isPending && (
            <Chip
              label="インポート中"
              color="info"
              size="small"
              sx={{ ml: 'auto' }}
            />
          )}
        </Box>

        {csvImportMutation.isPending && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              CSVファイルをインポート中...
            </Typography>
          </Box>
        )}

        {/* ファイルアップロード領域 */}
        <Box
          sx={{
            border: 2,
            borderStyle: 'dashed',
            borderColor: dragActive ? 'primary.main' : 'divider',
            borderRadius: 3,
            p: 4,
            textAlign: 'center',
            bgcolor: dragActive ? 'primary.light' : 'background.default',
            opacity: dragActive ? 0.8 : 1,
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: 'primary.main',
              bgcolor: 'background.paper',
            },
            mb: 3,
          }}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.txt"
            onChange={handleInputChange}
            style={{ display: 'none' }}
            disabled={csvImportMutation.isPending}
          />

          {selectedFile ? (
            <Box>
              <Description sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                {selectedFile.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {formatFileSize(selectedFile.size)}
              </Typography>
              
              {fileValidated !== null && (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                  {fileValidated ? (
                    <CheckCircle sx={{ color: 'success.main', mr: 1 }} />
                  ) : (
                    <Error sx={{ color: 'error.main', mr: 1 }} />
                  )}
                  <Typography 
                    variant="body2" 
                    color={fileValidated ? 'success.main' : 'error.main'}
                  >
                    {validationMessage}
                  </Typography>
                </Box>
              )}

              <IconButton
                onClick={(e) => {
                  e.stopPropagation();
                  handleClearFile();
                }}
                disabled={csvImportMutation.isPending}
                sx={{ mt: 1 }}
              >
                <Clear />
              </IconButton>
            </Box>
          ) : (
            <Box>
              <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" sx={{ mb: 1 }}>
                CSVファイルをアップロード
              </Typography>
              <Typography variant="body2" color="text.secondary">
                日銀形式のCSVファイルをドラッグ＆ドロップまたはクリックして選択
              </Typography>
            </Box>
          )}
        </Box>

        {/* インポート情報 */}
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>対応形式:</strong> CSV (.csv), TSV (.txt)<br />
            <strong>最大ファイルサイズ:</strong> 50MB<br />
            <strong>期待データ形式:</strong> 日時, 通貨ペア, レート, 出来高
          </Typography>
        </Alert>

        {/* 実行ボタン */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<CloudUpload />}
            onClick={handleImport}
            disabled={!selectedFile || !fileValidated || csvImportMutation.isPending}
            fullWidth
          >
            インポート実行
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<Clear />}
            onClick={handleClearFile}
            disabled={!selectedFile || csvImportMutation.isPending}
            sx={{ minWidth: 120 }}
          >
            クリア
          </Button>
        </Box>

        {/* インポート設定情報 */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <InfoOutlined sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              インポート設定
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • 重複データ: 自動スキップ
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • 文字エンコーディング: UTF-8, Shift_JIS自動判定
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • 区切り文字: カンマ(,), タブ自動判定
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
              • バッチサイズ: 1,000レコード/バッチ
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default CSVImportUpload;
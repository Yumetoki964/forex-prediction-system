"""
特徴量エンジニアリング - 為替予測のための特徴量生成
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """為替予測のための特徴量エンジニアリング"""
    
    def __init__(self):
        self.feature_names = []
        
    def create_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'close_rate',
        include_technical: bool = True,
        include_lag: bool = True,
        include_rolling: bool = True,
        include_time: bool = True
    ) -> pd.DataFrame:
        """
        特徴量を生成
        
        Args:
            df: OHLCデータのDataFrame
            target_col: ターゲット列名
            include_technical: テクニカル指標を含むか
            include_lag: ラグ特徴量を含むか
            include_rolling: ローリング統計を含むか
            include_time: 時系列特徴量を含むか
        
        Returns:
            特徴量が追加されたDataFrame
        """
        df = df.copy()
        
        # 基本的な価格変動特徴量
        df = self._add_price_features(df)
        
        # テクニカル指標
        if include_technical:
            df = self._add_technical_indicators(df)
        
        # ラグ特徴量
        if include_lag:
            df = self._add_lag_features(df, target_col)
        
        # ローリング統計
        if include_rolling:
            df = self._add_rolling_features(df, target_col)
        
        # 時系列特徴量
        if include_time:
            df = self._add_time_features(df)
        
        # 特徴量名を保存
        self.feature_names = [col for col in df.columns if col not in ['date', target_col]]
        
        return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """価格変動に関する特徴量を追加"""
        
        # 日次リターン
        df['returns'] = df['close_rate'].pct_change()
        
        # 対数リターン
        df['log_returns'] = np.log(df['close_rate'] / df['close_rate'].shift(1))
        
        # 価格レンジ
        df['high_low_range'] = df['high_rate'] - df['low_rate']
        df['high_low_pct'] = df['high_low_range'] / df['close_rate']
        
        # ボディサイズ（実体）
        df['body_size'] = abs(df['close_rate'] - df['open_rate'])
        df['body_pct'] = df['body_size'] / df['close_rate']
        
        # 上ヒゲ・下ヒゲ
        df['upper_shadow'] = df['high_rate'] - df[['open_rate', 'close_rate']].max(axis=1)
        df['lower_shadow'] = df[['open_rate', 'close_rate']].min(axis=1) - df['low_rate']
        
        # 価格位置（日中のどこで終値をつけたか）
        df['price_position'] = (df['close_rate'] - df['low_rate']) / (df['high_rate'] - df['low_rate'] + 1e-10)
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """テクニカル指標を追加"""
        
        # 移動平均
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['close_rate'].rolling(window=period).mean()
            df[f'sma_{period}_ratio'] = df['close_rate'] / df[f'sma_{period}']
        
        # 指数移動平均
        for period in [12, 26]:
            df[f'ema_{period}'] = df['close_rate'].ewm(span=period, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close_rate'], period=14)
        
        # ボリンジャーバンド
        bb_period = 20
        bb_std = 2
        df['bb_middle'] = df['close_rate'].rolling(window=bb_period).mean()
        bb_std_dev = df['close_rate'].rolling(window=bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (bb_std_dev * bb_std)
        df['bb_width'] = df['bb_upper'] - df['bb_lower']
        df['bb_position'] = (df['close_rate'] - df['bb_lower']) / (df['bb_width'] + 1e-10)
        
        # ATR (Average True Range)
        df['atr'] = self._calculate_atr(df, period=14)
        
        # ストキャスティクス
        stoch_period = 14
        df['stoch_k'] = ((df['close_rate'] - df['low_rate'].rolling(window=stoch_period).min()) / 
                        (df['high_rate'].rolling(window=stoch_period).max() - 
                         df['low_rate'].rolling(window=stoch_period).min() + 1e-10)) * 100
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSIを計算"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATRを計算"""
        high_low = df['high_rate'] - df['low_rate']
        high_close = abs(df['high_rate'] - df['close_rate'].shift())
        low_close = abs(df['low_rate'] - df['close_rate'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def _add_lag_features(self, df: pd.DataFrame, target_col: str, lags: List[int] = None) -> pd.DataFrame:
        """ラグ特徴量を追加"""
        if lags is None:
            lags = [1, 2, 3, 5, 10, 20]
        
        for lag in lags:
            df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
            df[f'returns_lag_{lag}'] = df['returns'].shift(lag)
        
        return df
    
    def _add_rolling_features(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """ローリング統計量を追加"""
        
        windows = [5, 10, 20, 50]
        
        for window in windows:
            # ローリング平均
            df[f'rolling_mean_{window}'] = df[target_col].rolling(window=window).mean()
            
            # ローリング標準偏差（ボラティリティ）
            df[f'rolling_std_{window}'] = df[target_col].rolling(window=window).std()
            
            # ローリング最大値・最小値
            df[f'rolling_max_{window}'] = df[target_col].rolling(window=window).max()
            df[f'rolling_min_{window}'] = df[target_col].rolling(window=window).min()
            
            # 現在値の位置（最大値・最小値に対する）
            df[f'price_to_max_{window}'] = df[target_col] / df[f'rolling_max_{window}']
            df[f'price_to_min_{window}'] = df[target_col] / df[f'rolling_min_{window}']
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """時系列特徴量を追加"""
        
        if 'date' in df.columns:
            # dateがdatetime型でない場合は変換
            if not pd.api.types.is_datetime64_any_dtype(df['date']):
                df['date'] = pd.to_datetime(df['date'])
            
            # 曜日（0=月曜日, 4=金曜日）
            df['day_of_week'] = df['date'].dt.dayofweek
            
            # 月
            df['month'] = df['date'].dt.month
            
            # 四半期
            df['quarter'] = df['date'].dt.quarter
            
            # 月初・月末フラグ
            df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
            df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
            
            # 四半期初・四半期末フラグ
            df['is_quarter_start'] = df['date'].dt.is_quarter_start.astype(int)
            df['is_quarter_end'] = df['date'].dt.is_quarter_end.astype(int)
        
        return df
    
    def prepare_sequences(
        self,
        df: pd.DataFrame,
        sequence_length: int = 60,
        target_col: str = 'close_rate',
        prediction_horizon: int = 1
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        LSTM用のシーケンスデータを準備
        
        Args:
            df: 特徴量DataFrame
            sequence_length: シーケンスの長さ
            target_col: ターゲット列名
            prediction_horizon: 予測期間
        
        Returns:
            X, y のタプル
        """
        # 特徴量列を選択（NaNを含む列を除外）
        feature_cols = [col for col in self.feature_names if col in df.columns]
        df_features = df[feature_cols].dropna()
        
        # スケーリングのための値を保存
        self.feature_means = df_features.mean()
        self.feature_stds = df_features.std()
        
        # 正規化
        df_normalized = (df_features - self.feature_means) / (self.feature_stds + 1e-10)
        
        # シーケンスを作成
        X, y = [], []
        
        for i in range(sequence_length, len(df_normalized) - prediction_horizon + 1):
            X.append(df_normalized.iloc[i-sequence_length:i].values)
            
            # ターゲットは元のスケールの価格変化率
            current_price = df[target_col].iloc[i-1]
            future_price = df[target_col].iloc[i-1+prediction_horizon]
            y.append((future_price - current_price) / current_price)
        
        return np.array(X), np.array(y)
    
    def prepare_tabular_data(
        self,
        df: pd.DataFrame,
        target_col: str = 'close_rate',
        prediction_horizon: int = 1
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        XGBoost用の表形式データを準備
        
        Args:
            df: 特徴量DataFrame
            target_col: ターゲット列名
            prediction_horizon: 予測期間
        
        Returns:
            X, y のタプル
        """
        # 特徴量列を選択
        feature_cols = [col for col in self.feature_names if col in df.columns]
        X = df[feature_cols].copy()
        
        # ターゲットを作成（未来の価格変化率）
        y = df[target_col].shift(-prediction_horizon).pct_change(prediction_horizon)
        
        # NaNを削除
        valid_idx = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_idx]
        y = y[valid_idx]
        
        return X, y
    
    def get_feature_importance(self, model, feature_names: List[str] = None) -> pd.DataFrame:
        """
        特徴量の重要度を取得
        
        Args:
            model: 学習済みモデル
            feature_names: 特徴量名のリスト
        
        Returns:
            特徴量重要度のDataFrame
        """
        if feature_names is None:
            feature_names = self.feature_names
        
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = abs(model.coef_)
        else:
            return pd.DataFrame()
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return importance_df
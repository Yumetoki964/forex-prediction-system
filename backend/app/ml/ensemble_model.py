"""
アンサンブルモデル - LSTMとXGBoostを組み合わせた統合予測モデル
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging
import json

from app.ml.lstm_model import LSTMForexPredictor
from app.ml.xgboost_model import XGBoostForexPredictor
from app.ml.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class EnsembleForexPredictor:
    """LSTM と XGBoost を組み合わせたアンサンブル予測モデル"""
    
    def __init__(
        self,
        lstm_weight: float = 0.5,
        xgboost_weight: float = 0.5,
        use_meta_learner: bool = False
    ):
        """
        Args:
            lstm_weight: LSTMモデルの重み
            xgboost_weight: XGBoostモデルの重み
            use_meta_learner: メタ学習器を使用するか
        """
        self.lstm_weight = lstm_weight
        self.xgboost_weight = xgboost_weight
        self.use_meta_learner = use_meta_learner
        
        # モデルの初期化
        self.lstm_model = LSTMForexPredictor()
        self.xgboost_model = XGBoostForexPredictor()
        self.feature_engineer = FeatureEngineer()
        
        # メタ学習器（必要な場合）
        self.meta_learner = None
        if use_meta_learner:
            from sklearn.linear_model import LinearRegression
            self.meta_learner = LinearRegression()
        
        self.is_trained = False
        
    def prepare_data(
        self,
        df: pd.DataFrame,
        target_col: str = 'close_rate',
        sequence_length: int = 60,
        prediction_horizon: int = 1,
        test_size: float = 0.2,
        val_size: float = 0.1
    ) -> Dict[str, Any]:
        """
        データを準備
        
        Args:
            df: 元データ
            target_col: ターゲット列
            sequence_length: シーケンス長
            prediction_horizon: 予測期間
            test_size: テストデータの割合
            val_size: 検証データの割合
        
        Returns:
            準備されたデータセット
        """
        # 特徴量エンジニアリング
        df_features = self.feature_engineer.create_features(df, target_col)
        
        # データ分割のインデックス
        n_samples = len(df_features)
        test_idx = int(n_samples * (1 - test_size))
        val_idx = int(test_idx * (1 - val_size))
        
        # LSTM用データ準備
        X_seq, y_seq = self.feature_engineer.prepare_sequences(
            df_features,
            sequence_length=sequence_length,
            target_col=target_col,
            prediction_horizon=prediction_horizon
        )
        
        # XGBoost用データ準備
        X_tab, y_tab = self.feature_engineer.prepare_tabular_data(
            df_features,
            target_col=target_col,
            prediction_horizon=prediction_horizon
        )
        
        # データセットを分割
        # シーケンスデータの分割インデックスを調整
        seq_val_idx = val_idx - sequence_length
        seq_test_idx = test_idx - sequence_length
        
        datasets = {
            'lstm': {
                'X_train': X_seq[:seq_val_idx],
                'y_train': y_seq[:seq_val_idx],
                'X_val': X_seq[seq_val_idx:seq_test_idx],
                'y_val': y_seq[seq_val_idx:seq_test_idx],
                'X_test': X_seq[seq_test_idx:],
                'y_test': y_seq[seq_test_idx:]
            },
            'xgboost': {
                'X_train': X_tab.iloc[:val_idx],
                'y_train': y_tab.iloc[:val_idx],
                'X_val': X_tab.iloc[val_idx:test_idx],
                'y_val': y_tab.iloc[val_idx:test_idx],
                'X_test': X_tab.iloc[test_idx:],
                'y_test': y_tab.iloc[test_idx:]
            }
        }
        
        return datasets
    
    def train(
        self,
        datasets: Dict[str, Any],
        lstm_epochs: int = 50,
        lstm_batch_size: int = 32,
        xgb_early_stopping: int = 50,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        アンサンブルモデルを訓練
        
        Args:
            datasets: prepare_dataで準備したデータセット
            lstm_epochs: LSTMのエポック数
            lstm_batch_size: LSTMのバッチサイズ
            xgb_early_stopping: XGBoostの早期停止ラウンド
            verbose: 詳細出力
        
        Returns:
            訓練結果
        """
        results = {}
        
        # LSTMモデルの訓練
        logger.info("Training LSTM model...")
        lstm_history = self.lstm_model.train(
            datasets['lstm']['X_train'],
            datasets['lstm']['y_train'],
            datasets['lstm']['X_val'],
            datasets['lstm']['y_val'],
            epochs=lstm_epochs,
            batch_size=lstm_batch_size,
            verbose=1 if verbose else 0
        )
        results['lstm'] = lstm_history
        
        # XGBoostモデルの訓練
        logger.info("Training XGBoost model...")
        xgb_results = self.xgboost_model.train(
            datasets['xgboost']['X_train'],
            datasets['xgboost']['y_train'],
            datasets['xgboost']['X_val'],
            datasets['xgboost']['y_val'],
            early_stopping_rounds=xgb_early_stopping,
            verbose=verbose
        )
        results['xgboost'] = xgb_results
        
        # メタ学習器の訓練（必要な場合）
        if self.use_meta_learner:
            logger.info("Training meta-learner...")
            
            # 検証データで各モデルの予測を取得
            lstm_val_pred = self.lstm_model.predict(datasets['lstm']['X_val'])
            xgb_val_pred = self.xgboost_model.predict(datasets['xgboost']['X_val'])
            
            # メタ特徴量を作成
            meta_features = np.column_stack([lstm_val_pred, xgb_val_pred])
            
            # メタ学習器を訓練
            self.meta_learner.fit(meta_features, datasets['lstm']['y_val'])
            
            results['meta_learner'] = {
                'coefficients': self.meta_learner.coef_.tolist(),
                'intercept': float(self.meta_learner.intercept_)
            }
        
        self.is_trained = True
        return results
    
    def predict(
        self,
        lstm_input: Optional[np.ndarray] = None,
        xgboost_input: Optional[pd.DataFrame] = None,
        ensemble_method: str = 'weighted_average'
    ) -> np.ndarray:
        """
        アンサンブル予測を実行
        
        Args:
            lstm_input: LSTM用入力データ
            xgboost_input: XGBoost用入力データ
            ensemble_method: アンサンブル方法 ('weighted_average', 'meta_learner', 'voting')
        
        Returns:
            予測値
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        predictions = []
        
        # LSTM予測
        if lstm_input is not None:
            lstm_pred = self.lstm_model.predict(lstm_input)
            predictions.append(('lstm', lstm_pred))
        
        # XGBoost予測
        if xgboost_input is not None:
            xgb_pred = self.xgboost_model.predict(xgboost_input)
            predictions.append(('xgboost', xgb_pred))
        
        if not predictions:
            raise ValueError("No input data provided")
        
        # アンサンブル
        if ensemble_method == 'weighted_average':
            if len(predictions) == 2:
                final_pred = (self.lstm_weight * predictions[0][1] + 
                            self.xgboost_weight * predictions[1][1])
            else:
                # 単一モデルの場合
                final_pred = predictions[0][1]
                
        elif ensemble_method == 'meta_learner' and self.meta_learner is not None:
            if len(predictions) == 2:
                meta_features = np.column_stack([predictions[0][1], predictions[1][1]])
                final_pred = self.meta_learner.predict(meta_features)
            else:
                final_pred = predictions[0][1]
                
        elif ensemble_method == 'voting':
            # 多数決（分類問題向け、ここでは平均を使用）
            final_pred = np.mean([pred[1] for pred in predictions], axis=0)
            
        else:
            final_pred = predictions[0][1]
        
        return final_pred
    
    def predict_with_confidence(
        self,
        lstm_input: Optional[np.ndarray] = None,
        xgboost_input: Optional[pd.DataFrame] = None,
        confidence_level: float = 0.95,
        n_simulations: int = 100
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        信頼区間付きで予測
        
        Args:
            lstm_input: LSTM用入力データ
            xgboost_input: XGBoost用入力データ
            confidence_level: 信頼水準
            n_simulations: シミュレーション回数
        
        Returns:
            予測値、下限、上限のタプル
        """
        predictions_list = []
        lower_bounds = []
        upper_bounds = []
        
        # LSTM予測（信頼区間付き）
        if lstm_input is not None:
            lstm_pred, lstm_lower, lstm_upper = self.lstm_model.predict_with_confidence(
                lstm_input, n_simulations
            )
            predictions_list.append(lstm_pred)
            lower_bounds.append(lstm_lower)
            upper_bounds.append(lstm_upper)
        
        # XGBoost予測（信頼区間付き）
        if xgboost_input is not None:
            xgb_pred, xgb_lower, xgb_upper = self.xgboost_model.predict_with_confidence(
                xgboost_input, confidence_level
            )
            predictions_list.append(xgb_pred)
            lower_bounds.append(xgb_lower)
            upper_bounds.append(xgb_upper)
        
        # アンサンブル
        if len(predictions_list) == 2:
            final_pred = (self.lstm_weight * predictions_list[0] + 
                        self.xgboost_weight * predictions_list[1])
            final_lower = (self.lstm_weight * lower_bounds[0] + 
                         self.xgboost_weight * lower_bounds[1])
            final_upper = (self.lstm_weight * upper_bounds[0] + 
                         self.xgboost_weight * upper_bounds[1])
        else:
            final_pred = predictions_list[0]
            final_lower = lower_bounds[0]
            final_upper = upper_bounds[0]
        
        return final_pred, final_lower, final_upper
    
    def evaluate(
        self,
        datasets: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        モデルを評価
        
        Args:
            datasets: テストデータセット
        
        Returns:
            評価結果
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        results = {}
        
        # 個別モデルの評価
        results['lstm'] = self.lstm_model.evaluate(
            datasets['lstm']['X_test'],
            datasets['lstm']['y_test']
        )
        
        results['xgboost'] = self.xgboost_model.evaluate(
            datasets['xgboost']['X_test'],
            datasets['xgboost']['y_test']
        )
        
        # アンサンブルモデルの評価
        ensemble_pred = self.predict(
            lstm_input=datasets['lstm']['X_test'],
            xgboost_input=datasets['xgboost']['X_test']
        )
        
        # 最小長に合わせる（LSTMとXGBoostでテストサイズが異なる場合）
        min_len = min(len(ensemble_pred), len(datasets['lstm']['y_test']))
        ensemble_pred = ensemble_pred[:min_len]
        y_true = datasets['lstm']['y_test'][:min_len]
        
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        results['ensemble'] = {
            'mse': float(mean_squared_error(y_true, ensemble_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_true, ensemble_pred))),
            'mae': float(mean_absolute_error(y_true, ensemble_pred)),
            'r2': float(r2_score(y_true, ensemble_pred)),
            'direction_accuracy': float(np.mean((ensemble_pred > 0) == (y_true > 0)))
        }
        
        return results
    
    def save_models(self, filepath_prefix: str):
        """
        モデルを保存
        
        Args:
            filepath_prefix: ファイルパスのプレフィックス
        """
        if not self.is_trained:
            raise ValueError("Models not trained yet")
        
        # 各モデルを保存
        self.lstm_model.save_model(f"{filepath_prefix}_lstm")
        self.xgboost_model.save_model(f"{filepath_prefix}_xgboost")
        
        # アンサンブル設定を保存
        ensemble_config = {
            'lstm_weight': self.lstm_weight,
            'xgboost_weight': self.xgboost_weight,
            'use_meta_learner': self.use_meta_learner
        }
        
        with open(f"{filepath_prefix}_ensemble_config.json", 'w') as f:
            json.dump(ensemble_config, f)
        
        # メタ学習器を保存（必要な場合）
        if self.meta_learner is not None:
            import joblib
            joblib.dump(self.meta_learner, f"{filepath_prefix}_meta_learner.pkl")
        
        logger.info(f"Models saved with prefix: {filepath_prefix}")
    
    def load_models(self, filepath_prefix: str):
        """
        モデルを読み込み
        
        Args:
            filepath_prefix: ファイルパスのプレフィックス
        """
        # 各モデルを読み込み
        self.lstm_model.load_model(f"{filepath_prefix}_lstm")
        self.xgboost_model.load_model(f"{filepath_prefix}_xgboost")
        
        # アンサンブル設定を読み込み
        with open(f"{filepath_prefix}_ensemble_config.json", 'r') as f:
            ensemble_config = json.load(f)
        
        self.lstm_weight = ensemble_config['lstm_weight']
        self.xgboost_weight = ensemble_config['xgboost_weight']
        self.use_meta_learner = ensemble_config['use_meta_learner']
        
        # メタ学習器を読み込み（必要な場合）
        if self.use_meta_learner:
            import joblib
            self.meta_learner = joblib.load(f"{filepath_prefix}_meta_learner.pkl")
        
        self.is_trained = True
        logger.info(f"Models loaded from prefix: {filepath_prefix}")
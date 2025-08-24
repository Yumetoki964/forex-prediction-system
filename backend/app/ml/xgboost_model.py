"""
XGBoostモデル - 勾配ブースティング決定木による為替予測
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
import xgboost as xgb
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import json
import logging

logger = logging.getLogger(__name__)


class XGBoostForexPredictor:
    """為替予測用XGBoostモデル"""
    
    def __init__(
        self,
        objective: str = 'reg:squarederror',
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42
    ):
        """
        Args:
            objective: 目的関数
            n_estimators: 木の数
            max_depth: 木の最大深さ
            learning_rate: 学習率
            subsample: サブサンプリング率
            colsample_bytree: 特徴量のサブサンプリング率
            random_state: 乱数シード
        """
        self.params = {
            'objective': objective,
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'subsample': subsample,
            'colsample_bytree': colsample_bytree,
            'random_state': random_state,
            'tree_method': 'hist',  # 高速化
            'eval_metric': 'rmse'
        }
        
        self.model = None
        self.feature_importance = None
        self.best_params = None
        
    def build_model(self) -> xgb.XGBRegressor:
        """XGBoostモデルを構築"""
        self.model = xgb.XGBRegressor(**self.params)
        return self.model
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        early_stopping_rounds: int = 50,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        モデルを訓練
        
        Args:
            X_train: 訓練データ
            y_train: 訓練ラベル
            X_val: 検証データ
            y_val: 検証ラベル
            early_stopping_rounds: 早期停止のラウンド数
            verbose: 出力の詳細度
        
        Returns:
            訓練結果
        """
        if self.model is None:
            self.build_model()
        
        # 評価セットの準備
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))
        
        # モデルの訓練
        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            early_stopping_rounds=early_stopping_rounds if X_val is not None else None,
            verbose=verbose
        )
        
        # 特徴量重要度を保存
        self.feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # 訓練結果を返す
        results = {
            'n_features': X_train.shape[1],
            'n_samples': X_train.shape[0],
            'best_iteration': self.model.best_iteration if hasattr(self.model, 'best_iteration') else None,
            'best_score': self.model.best_score if hasattr(self.model, 'best_score') else None
        }
        
        return results
    
    def hyperparameter_tuning(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        param_grid: Optional[Dict] = None,
        cv_splits: int = 5,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """
        ハイパーパラメータチューニング
        
        Args:
            X_train: 訓練データ
            y_train: 訓練ラベル
            param_grid: パラメータグリッド
            cv_splits: クロスバリデーションの分割数
            verbose: 出力の詳細度
        
        Returns:
            最適パラメータと結果
        """
        if param_grid is None:
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7, 9],
                'learning_rate': [0.01, 0.05, 0.1, 0.2],
                'subsample': [0.6, 0.8, 1.0],
                'colsample_bytree': [0.6, 0.8, 1.0]
            }
        
        # 時系列クロスバリデーション
        tscv = TimeSeriesSplit(n_splits=cv_splits)
        
        # グリッドサーチ
        base_model = xgb.XGBRegressor(
            objective=self.params['objective'],
            random_state=self.params['random_state'],
            tree_method='hist'
        )
        
        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            cv=tscv,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=verbose
        )
        
        # フィット
        grid_search.fit(X_train, y_train)
        
        # 最適パラメータを保存
        self.best_params = grid_search.best_params_
        self.params.update(self.best_params)
        
        # 最適モデルを保存
        self.model = grid_search.best_estimator_
        
        return {
            'best_params': self.best_params,
            'best_score': -grid_search.best_score_,
            'cv_results': pd.DataFrame(grid_search.cv_results_)
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        予測を実行
        
        Args:
            X: 入力データ
        
        Returns:
            予測値
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        predictions = self.model.predict(X)
        return predictions
    
    def predict_with_confidence(
        self,
        X: pd.DataFrame,
        confidence_level: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        信頼区間付きで予測
        
        Args:
            X: 入力データ
            confidence_level: 信頼水準
        
        Returns:
            予測値、下限、上限のタプル
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # 基本予測
        predictions = self.predict(X)
        
        # XGBoostの予測区間（簡易版）
        # より正確な予測区間を得るには、分位点回帰を使用
        # ここでは標準誤差の推定値を使用
        
        # 訓練データの残差から標準誤差を推定
        # （実際の実装では訓練時に保存しておく）
        std_error = 0.1  # プレースホルダー
        
        # 信頼区間の計算
        z_score = 1.96 if confidence_level == 0.95 else 2.58
        lower_bound = predictions - z_score * std_error
        upper_bound = predictions + z_score * std_error
        
        return predictions, lower_bound, upper_bound
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """
        モデルを評価
        
        Args:
            X_test: テストデータ
            y_test: テストラベル
        
        Returns:
            評価メトリクス
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # 予測
        predictions = self.predict(X_test)
        
        # メトリクスの計算
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        # 方向精度（上昇/下降の予測精度）
        direction_accuracy = np.mean(
            (predictions > 0) == (y_test > 0)
        )
        
        # MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_test - predictions) / (y_test + 1e-10))) * 100
        
        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'r2': float(r2),
            'direction_accuracy': float(direction_accuracy)
        }
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        特徴量重要度を取得
        
        Args:
            top_n: 上位N個の特徴量
        
        Returns:
            特徴量重要度のDataFrame
        """
        if self.feature_importance is None:
            raise ValueError("Model not trained yet")
        
        return self.feature_importance.head(top_n)
    
    def explain_prediction(
        self,
        X: pd.DataFrame,
        feature_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        予測の説明（SHAP値を使用）
        
        Args:
            X: 説明したいデータ
            feature_names: 特徴量名
        
        Returns:
            説明情報
        """
        try:
            import shap
            
            # SHAP Explainerを作成
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)
            
            # 特徴量の寄与度を計算
            if feature_names is None:
                feature_names = X.columns.tolist()
            
            feature_contributions = pd.DataFrame({
                'feature': feature_names,
                'contribution': shap_values[0] if len(shap_values.shape) == 1 else shap_values.mean(axis=0)
            }).sort_values('contribution', key=abs, ascending=False)
            
            return {
                'base_value': float(explainer.expected_value),
                'prediction': float(self.predict(X)[0]),
                'feature_contributions': feature_contributions.to_dict('records')
            }
            
        except ImportError:
            logger.warning("SHAP not installed. Cannot explain predictions.")
            return {}
    
    def save_model(self, filepath: str):
        """
        モデルを保存
        
        Args:
            filepath: 保存先のパス
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # モデルを保存
        joblib.dump(self.model, f"{filepath}_model.pkl")
        
        # パラメータを保存
        with open(f"{filepath}_params.json", 'w') as f:
            json.dump(self.params, f)
        
        # 特徴量重要度を保存
        if self.feature_importance is not None:
            self.feature_importance.to_csv(f"{filepath}_importance.csv", index=False)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        モデルを読み込み
        
        Args:
            filepath: 読み込み元のパス
        """
        # モデルを読み込み
        self.model = joblib.load(f"{filepath}_model.pkl")
        
        # パラメータを読み込み
        with open(f"{filepath}_params.json", 'r') as f:
            self.params = json.load(f)
        
        # 特徴量重要度を読み込み
        try:
            self.feature_importance = pd.read_csv(f"{filepath}_importance.csv")
        except FileNotFoundError:
            self.feature_importance = None
        
        logger.info(f"Model loaded from {filepath}")
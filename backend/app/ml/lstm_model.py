"""
LSTM（Long Short-Term Memory）モデル - 時系列予測用ディープラーニングモデル
"""
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
import logging
import json

logger = logging.getLogger(__name__)


class LSTMForexPredictor:
    """為替予測用LSTMモデル"""
    
    def __init__(
        self,
        sequence_length: int = 60,
        n_features: int = None,
        lstm_units: List[int] = None,
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001
    ):
        """
        Args:
            sequence_length: 入力シーケンスの長さ
            n_features: 特徴量の数
            lstm_units: 各LSTM層のユニット数
            dropout_rate: ドロップアウト率
            learning_rate: 学習率
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units or [128, 64, 32]
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.model = None
        self.scaler = StandardScaler()
        self.history = None
        
    def build_model(self, input_shape: Tuple[int, int]) -> keras.Model:
        """
        LSTMモデルを構築
        
        Args:
            input_shape: 入力の形状 (sequence_length, n_features)
        
        Returns:
            構築されたモデル
        """
        model = models.Sequential()
        
        # 最初のLSTM層
        model.add(layers.LSTM(
            self.lstm_units[0],
            return_sequences=True if len(self.lstm_units) > 1 else False,
            input_shape=input_shape
        ))
        model.add(layers.Dropout(self.dropout_rate))
        
        # 中間LSTM層
        for i in range(1, len(self.lstm_units) - 1):
            model.add(layers.LSTM(self.lstm_units[i], return_sequences=True))
            model.add(layers.Dropout(self.dropout_rate))
        
        # 最後のLSTM層
        if len(self.lstm_units) > 1:
            model.add(layers.LSTM(self.lstm_units[-1], return_sequences=False))
            model.add(layers.Dropout(self.dropout_rate))
        
        # 全結合層
        model.add(layers.Dense(64, activation='relu'))
        model.add(layers.Dropout(self.dropout_rate))
        model.add(layers.Dense(32, activation='relu'))
        
        # 出力層（回帰問題なので活性化関数なし）
        model.add(layers.Dense(1))
        
        # モデルをコンパイル
        optimizer = Adam(learning_rate=self.learning_rate)
        model.compile(
            optimizer=optimizer,
            loss='mse',
            metrics=['mae', 'mape']
        )
        
        self.model = model
        return model
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 100,
        batch_size: int = 32,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """
        モデルを訓練
        
        Args:
            X_train: 訓練データ
            y_train: 訓練ラベル
            X_val: 検証データ
            y_val: 検証ラベル
            epochs: エポック数
            batch_size: バッチサイズ
            verbose: 出力の詳細度
        
        Returns:
            訓練履歴
        """
        if self.model is None:
            input_shape = (X_train.shape[1], X_train.shape[2])
            self.build_model(input_shape)
        
        # コールバックの設定
        callbacks_list = [
            callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=20,
                restore_best_weights=True
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=10,
                min_lr=1e-7,
                verbose=verbose
            )
        ]
        
        # モデルの訓練
        validation_data = (X_val, y_val) if X_val is not None else None
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks_list,
            verbose=verbose
        )
        
        return self.history.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        予測を実行
        
        Args:
            X: 入力データ
        
        Returns:
            予測値
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
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
        
        # モデルの評価
        loss, mae, mape = self.model.evaluate(X_test, y_test, verbose=0)
        
        # 予測
        predictions = self.predict(X_test)
        
        # 追加メトリクスの計算
        from sklearn.metrics import mean_squared_error, r2_score
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, predictions)
        
        # 方向精度（上昇/下降の予測精度）
        direction_accuracy = np.mean(
            (predictions > 0) == (y_test > 0)
        )
        
        return {
            'loss': float(loss),
            'mae': float(mae),
            'mape': float(mape),
            'mse': float(mse),
            'rmse': float(rmse),
            'r2': float(r2),
            'direction_accuracy': float(direction_accuracy)
        }
    
    def save_model(self, filepath: str):
        """
        モデルを保存
        
        Args:
            filepath: 保存先のパス
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # モデルを保存
        self.model.save(f"{filepath}_model.h5")
        
        # 設定を保存
        config = {
            'sequence_length': self.sequence_length,
            'n_features': self.n_features,
            'lstm_units': self.lstm_units,
            'dropout_rate': self.dropout_rate,
            'learning_rate': self.learning_rate
        }
        
        with open(f"{filepath}_config.json", 'w') as f:
            json.dump(config, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        モデルを読み込み
        
        Args:
            filepath: 読み込み元のパス
        """
        # モデルを読み込み
        self.model = keras.models.load_model(f"{filepath}_model.h5")
        
        # 設定を読み込み
        with open(f"{filepath}_config.json", 'r') as f:
            config = json.load(f)
        
        self.sequence_length = config['sequence_length']
        self.n_features = config['n_features']
        self.lstm_units = config['lstm_units']
        self.dropout_rate = config['dropout_rate']
        self.learning_rate = config['learning_rate']
        
        logger.info(f"Model loaded from {filepath}")
    
    def get_model_summary(self) -> str:
        """モデルの概要を取得"""
        if self.model is None:
            return "Model not built yet"
        
        import io
        stream = io.StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()
    
    def predict_with_confidence(
        self,
        X: np.ndarray,
        n_simulations: int = 100
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        信頼区間付きで予測（モンテカルロドロップアウト）
        
        Args:
            X: 入力データ
            n_simulations: シミュレーション回数
        
        Returns:
            予測値、下限、上限のタプル
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # ドロップアウトを有効にして複数回予測
        predictions = []
        
        for _ in range(n_simulations):
            # training=Trueでドロップアウトを有効化
            pred = self.model(X, training=True).numpy().flatten()
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        # 統計量を計算
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        # 95%信頼区間
        lower_bound = mean_pred - 1.96 * std_pred
        upper_bound = mean_pred + 1.96 * std_pred
        
        return mean_pred, lower_bound, upper_bound
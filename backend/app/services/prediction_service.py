"""
予測サービス - モデルの訓練と予測実行
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import logging
import os
import asyncio

from app.models import ExchangeRate, Prediction, PredictionModel, PredictionPeriod
from app.ml.ensemble_model import EnsembleForexPredictor
from app.ml.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class PredictionService:
    """予測サービス - モデル管理と予測実行"""
    
    def __init__(self):
        self.ensemble_model = None
        self.feature_engineer = FeatureEngineer()
        self.model_path = "models/forex_ensemble"
        self.is_model_loaded = False
        
    async def prepare_training_data(
        self,
        db: AsyncSession,
        currency_pair: str = 'USD/JPY',
        days: int = 365
    ) -> pd.DataFrame:
        """
        訓練データを準備
        
        Args:
            db: データベースセッション
            currency_pair: 通貨ペア
            days: データ取得日数
        
        Returns:
            準備されたDataFrame
        """
        try:
            # データを取得
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            query = select(ExchangeRate).where(
                and_(
                    ExchangeRate.date >= start_date,
                    ExchangeRate.date <= end_date
                )
            ).order_by(ExchangeRate.date)
            
            result = await db.execute(query)
            records = result.scalars().all()
            
            if not records:
                raise ValueError("No data found for training")
            
            # DataFrameに変換
            data = []
            for record in records:
                data.append({
                    'date': record.date,
                    'open_rate': float(record.open_rate) if record.open_rate else 0,
                    'high_rate': float(record.high_rate) if record.high_rate else 0,
                    'low_rate': float(record.low_rate) if record.low_rate else 0,
                    'close_rate': float(record.close_rate),
                    'volume': record.volume if record.volume else 0
                })
            
            df = pd.DataFrame(data)
            df.set_index('date', inplace=True)
            
            # 欠損値を補完
            df = df.fillna(method='ffill').fillna(method='bfill')
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            raise
    
    async def train_model(
        self,
        db: AsyncSession,
        currency_pair: str = 'USD/JPY',
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """
        モデルを訓練
        
        Args:
            db: データベースセッション
            currency_pair: 通貨ペア
            force_retrain: 強制的に再訓練するか
        
        Returns:
            訓練結果
        """
        try:
            # 既存モデルがあり、強制再訓練でない場合はスキップ
            if self.is_model_loaded and not force_retrain:
                return {
                    'status': 'skipped',
                    'message': 'Model already loaded. Use force_retrain=True to retrain.'
                }
            
            logger.info(f"Starting model training for {currency_pair}")
            
            # データを準備
            df = await self.prepare_training_data(db, currency_pair)
            
            if len(df) < 100:
                return {
                    'status': 'error',
                    'message': 'Insufficient data for training (need at least 100 records)'
                }
            
            # モデルを初期化
            self.ensemble_model = EnsembleForexPredictor(
                lstm_weight=0.6,
                xgboost_weight=0.4,
                use_meta_learner=True
            )
            
            # データセットを準備
            datasets = await asyncio.get_event_loop().run_in_executor(
                None,
                self.ensemble_model.prepare_data,
                df,
                'close_rate',
                60,  # sequence_length
                1,   # prediction_horizon
                0.2, # test_size
                0.1  # val_size
            )
            
            # モデルを訓練
            train_results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.ensemble_model.train,
                datasets,
                50,  # lstm_epochs
                32,  # lstm_batch_size
                50,  # xgb_early_stopping
                False # verbose
            )
            
            # モデルを評価
            eval_results = await asyncio.get_event_loop().run_in_executor(
                None,
                self.ensemble_model.evaluate,
                datasets
            )
            
            # モデルを保存
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.ensemble_model.save_models,
                self.model_path
            )
            
            self.is_model_loaded = True
            
            return {
                'status': 'success',
                'message': 'Model trained successfully',
                'evaluation': eval_results,
                'data_info': {
                    'total_records': len(df),
                    'date_range': {
                        'start': df.index[0].strftime('%Y-%m-%d'),
                        'end': df.index[-1].strftime('%Y-%m-%d')
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def load_model(self) -> bool:
        """
        保存されたモデルを読み込み
        
        Returns:
            読み込み成功フラグ
        """
        try:
            if self.is_model_loaded:
                return True
            
            # モデルファイルの存在確認
            if not os.path.exists(f"{self.model_path}_ensemble_config.json"):
                logger.warning("Model files not found")
                return False
            
            # モデルを初期化して読み込み
            self.ensemble_model = EnsembleForexPredictor()
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.ensemble_model.load_models,
                self.model_path
            )
            
            self.is_model_loaded = True
            logger.info("Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    async def predict(
        self,
        db: AsyncSession,
        currency_pair: str = 'USD/JPY',
        prediction_periods: List[str] = None
    ) -> Dict[str, Any]:
        """
        予測を実行
        
        Args:
            db: データベースセッション
            currency_pair: 通貨ペア
            prediction_periods: 予測期間のリスト
        
        Returns:
            予測結果
        """
        try:
            # モデルが読み込まれていない場合は読み込み
            if not self.is_model_loaded:
                loaded = await self.load_model()
                if not loaded:
                    # モデルが存在しない場合は訓練
                    train_result = await self.train_model(db, currency_pair)
                    if train_result['status'] != 'success':
                        return train_result
            
            # 最新データを取得
            df = await self.prepare_training_data(db, currency_pair, days=90)
            
            # 特徴量を生成
            df_features = await asyncio.get_event_loop().run_in_executor(
                None,
                self.feature_engineer.create_features,
                df,
                'close_rate'
            )
            
            # 予測期間のデフォルト
            if prediction_periods is None:
                prediction_periods = ['1day', '1week', '2weeks', '1month']
            
            predictions = {}
            current_price = float(df['close_rate'].iloc[-1])
            
            for period in prediction_periods:
                # 期間に応じた予測ホライズンを設定
                if period == '1day':
                    horizon = 1
                elif period == '1week':
                    horizon = 5
                elif period == '2weeks':
                    horizon = 10
                elif period == '1month':
                    horizon = 20
                else:
                    continue
                
                # シーケンスデータを準備
                X_seq, _ = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.feature_engineer.prepare_sequences,
                    df_features,
                    60,  # sequence_length
                    'close_rate',
                    horizon
                )
                
                # 表形式データを準備
                X_tab, _ = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.feature_engineer.prepare_tabular_data,
                    df_features,
                    'close_rate',
                    horizon
                )
                
                # 最新データのみ使用
                if len(X_seq) > 0:
                    X_seq_latest = X_seq[-1:].reshape(1, X_seq.shape[1], X_seq.shape[2])
                else:
                    X_seq_latest = None
                
                if len(X_tab) > 0:
                    X_tab_latest = X_tab.iloc[-1:].reset_index(drop=True)
                else:
                    X_tab_latest = None
                
                # 予測実行
                if X_seq_latest is not None and X_tab_latest is not None:
                    pred_return, lower, upper = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.ensemble_model.predict_with_confidence,
                        X_seq_latest,
                        X_tab_latest
                    )
                    
                    # 価格に変換
                    predicted_price = current_price * (1 + pred_return[0])
                    lower_price = current_price * (1 + lower[0])
                    upper_price = current_price * (1 + upper[0])
                    
                    predictions[period] = {
                        'predicted_rate': float(predicted_price),
                        'confidence_interval': {
                            'lower': float(lower_price),
                            'upper': float(upper_price)
                        },
                        'change_percent': float(pred_return[0] * 100),
                        'signal': self._get_signal(pred_return[0])
                    }
            
            # 予測結果をデータベースに保存
            await self._save_predictions(db, currency_pair, predictions)
            
            return {
                'status': 'success',
                'currency_pair': currency_pair,
                'current_rate': current_price,
                'predictions': predictions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_signal(self, change_rate: float) -> str:
        """
        変化率から売買シグナルを生成
        
        Args:
            change_rate: 予測変化率
        
        Returns:
            シグナル文字列
        """
        if change_rate > 0.02:
            return 'strong_buy'
        elif change_rate > 0.005:
            return 'buy'
        elif change_rate < -0.02:
            return 'strong_sell'
        elif change_rate < -0.005:
            return 'sell'
        else:
            return 'hold'
    
    async def _save_predictions(
        self,
        db: AsyncSession,
        currency_pair: str,
        predictions: Dict[str, Any]
    ):
        """
        予測結果をデータベースに保存
        
        Args:
            db: データベースセッション
            currency_pair: 通貨ペア
            predictions: 予測結果
        """
        try:
            prediction_date = datetime.now().date()
            
            for period_str, pred_data in predictions.items():
                # 期間を変換
                if period_str == '1day':
                    period = PredictionPeriod.ONE_WEEK
                    target_date = prediction_date + timedelta(days=1)
                elif period_str == '1week':
                    period = PredictionPeriod.ONE_WEEK
                    target_date = prediction_date + timedelta(days=7)
                elif period_str == '2weeks':
                    period = PredictionPeriod.TWO_WEEKS
                    target_date = prediction_date + timedelta(days=14)
                elif period_str == '1month':
                    period = PredictionPeriod.ONE_MONTH
                    target_date = prediction_date + timedelta(days=30)
                else:
                    continue
                
                # 既存の予測を確認
                existing = await db.execute(
                    select(Prediction).where(
                        and_(
                            Prediction.prediction_date == prediction_date,
                            Prediction.target_date == target_date,
                            Prediction.model_type == PredictionModel.ENSEMBLE
                        )
                    )
                )
                
                if existing.scalar_one_or_none():
                    continue
                
                # 新しい予測を保存
                prediction = Prediction(
                    prediction_date=prediction_date,
                    target_date=target_date,
                    period=period,
                    predicted_rate=pred_data['predicted_rate'],
                    confidence_interval_lower=pred_data['confidence_interval']['lower'],
                    confidence_interval_upper=pred_data['confidence_interval']['upper'],
                    confidence_level=0.95,
                    prediction_strength=abs(pred_data['change_percent']) / 10,  # 正規化
                    model_type=PredictionModel.ENSEMBLE,
                    model_version='1.0.0'
                )
                
                db.add(prediction)
            
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving predictions: {str(e)}")
    
    async def get_model_status(self) -> Dict[str, Any]:
        """
        モデルのステータスを取得
        
        Returns:
            ステータス情報
        """
        return {
            'is_loaded': self.is_model_loaded,
            'model_path': self.model_path,
            'model_exists': os.path.exists(f"{self.model_path}_ensemble_config.json"),
            'last_check': datetime.now().isoformat()
        }
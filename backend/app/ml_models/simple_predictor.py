"""
Simple Statistical Prediction Model
====================================

統計ベースの簡易予測モデル
- 移動平均ベースのトレンド予測
- ボラティリティベースの信頼区間計算
- 時系列分解による季節性分析
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import math
from statistics import mean, stdev
import logging

logger = logging.getLogger(__name__)


class SimplePredictorModel:
    """
    統計ベース簡易予測モデル
    
    実際の機械学習モデルの代替として使用
    統計的手法による為替レート予測を実行
    """
    
    def __init__(self, model_name: str = "simple_statistical_v1.0"):
        self.model_name = model_name
        self.is_trained = False
        self.training_data = []
        self.model_params = {
            "short_ma_period": 5,
            "long_ma_period": 20,
            "volatility_period": 30,
            "trend_sensitivity": 0.5,
            "confidence_level": 0.95
        }
        
    # ===================================================================
    # モデル学習
    # ===================================================================
    
    def fit(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        モデルを学習
        
        Args:
            historical_data: 過去の為替データ（日付、価格、出来高など）
            
        Returns:
            Dict[str, Any]: 学習結果の統計情報
        """
        try:
            if len(historical_data) < 30:
                raise ValueError("学習に必要な最小データ数（30日分）に達していません")
            
            self.training_data = historical_data.copy()
            
            # 価格データを抽出
            prices = [data["close_rate"] for data in historical_data]
            dates = [data["date"] for data in historical_data]
            
            # 基本統計を計算
            training_stats = self._calculate_training_statistics(prices, dates)
            
            # トレンド分析
            trend_analysis = self._analyze_trend_patterns(prices)
            
            # ボラティリティ分析
            volatility_analysis = self._analyze_volatility_patterns(prices)
            
            # 季節性分析
            seasonal_analysis = self._analyze_seasonal_patterns(historical_data)
            
            # モデルパラメータの最適化
            self._optimize_parameters(prices)
            
            self.is_trained = True
            
            logger.info(f"モデル学習完了: {len(historical_data)}日分のデータで学習")
            
            return {
                "model_name": self.model_name,
                "training_samples": len(historical_data),
                "training_period": f"{dates[0]} to {dates[-1]}",
                "basic_stats": training_stats,
                "trend_analysis": trend_analysis,
                "volatility_analysis": volatility_analysis,
                "seasonal_analysis": seasonal_analysis,
                "model_params": self.model_params.copy(),
                "training_completed": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"モデル学習中にエラー: {str(e)}")
            raise
    
    # ===================================================================
    # 予測実行
    # ===================================================================
    
    def predict(
        self, 
        target_days: int,
        current_rate: float,
        recent_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        指定日数後の為替レートを予測
        
        Args:
            target_days: 予測対象日数（1-30日）
            current_rate: 現在の為替レート
            recent_data: 直近のデータ（オプション）
            
        Returns:
            Dict[str, Any]: 予測結果
        """
        try:
            if not self.is_trained:
                raise RuntimeError("モデルが学習されていません。fit()を先に実行してください")
            
            if target_days < 1 or target_days > 30:
                raise ValueError("予測日数は1-30日の範囲で指定してください")
            
            # 直近データが提供されていない場合は学習データの最新部分を使用
            analysis_data = recent_data[-50:] if recent_data else self.training_data[-50:]
            
            # トレンド分析
            trend_prediction = self._predict_trend_component(
                analysis_data, target_days, current_rate
            )
            
            # ボラティリティ予測
            volatility_prediction = self._predict_volatility_component(
                analysis_data, target_days
            )
            
            # 季節性調整
            seasonal_adjustment = self._predict_seasonal_component(
                analysis_data, target_days
            )
            
            # 最終予測値の計算
            base_prediction = trend_prediction["predicted_rate"]
            seasonal_adjusted = base_prediction + seasonal_adjustment
            
            # 信頼区間の計算
            confidence_interval = self._calculate_confidence_interval(
                seasonal_adjusted,
                volatility_prediction["predicted_volatility"],
                target_days,
                self.model_params["confidence_level"]
            )
            
            # 予測強度の計算
            prediction_strength = self._calculate_prediction_strength(
                trend_prediction, volatility_prediction, target_days
            )
            
            prediction_result = {
                "model_name": self.model_name,
                "prediction_date": datetime.now().isoformat(),
                "target_days": target_days,
                "current_rate": current_rate,
                "predicted_rate": round(seasonal_adjusted, 4),
                "confidence_interval": {
                    "lower": round(confidence_interval[0], 4),
                    "upper": round(confidence_interval[1], 4),
                    "level": self.model_params["confidence_level"]
                },
                "volatility": {
                    "predicted": round(volatility_prediction["predicted_volatility"], 4),
                    "regime": volatility_prediction["regime"]
                },
                "prediction_strength": round(prediction_strength, 3),
                "components": {
                    "trend": round(trend_prediction["trend_component"], 4),
                    "seasonal": round(seasonal_adjustment, 4),
                    "base_prediction": round(base_prediction, 4)
                },
                "model_confidence": round(trend_prediction["confidence"], 3)
            }
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"予測実行中にエラー: {str(e)}")
            raise
    
    # ===================================================================
    # バッチ予測
    # ===================================================================
    
    def predict_multiple_horizons(
        self,
        horizons: List[int],
        current_rate: float,
        recent_data: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        複数の予測期間に対して一度に予測を実行
        
        Args:
            horizons: 予測対象日数のリスト
            current_rate: 現在の為替レート
            recent_data: 直近のデータ（オプション）
            
        Returns:
            List[Dict[str, Any]]: 各期間の予測結果のリスト
        """
        try:
            predictions = []
            
            for horizon in horizons:
                prediction = self.predict(horizon, current_rate, recent_data)
                prediction["horizon"] = horizon
                predictions.append(prediction)
            
            return predictions
            
        except Exception as e:
            logger.error(f"バッチ予測実行中にエラー: {str(e)}")
            raise
    
    # ===================================================================
    # 分析メソッド
    # ===================================================================
    
    def _calculate_training_statistics(
        self, 
        prices: List[float], 
        dates: List[date]
    ) -> Dict[str, Any]:
        """学習データの基本統計を計算"""
        try:
            daily_returns = []
            for i in range(1, len(prices)):
                daily_return = (prices[i] - prices[i-1]) / prices[i-1]
                daily_returns.append(daily_return)
            
            return {
                "price_stats": {
                    "min": round(min(prices), 4),
                    "max": round(max(prices), 4),
                    "mean": round(mean(prices), 4),
                    "std": round(stdev(prices), 4)
                },
                "return_stats": {
                    "mean_daily_return": round(mean(daily_returns), 6),
                    "volatility": round(stdev(daily_returns), 6),
                    "annualized_volatility": round(stdev(daily_returns) * math.sqrt(252), 4)
                },
                "data_quality": {
                    "total_points": len(prices),
                    "date_range": f"{dates[0]} to {dates[-1]}",
                    "coverage_days": (dates[-1] - dates[0]).days + 1
                }
            }
        except Exception:
            return {}
    
    def _analyze_trend_patterns(self, prices: List[float]) -> Dict[str, Any]:
        """トレンドパターンを分析"""
        try:
            # 短期・長期移動平均
            short_ma = self._calculate_moving_average(prices, self.model_params["short_ma_period"])
            long_ma = self._calculate_moving_average(prices, self.model_params["long_ma_period"])
            
            # 現在のトレンド方向
            current_trend = "neutral"
            if short_ma[-1] > long_ma[-1] * 1.002:
                current_trend = "upward"
            elif short_ma[-1] < long_ma[-1] * 0.998:
                current_trend = "downward"
            
            # トレンド強度
            trend_strength = abs(short_ma[-1] - long_ma[-1]) / long_ma[-1]
            
            return {
                "current_trend": current_trend,
                "trend_strength": round(trend_strength, 4),
                "short_ma_current": round(short_ma[-1], 4),
                "long_ma_current": round(long_ma[-1], 4),
                "ma_ratio": round(short_ma[-1] / long_ma[-1], 4)
            }
        except Exception:
            return {"current_trend": "neutral", "trend_strength": 0.0}
    
    def _analyze_volatility_patterns(self, prices: List[float]) -> Dict[str, Any]:
        """ボラティリティパターンを分析"""
        try:
            # 期間別ボラティリティ
            short_vol = self._calculate_volatility(prices, 10)  # 10日
            medium_vol = self._calculate_volatility(prices, 20) # 20日
            long_vol = self._calculate_volatility(prices, 50)   # 50日
            
            # ボラティリティレジーム
            current_vol = short_vol
            regime = "normal"
            if current_vol > long_vol * 1.5:
                regime = "high"
            elif current_vol < long_vol * 0.7:
                regime = "low"
            
            return {
                "current_volatility": round(current_vol, 4),
                "volatility_10d": round(short_vol, 4),
                "volatility_20d": round(medium_vol, 4),
                "volatility_50d": round(long_vol, 4),
                "regime": regime,
                "vol_ratio": round(current_vol / long_vol, 2) if long_vol > 0 else 1.0
            }
        except Exception:
            return {"current_volatility": 0.15, "regime": "normal"}
    
    def _analyze_seasonal_patterns(
        self, 
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """季節性パターンを分析"""
        try:
            # 月別平均リターン
            monthly_returns = {}
            for i in range(1, len(historical_data)):
                current = historical_data[i]
                previous = historical_data[i-1]
                
                month = current["date"].month
                daily_return = (current["close_rate"] - previous["close_rate"]) / previous["close_rate"]
                
                if month not in monthly_returns:
                    monthly_returns[month] = []
                monthly_returns[month].append(daily_return)
            
            # 月別平均計算
            monthly_averages = {}
            for month, returns in monthly_returns.items():
                if returns:
                    monthly_averages[month] = mean(returns)
            
            return {
                "has_seasonal_pattern": len(monthly_averages) > 0,
                "monthly_patterns": monthly_averages,
                "seasonal_strength": 0.1  # 簡易実装のため固定値
            }
        except Exception:
            return {"has_seasonal_pattern": False}
    
    def _optimize_parameters(self, prices: List[float]) -> None:
        """モデルパラメータを最適化（簡易版）"""
        try:
            # 価格データの特性に基づいてパラメータを調整
            price_volatility = self._calculate_volatility(prices, 30)
            
            # ボラティリティに応じてトレンド感度を調整
            if price_volatility > 0.02:
                self.model_params["trend_sensitivity"] = 0.3  # 高ボラ時は感度下げる
            elif price_volatility < 0.01:
                self.model_params["trend_sensitivity"] = 0.7  # 低ボラ時は感度上げる
            
        except Exception:
            pass  # パラメータ最適化に失敗しても続行
    
    # ===================================================================
    # 予測コンポーネント
    # ===================================================================
    
    def _predict_trend_component(
        self,
        analysis_data: List[Dict[str, Any]],
        target_days: int,
        current_rate: float
    ) -> Dict[str, Any]:
        """トレンド成分を予測"""
        try:
            prices = [data["close_rate"] for data in analysis_data]
            
            # 移動平均ベースのトレンド計算
            short_ma = self._calculate_moving_average(prices, self.model_params["short_ma_period"])
            long_ma = self._calculate_moving_average(prices, self.model_params["long_ma_period"])
            
            # トレンド方向と強度
            trend_direction = short_ma[-1] - long_ma[-1]
            trend_strength = abs(trend_direction) / long_ma[-1]
            
            # トレンドの持続性を考慮した予測
            trend_decay = 0.9 ** (target_days / 7)  # 週単位で減衰
            adjusted_trend = trend_direction * trend_decay * self.model_params["trend_sensitivity"]
            
            # 最終予測値
            predicted_rate = current_rate + (adjusted_trend * target_days / self.model_params["short_ma_period"])
            
            # 信頼度計算
            confidence = max(0.5, 1.0 - (target_days / 30) * 0.5)  # 日数が増えるほど信頼度低下
            
            return {
                "predicted_rate": predicted_rate,
                "trend_component": adjusted_trend,
                "trend_direction": "up" if trend_direction > 0 else "down" if trend_direction < 0 else "flat",
                "trend_strength": trend_strength,
                "confidence": confidence
            }
            
        except Exception:
            # フォールバック: 現在レートをベースにした保守的予測
            return {
                "predicted_rate": current_rate * (1 + 0.001 * target_days),
                "trend_component": 0.0,
                "trend_direction": "flat",
                "trend_strength": 0.0,
                "confidence": 0.5
            }
    
    def _predict_volatility_component(
        self,
        analysis_data: List[Dict[str, Any]],
        target_days: int
    ) -> Dict[str, Any]:
        """ボラティリティ成分を予測"""
        try:
            prices = [data["close_rate"] for data in analysis_data]
            
            # 現在のボラティリティ
            current_vol = self._calculate_volatility(prices, self.model_params["volatility_period"])
            
            # 期間調整（ボラティリティは時間と共に拡大）
            time_adjusted_vol = current_vol * math.sqrt(target_days)
            
            # レジーム判定
            long_term_vol = self._calculate_volatility(prices, len(prices) // 2)
            regime = "normal"
            if current_vol > long_term_vol * 1.3:
                regime = "high"
            elif current_vol < long_term_vol * 0.7:
                regime = "low"
            
            return {
                "predicted_volatility": time_adjusted_vol,
                "current_volatility": current_vol,
                "regime": regime,
                "volatility_trend": "increasing" if current_vol > long_term_vol else "decreasing"
            }
            
        except Exception:
            # フォールバック値
            base_vol = 0.15 * math.sqrt(target_days)
            return {
                "predicted_volatility": base_vol,
                "current_volatility": 0.15,
                "regime": "normal",
                "volatility_trend": "stable"
            }
    
    def _predict_seasonal_component(
        self,
        analysis_data: List[Dict[str, Any]],
        target_days: int
    ) -> float:
        """季節性成分を予測"""
        try:
            # 簡易実装: 時期に応じた小さな調整
            current_month = datetime.now().month
            
            # 月別調整係数（経験的）
            monthly_adjustments = {
                1: 0.0002,   # 1月: 新年効果
                2: -0.0001,  # 2月: 冬枯れ
                3: 0.0003,   # 3月: 年度末
                4: 0.0001,   # 4月: 新年度
                5: 0.0000,   # 5月: 中立
                6: -0.0001,  # 6月: 半期末
                7: 0.0002,   # 7月: 夏季
                8: -0.0002,  # 8月: 夏休み
                9: 0.0001,   # 9月: 秋相場
                10: 0.0000,  # 10月: 中立
                11: -0.0001, # 11月: 調整
                12: 0.0003   # 12月: 年末効果
            }
            
            seasonal_factor = monthly_adjustments.get(current_month, 0.0)
            
            # 期間に応じてスケール調整
            return seasonal_factor * target_days
            
        except Exception:
            return 0.0
    
    def _calculate_confidence_interval(
        self,
        predicted_rate: float,
        volatility: float,
        target_days: int,
        confidence_level: float
    ) -> Tuple[float, float]:
        """信頼区間を計算"""
        try:
            # 正規分布仮定でのZ値
            z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
            z_score = z_scores.get(confidence_level, 1.96)
            
            # 信頼区間幅
            interval_width = z_score * volatility * predicted_rate
            
            lower_bound = predicted_rate - interval_width
            upper_bound = predicted_rate + interval_width
            
            return (lower_bound, upper_bound)
            
        except Exception:
            # フォールバック: ±2%の範囲
            margin = predicted_rate * 0.02
            return (predicted_rate - margin, predicted_rate + margin)
    
    def _calculate_prediction_strength(
        self,
        trend_prediction: Dict[str, Any],
        volatility_prediction: Dict[str, Any],
        target_days: int
    ) -> float:
        """予測強度を計算"""
        try:
            # トレンド信頼度
            trend_confidence = trend_prediction.get("confidence", 0.5)
            
            # ボラティリティ信頼度（低ボラほど高信頼）
            vol_factor = 1.0 / (1.0 + volatility_prediction["predicted_volatility"])
            
            # 期間による減衰
            time_decay = 0.95 ** (target_days / 7)
            
            # 総合強度
            strength = trend_confidence * vol_factor * time_decay
            
            return max(0.1, min(1.0, strength))
            
        except Exception:
            return 0.5
    
    # ===================================================================
    # ユーティリティメソッド
    # ===================================================================
    
    def _calculate_moving_average(self, prices: List[float], period: int) -> List[float]:
        """移動平均を計算"""
        if len(prices) < period:
            return [mean(prices)] if prices else [0.0]
        
        moving_averages = []
        for i in range(len(prices)):
            if i < period - 1:
                moving_averages.append(mean(prices[:i+1]))
            else:
                moving_averages.append(mean(prices[i-period+1:i+1]))
        
        return moving_averages
    
    def _calculate_volatility(self, prices: List[float], period: int) -> float:
        """ボラティリティを計算（年率換算）"""
        if len(prices) < 2:
            return 0.15  # デフォルト値
        
        # 日次リターンを計算
        returns = []
        for i in range(1, min(len(prices), period + 1)):
            daily_return = (prices[-i] - prices[-i-1]) / prices[-i-1]
            returns.append(daily_return)
        
        if len(returns) < 2:
            return 0.15
        
        # 年率換算ボラティリティ
        daily_vol = stdev(returns)
        annual_vol = daily_vol * math.sqrt(252)  # 252営業日
        
        return annual_vol
    
    # ===================================================================
    # モデル情報
    # ===================================================================
    
    def get_model_info(self) -> Dict[str, Any]:
        """モデル情報を取得"""
        return {
            "model_name": self.model_name,
            "model_type": "statistical_trend_following",
            "is_trained": self.is_trained,
            "training_samples": len(self.training_data) if self.training_data else 0,
            "parameters": self.model_params.copy(),
            "capabilities": {
                "min_prediction_days": 1,
                "max_prediction_days": 30,
                "provides_confidence_intervals": True,
                "provides_volatility_forecast": True,
                "handles_seasonal_adjustment": True
            }
        }
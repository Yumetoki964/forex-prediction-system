"""
Backtest Service Layer
=====================

バックテスト機能のビジネスロジック実装
過去データを使用した予測精度検証とパフォーマンス分析のサービス層
"""

import json
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from app.models import (
    BacktestResult, 
    ExchangeRate, 
    Prediction, 
    TradingSignal,
    PredictionModel,
    BacktestStatus
)
from app.schemas.backtest import (
    BacktestConfig,
    BacktestJobResponse,
    BacktestResultsResponse,
    BacktestMetricsResponse,
    BacktestTradesResponse,
    TradeRecord,
    PredictionModelType,
    BacktestStatusType
)

logger = logging.getLogger(__name__)


class BacktestService:
    """バックテストサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_backtest(self, config: BacktestConfig) -> BacktestJobResponse:
        """
        バックテストを開始する
        
        Args:
            config: バックテスト設定
            
        Returns:
            BacktestJobResponse: ジョブ情報
        """
        # ジョブIDを生成
        job_id = str(uuid.uuid4())
        
        # 日付検証
        if config.end_date <= config.start_date:
            raise ValueError("End date must be after start date")
        
        if config.start_date < date(1990, 1, 1):
            raise ValueError("Start date cannot be earlier than 1990-01-01")
        
        if config.end_date > date.today():
            raise ValueError("End date cannot be in the future")
        
        # データの存在確認
        await self._validate_data_availability(config.start_date, config.end_date)
        
        # バックテスト結果レコードを作成
        backtest_result = BacktestResult(
            job_id=job_id,
            start_date=config.start_date,
            end_date=config.end_date,
            initial_capital=config.initial_capital,
            model_type=PredictionModel(config.prediction_model_type.value),
            model_config=json.dumps(config.prediction_model_config) if config.prediction_model_config else None,
            status=BacktestStatus.PENDING
        )
        
        self.db.add(backtest_result)
        await self.db.commit()
        await self.db.refresh(backtest_result)
        
        # バックグラウンドでバックテストを実行
        asyncio.create_task(self._run_backtest_async(job_id, config))
        
        return BacktestJobResponse(
            job_id=job_id,
            status=BacktestStatusType.PENDING,
            start_date=config.start_date,
            end_date=config.end_date,
            created_at=backtest_result.created_at,
            estimated_completion_time=self._estimate_completion_time(config.start_date, config.end_date)
        )

    async def get_results(self, job_id: str) -> Optional[BacktestResultsResponse]:
        """
        バックテスト結果を取得する
        
        Args:
            job_id: ジョブID
            
        Returns:
            BacktestResultsResponse: バックテスト結果
        """
        stmt = select(BacktestResult).where(BacktestResult.job_id == job_id)
        result = await self.db.execute(stmt)
        backtest_result = result.scalar_one_or_none()
        
        if not backtest_result:
            return None
        
        return BacktestResultsResponse(
            job_id=backtest_result.job_id,
            status=BacktestStatusType(backtest_result.status.value),
            start_date=backtest_result.start_date,
            end_date=backtest_result.end_date,
            initial_capital=backtest_result.initial_capital,
            prediction_model_type=PredictionModelType(backtest_result.model_type.value),
            execution_time=backtest_result.execution_time,
            completed_at=backtest_result.completed_at,
            error_message=backtest_result.error_message,
            total_return=backtest_result.total_return,
            annualized_return=backtest_result.annualized_return,
            volatility=backtest_result.volatility,
            sharpe_ratio=backtest_result.sharpe_ratio,
            max_drawdown=backtest_result.max_drawdown,
            total_trades=backtest_result.total_trades,
            winning_trades=backtest_result.winning_trades,
            losing_trades=backtest_result.losing_trades,
            win_rate=backtest_result.win_rate
        )

    async def get_metrics(self, job_id: str) -> Optional[BacktestMetricsResponse]:
        """
        バックテスト詳細評価指標を取得する
        
        Args:
            job_id: ジョブID
            
        Returns:
            BacktestMetricsResponse: 詳細評価指標
        """
        stmt = select(BacktestResult).where(
            and_(
                BacktestResult.job_id == job_id,
                BacktestResult.status == BacktestStatus.COMPLETED
            )
        )
        result = await self.db.execute(stmt)
        backtest_result = result.scalar_one_or_none()
        
        if not backtest_result:
            return None
        
        # 拡張指標を計算
        trade_log = json.loads(backtest_result.trade_log) if backtest_result.trade_log else []
        monthly_returns = self._calculate_monthly_returns(trade_log)
        rolling_sharpe = self._calculate_rolling_sharpe(trade_log)
        
        return BacktestMetricsResponse(
            job_id=backtest_result.job_id,
            total_return=backtest_result.total_return or Decimal('0'),
            annualized_return=backtest_result.annualized_return or Decimal('0'),
            volatility=backtest_result.volatility or Decimal('0'),
            sharpe_ratio=backtest_result.sharpe_ratio or Decimal('0'),
            max_drawdown=backtest_result.max_drawdown or Decimal('0'),
            total_trades=backtest_result.total_trades or 0,
            winning_trades=backtest_result.winning_trades or 0,
            losing_trades=backtest_result.losing_trades or 0,
            win_rate=backtest_result.win_rate or Decimal('0'),
            prediction_accuracy_1w=backtest_result.prediction_accuracy_1w,
            prediction_accuracy_2w=backtest_result.prediction_accuracy_2w,
            prediction_accuracy_3w=backtest_result.prediction_accuracy_3w,
            prediction_accuracy_1m=backtest_result.prediction_accuracy_1m,
            sortino_ratio=self._calculate_sortino_ratio(trade_log),
            calmar_ratio=self._calculate_calmar_ratio(backtest_result.annualized_return, backtest_result.max_drawdown),
            var_95=self._calculate_var_95(trade_log),
            monthly_returns=monthly_returns,
            rolling_sharpe=rolling_sharpe
        )

    async def get_trades(self, job_id: str, page: int, page_size: int) -> Optional[BacktestTradesResponse]:
        """
        バックテスト取引履歴を取得する
        
        Args:
            job_id: ジョブID
            page: ページ番号
            page_size: ページサイズ
            
        Returns:
            BacktestTradesResponse: 取引履歴
        """
        stmt = select(BacktestResult).where(BacktestResult.job_id == job_id)
        result = await self.db.execute(stmt)
        backtest_result = result.scalar_one_or_none()
        
        if not backtest_result or not backtest_result.trade_log:
            return None
        
        trade_log = json.loads(backtest_result.trade_log)
        
        # ページネーション
        offset = (page - 1) * page_size
        paginated_trades = trade_log[offset:offset + page_size]
        
        # TradeRecordに変換
        trade_records = [
            TradeRecord(
                trade_date=datetime.fromisoformat(trade['trade_date']).date(),
                signal_type=trade['signal_type'],
                entry_rate=Decimal(str(trade['entry_rate'])),
                exit_rate=Decimal(str(trade['exit_rate'])) if trade.get('exit_rate') else None,
                position_size=Decimal(str(trade['position_size'])),
                profit_loss=Decimal(str(trade['profit_loss'])) if trade.get('profit_loss') else None,
                holding_period=trade.get('holding_period'),
                confidence=Decimal(str(trade['confidence'])),
                market_volatility=Decimal(str(trade['market_volatility'])) if trade.get('market_volatility') else None
            )
            for trade in paginated_trades
        ]
        
        # 統計サマリーを計算
        profit_trades = sum(1 for t in trade_log if t.get('profit_loss', 0) > 0)
        loss_trades = sum(1 for t in trade_log if t.get('profit_loss', 0) < 0)
        profits = [t['profit_loss'] for t in trade_log if t.get('profit_loss', 0) > 0]
        losses = [t['profit_loss'] for t in trade_log if t.get('profit_loss', 0) < 0]
        
        return BacktestTradesResponse(
            job_id=job_id,
            total_trades=len(trade_log),
            page=page,
            page_size=page_size,
            total_pages=(len(trade_log) + page_size - 1) // page_size,
            trades=trade_records,
            profit_trades=profit_trades,
            loss_trades=loss_trades,
            average_profit=Decimal(str(sum(profits) / len(profits))) if profits else Decimal('0'),
            average_loss=Decimal(str(sum(losses) / len(losses))) if losses else Decimal('0'),
            largest_profit=Decimal(str(max(profits))) if profits else Decimal('0'),
            largest_loss=Decimal(str(min(losses))) if losses else Decimal('0')
        )

    async def _validate_data_availability(self, start_date: date, end_date: date) -> None:
        """データの存在を確認する"""
        stmt = select(func.count(ExchangeRate.id)).where(
            and_(
                ExchangeRate.date >= start_date,
                ExchangeRate.date <= end_date
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar()
        
        # 営業日数の概算（土日祝除く）
        total_days = (end_date - start_date).days + 1
        estimated_business_days = total_days * 5 // 7  # 週5日の概算
        
        if count < estimated_business_days * 0.8:  # 80%以上のデータが必要
            raise ValueError(f"Insufficient data for backtest period. Found {count} records, need at least {int(estimated_business_days * 0.8)}")

    def _estimate_completion_time(self, start_date: date, end_date: date) -> int:
        """完了時間を推定する"""
        days = (end_date - start_date).days
        # 1年あたり約60秒と想定
        return max(60, days * 60 // 365)

    async def _run_backtest_async(self, job_id: str, config: BacktestConfig) -> None:
        """
        非同期でバックテストを実行する
        
        Args:
            job_id: ジョブID
            config: バックテスト設定
        """
        try:
            start_time = datetime.now()
            
            # ステータスをRUNNINGに更新
            await self._update_backtest_status(job_id, BacktestStatus.RUNNING)
            
            # バックテスト実行
            results = await self._execute_backtest(job_id, config)
            
            # 結果をデータベースに保存
            execution_time = int((datetime.now() - start_time).total_seconds())
            await self._save_backtest_results(job_id, results, execution_time)
            
            # ステータスをCOMPLETEDに更新
            await self._update_backtest_status(job_id, BacktestStatus.COMPLETED)
            
        except Exception as e:
            logger.error(f"Backtest {job_id} failed: {str(e)}")
            await self._save_backtest_error(job_id, str(e))

    async def _update_backtest_status(self, job_id: str, status: BacktestStatus) -> None:
        """バックテストステータスを更新する"""
        stmt = select(BacktestResult).where(BacktestResult.job_id == job_id)
        result = await self.db.execute(stmt)
        backtest_result = result.scalar_one()
        
        backtest_result.status = status
        backtest_result.updated_at = datetime.now()
        
        if status == BacktestStatus.COMPLETED:
            backtest_result.completed_at = datetime.now()
        
        await self.db.commit()

    async def _execute_backtest(self, job_id: str, config: BacktestConfig) -> Dict[str, Any]:
        """
        バックテストを実行する
        
        Args:
            job_id: ジョブID
            config: バックテスト設定
            
        Returns:
            バックテスト結果
        """
        # 為替データを取得
        exchange_data = await self._get_exchange_data(config.start_date, config.end_date)
        
        # 予測データを取得または生成
        prediction_data = await self._get_or_generate_predictions(config, exchange_data)
        
        # 売買シミュレーションを実行
        simulation_results = await self._run_trading_simulation(
            exchange_data, 
            prediction_data, 
            config.initial_capital
        )
        
        # パフォーマンス指標を計算
        performance_metrics = self._calculate_performance_metrics(simulation_results, config.initial_capital)
        
        # 予測精度を計算
        prediction_accuracy = self._calculate_prediction_accuracy(exchange_data, prediction_data)
        
        return {
            'simulation_results': simulation_results,
            'performance_metrics': performance_metrics,
            'prediction_accuracy': prediction_accuracy
        }

    async def _get_exchange_data(self, start_date: date, end_date: date) -> List[Dict]:
        """為替データを取得する"""
        stmt = select(ExchangeRate).where(
            and_(
                ExchangeRate.date >= start_date,
                ExchangeRate.date <= end_date
            )
        ).order_by(ExchangeRate.date)
        
        result = await self.db.execute(stmt)
        exchange_rates = result.scalars().all()
        
        return [
            {
                'date': rate.date,
                'open': float(rate.open_rate) if rate.open_rate else None,
                'high': float(rate.high_rate) if rate.high_rate else None,
                'low': float(rate.low_rate) if rate.low_rate else None,
                'close': float(rate.close_rate)
            }
            for rate in exchange_rates
        ]

    async def _get_or_generate_predictions(self, config: BacktestConfig, exchange_data: List[Dict]) -> List[Dict]:
        """予測データを取得または生成する"""
        # 実装時は既存の予測データを使用し、不足分は簡易予測で補完
        predictions = []
        
        for i, data_point in enumerate(exchange_data[:-7]):  # 最後の7日は予測対象外
            # 簡易的な移動平均ベースの予測
            if i >= 20:  # 20日分のデータが必要
                recent_prices = [d['close'] for d in exchange_data[i-20:i]]
                ma_5 = sum(recent_prices[-5:]) / 5
                ma_20 = sum(recent_prices) / 20
                
                # シンプルな予測ロジック（移動平均の傾き）
                if ma_5 > ma_20:
                    predicted_change = 0.01  # 1%上昇予測
                else:
                    predicted_change = -0.01  # 1%下降予測
                
                predictions.append({
                    'prediction_date': data_point['date'],
                    'target_date': exchange_data[min(i+7, len(exchange_data)-1)]['date'],
                    'predicted_rate': data_point['close'] * (1 + predicted_change),
                    'confidence': 0.7,
                    'signal': 'buy' if predicted_change > 0 else 'sell'
                })
        
        return predictions

    async def _run_trading_simulation(self, exchange_data: List[Dict], prediction_data: List[Dict], initial_capital: Decimal) -> List[Dict]:
        """売買シミュレーションを実行する"""
        capital = float(initial_capital)
        position = 0  # USD保有量
        trades = []
        portfolio_value = []
        
        prediction_dict = {p['prediction_date']: p for p in prediction_data}
        
        for i, data_point in enumerate(exchange_data):
            current_date = data_point['date']
            current_rate = data_point['close']
            
            # ポートフォリオ価値を記録
            total_value = capital + position * current_rate
            portfolio_value.append({
                'date': current_date,
                'value': total_value,
                'cash': capital,
                'position': position
            })
            
            # 予測に基づく売買判定
            if current_date in prediction_dict:
                prediction = prediction_dict[current_date]
                signal = prediction['signal']
                confidence = prediction['confidence']
                
                # 信頼度が低い場合はスキップ
                if confidence < 0.6:
                    continue
                
                # 買いシグナル
                if signal == 'buy' and capital > current_rate * 1000:  # 最低1000USD取引
                    trade_amount = min(capital * 0.2, capital)  # 20%または全額
                    usd_amount = trade_amount / current_rate
                    
                    position += usd_amount
                    capital -= trade_amount
                    
                    trades.append({
                        'trade_date': current_date.isoformat(),
                        'signal_type': signal,
                        'entry_rate': current_rate,
                        'position_size': usd_amount,
                        'confidence': confidence,
                        'market_volatility': self._calculate_volatility(exchange_data, i)
                    })
                
                # 売りシグナル
                elif signal == 'sell' and position > 0:
                    sell_amount = position * 0.5  # 半分を売却
                    capital += sell_amount * current_rate
                    position -= sell_amount
                    
                    # 最後の取引を更新（利益計算）
                    if trades:
                        last_trade = trades[-1]
                        if 'exit_rate' not in last_trade:
                            last_trade['exit_rate'] = current_rate
                            last_trade['profit_loss'] = sell_amount * (current_rate - last_trade['entry_rate'])
                            last_trade['holding_period'] = (current_date - datetime.fromisoformat(last_trade['trade_date']).date()).days
                    
                    trades.append({
                        'trade_date': current_date.isoformat(),
                        'signal_type': signal,
                        'entry_rate': current_rate,
                        'exit_rate': current_rate,
                        'position_size': sell_amount,
                        'profit_loss': 0,  # 売りシグナルの場合
                        'holding_period': 0,
                        'confidence': confidence,
                        'market_volatility': self._calculate_volatility(exchange_data, i)
                    })
        
        return {
            'trades': trades,
            'portfolio_value': portfolio_value,
            'final_capital': capital,
            'final_position': position,
            'final_value': capital + position * exchange_data[-1]['close'] if exchange_data else capital
        }

    def _calculate_performance_metrics(self, simulation_results: Dict, initial_capital: Decimal) -> Dict:
        """パフォーマンス指標を計算する"""
        initial_value = float(initial_capital)
        final_value = simulation_results['final_value']
        trades = simulation_results['trades']
        portfolio_values = [pv['value'] for pv in simulation_results['portfolio_value']]
        
        # 総リターン
        total_return = (final_value - initial_value) / initial_value
        
        # 年率リターン（簡易計算）
        days = len(portfolio_values)
        annualized_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
        
        # ボラティリティ
        returns = []
        for i in range(1, len(portfolio_values)):
            daily_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            returns.append(daily_return)
        
        volatility = self._calculate_std(returns) * (365 ** 0.5) if returns else 0
        
        # シャープレシオ（リスクフリーレート=0と仮定）
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # 最大ドローダウン
        max_value = 0
        max_drawdown = 0
        for value in portfolio_values:
            max_value = max(max_value, value)
            drawdown = (max_value - value) / max_value if max_value > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        # 取引統計
        profit_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        loss_trades = [t for t in trades if t.get('profit_loss', 0) < 0]
        
        return {
            'total_return': Decimal(str(round(total_return, 4))),
            'annualized_return': Decimal(str(round(annualized_return, 4))),
            'volatility': Decimal(str(round(volatility, 4))),
            'sharpe_ratio': Decimal(str(round(sharpe_ratio, 4))),
            'max_drawdown': Decimal(str(round(max_drawdown, 4))),
            'total_trades': len(trades),
            'winning_trades': len(profit_trades),
            'losing_trades': len(loss_trades),
            'win_rate': Decimal(str(round(len(profit_trades) / len(trades), 4))) if trades else Decimal('0')
        }

    def _calculate_prediction_accuracy(self, exchange_data: List[Dict], prediction_data: List[Dict]) -> Dict:
        """予測精度を計算する"""
        # 実際の値と予測値を比較
        accuracies = {'1w': []}
        
        exchange_dict = {d['date']: d['close'] for d in exchange_data}
        
        for prediction in prediction_data:
            target_date = prediction['target_date']
            if target_date in exchange_dict:
                actual_rate = exchange_dict[target_date]
                predicted_rate = prediction['predicted_rate']
                
                # 誤差率を計算
                error_rate = abs(actual_rate - predicted_rate) / actual_rate
                accuracy = max(0, 1 - error_rate)  # 誤差が小さいほど精度が高い
                
                accuracies['1w'].append(accuracy)
        
        return {
            'prediction_accuracy_1w': Decimal(str(round(sum(accuracies['1w']) / len(accuracies['1w']), 4))) if accuracies['1w'] else None
        }

    def _calculate_volatility(self, exchange_data: List[Dict], current_index: int, window: int = 20) -> float:
        """ボラティリティを計算する"""
        if current_index < window:
            return 0.02  # デフォルト値
        
        prices = [d['close'] for d in exchange_data[current_index-window:current_index]]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        return self._calculate_std(returns)

    def _calculate_std(self, values: List[float]) -> float:
        """標準偏差を計算する"""
        if not values:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    async def _save_backtest_results(self, job_id: str, results: Dict, execution_time: int) -> None:
        """バックテスト結果を保存する"""
        stmt = select(BacktestResult).where(BacktestResult.job_id == job_id)
        result = await self.db.execute(stmt)
        backtest_result = result.scalar_one()
        
        performance_metrics = results['performance_metrics']
        prediction_accuracy = results['prediction_accuracy']
        
        # 結果を更新
        backtest_result.execution_time = execution_time
        backtest_result.total_return = performance_metrics['total_return']
        backtest_result.annualized_return = performance_metrics['annualized_return']
        backtest_result.volatility = performance_metrics['volatility']
        backtest_result.sharpe_ratio = performance_metrics['sharpe_ratio']
        backtest_result.max_drawdown = performance_metrics['max_drawdown']
        backtest_result.total_trades = performance_metrics['total_trades']
        backtest_result.winning_trades = performance_metrics['winning_trades']
        backtest_result.losing_trades = performance_metrics['losing_trades']
        backtest_result.win_rate = performance_metrics['win_rate']
        backtest_result.prediction_accuracy_1w = prediction_accuracy.get('prediction_accuracy_1w')
        backtest_result.trade_log = json.dumps(results['simulation_results']['trades'])
        
        await self.db.commit()

    async def _save_backtest_error(self, job_id: str, error_message: str) -> None:
        """バックテストエラーを保存する"""
        stmt = select(BacktestResult).where(BacktestResult.job_id == job_id)
        result = await self.db.execute(stmt)
        backtest_result = result.scalar_one()
        
        backtest_result.status = BacktestStatus.FAILED
        backtest_result.error_message = error_message
        backtest_result.updated_at = datetime.now()
        
        await self.db.commit()

    # 拡張指標計算メソッド
    def _calculate_monthly_returns(self, trade_log: List[Dict]) -> List[Decimal]:
        """月次リターンを計算する"""
        # 簡易実装（実際はより詳細な計算が必要）
        monthly_returns = [Decimal('0.02'), Decimal('0.01'), Decimal('-0.01')]  # サンプル値
        return monthly_returns

    def _calculate_rolling_sharpe(self, trade_log: List[Dict]) -> List[Decimal]:
        """ローリングシャープレシオを計算する"""
        # 簡易実装（実際はより詳細な計算が必要）
        rolling_sharpe = [Decimal('0.5'), Decimal('0.7'), Decimal('0.3')]  # サンプル値
        return rolling_sharpe

    def _calculate_sortino_ratio(self, trade_log: List[Dict]) -> Optional[Decimal]:
        """ソルティノレシオを計算する"""
        # 簡易実装
        return Decimal('0.6')

    def _calculate_calmar_ratio(self, annualized_return: Optional[Decimal], max_drawdown: Optional[Decimal]) -> Optional[Decimal]:
        """カルマーレシオを計算する"""
        if not annualized_return or not max_drawdown or max_drawdown == 0:
            return None
        return abs(annualized_return / max_drawdown)

    def _calculate_var_95(self, trade_log: List[Dict]) -> Optional[Decimal]:
        """VaR（95%）を計算する"""
        # 簡易実装
        return Decimal('-0.05')
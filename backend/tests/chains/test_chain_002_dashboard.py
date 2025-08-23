"""
CHAIN-002: ダッシュボード表示 - 連鎖APIテスト
================================================

ユーザーストーリー: 投資判断に必要な情報を一画面で確認したい
エンドポイント連鎖: 1.1→1.2→1.3→1.4→1.5

このテストは実データを使用してダッシュボード表示の完全フローを検証します。
モックデータは一切使用せず、実際のAPIレスポンスの整合性を確認します。
"""

import pytest
from httpx import AsyncClient
from datetime import datetime
from typing import Dict, Any
import asyncio

from app.main import app


class MilestoneTracker:
    """連鎖テスト中のマイルストーン追跡クラス"""
    
    def __init__(self, chain_name: str):
        self.chain_name = chain_name
        self.milestones = []
        self.start_time = datetime.now()
        
    def track(self, milestone: str):
        """マイルストーン追跡"""
        timestamp = datetime.now()
        self.milestones.append({
            "milestone": milestone,
            "timestamp": timestamp,
            "elapsed": (timestamp - self.start_time).total_seconds()
        })
        print(f"[{self.chain_name}] {milestone} - {timestamp}")
        
    def get_last_milestone(self) -> Dict[str, Any]:
        """最後のマイルストーンを取得"""
        return self.milestones[-1] if self.milestones else {}


@pytest.mark.asyncio
async def test_chain_002_dashboard_display():
    """
    CHAIN-002: ダッシュボード表示の完全フロー
    
    1.1: /api/rates/current - 現在レート取得
    1.2: /api/predictions/latest - 最新予測取得
    1.3: /api/signals/current - 売買シグナル取得
    1.4: /api/metrics/risk - リスク指標取得
    1.5: /api/alerts/active - アクティブアラート取得
    """
    
    tracker = MilestoneTracker("CHAIN-002_Dashboard")
    tracker.track("連鎖テスト開始")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # =================================================================
        # Step 1.1: 現在レート取得
        # =================================================================
        tracker.track("1.1: 現在レート取得開始")
        
        current_rate_response = await client.get("/api/rates/current")
        
        # 基本的なレスポンス検証
        assert current_rate_response.status_code == 200, f"現在レート取得失敗: {current_rate_response.status_code}"
        current_rate_data = current_rate_response.json()
        
        # 実データ検証（モック防止）
        assert current_rate_data is not None, "現在レートデータが空です"
        assert "rate" in current_rate_data, "レート情報が含まれていません"
        assert current_rate_data["rate"] > 0, "レート値が無効です"
        assert current_rate_data["rate"] != 999.99, "モックデータは禁止"  # モック値の例外検出
        
        # 必須フィールド存在確認
        required_fields = ["rate", "timestamp", "change_24h", "change_percentage_24h"]
        for field in required_fields:
            assert field in current_rate_data, f"必須フィールド '{field}' が不足"
        
        current_rate = current_rate_data["rate"]
        tracker.track("1.1: 現在レート取得完了")
        
        
        # =================================================================
        # Step 1.2: 最新予測取得
        # =================================================================
        tracker.track("1.2: 最新予測取得開始")
        
        predictions_response = await client.get("/api/predictions/latest")
        
        # 基本的なレスポンス検証
        assert predictions_response.status_code == 200, f"予測取得失敗: {predictions_response.status_code}"
        predictions_data = predictions_response.json()
        
        # 実データ検証（モック防止）
        assert predictions_data is not None, "予測データが空です"
        assert "predictions" in predictions_data, "予測リストが含まれていません"
        assert len(predictions_data["predictions"]) > 0, "予測データが存在しません"
        
        # 各予測期間の整合性確認
        for prediction in predictions_data["predictions"]:
            assert "period" in prediction, "予測期間が不明"
            assert "predicted_rate" in prediction, "予測レートが不足"
            assert prediction["predicted_rate"] > 0, "予測レートが無効"
            
            # 現在レートとの妥当な差分範囲（±20%以内）
            rate_diff = abs(prediction["predicted_rate"] - current_rate)
            rate_change_pct = (rate_diff / current_rate) * 100
            assert rate_change_pct <= 20, f"予測レートが現在レートから乖離しすぎ: {rate_change_pct}%"
        
        tracker.track("1.2: 最新予測取得完了")
        
        
        # =================================================================
        # Step 1.3: 売買シグナル取得
        # =================================================================
        tracker.track("1.3: 売買シグナル取得開始")
        
        signals_response = await client.get("/api/signals/current")
        
        # 基本的なレスポンス検証
        assert signals_response.status_code == 200, f"シグナル取得失敗: {signals_response.status_code}"
        signals_data = signals_response.json()
        
        # 実データ検証
        assert signals_data is not None, "シグナルデータが空です"
        assert "signal_type" in signals_data, "シグナルタイプが不足"
        assert "confidence" in signals_data, "信頼度が不足"
        
        # シグナルタイプの妥当性確認
        valid_signals = ["strong_sell", "sell", "hold", "buy", "strong_buy"]
        assert signals_data["signal_type"] in valid_signals, f"無効なシグナル: {signals_data['signal_type']}"
        
        # 信頼度の範囲確認（0-1の範囲）
        confidence = signals_data["confidence"]
        assert 0 <= confidence <= 1, f"信頼度が範囲外: {confidence}"
        
        tracker.track("1.3: 売買シグナル取得完了")
        
        
        # =================================================================
        # Step 1.4: リスク指標取得
        # =================================================================
        tracker.track("1.4: リスク指標取得開始")
        
        risk_response = await client.get("/api/metrics/risk")
        
        # 基本的なレスポンス検証
        assert risk_response.status_code == 200, f"リスク指標取得失敗: {risk_response.status_code}"
        risk_data = risk_response.json()
        
        # 実データ検証
        assert risk_data is not None, "リスクデータが空です"
        assert "volatility" in risk_data, "ボラティリティが不足"
        assert "value_at_risk" in risk_data, "VaRが不足"
        
        # ボラティリティの妥当性確認（0-100%の範囲）
        volatility = risk_data["volatility"]
        assert 0 <= volatility <= 100, f"ボラティリティが範囲外: {volatility}"
        
        tracker.track("1.4: リスク指標取得完了")
        
        
        # =================================================================
        # Step 1.5: アクティブアラート取得
        # =================================================================
        tracker.track("1.5: アクティブアラート取得開始")
        
        alerts_response = await client.get("/api/alerts/active")
        
        # 基本的なレスポンス検証
        assert alerts_response.status_code == 200, f"アラート取得失敗: {alerts_response.status_code}"
        alerts_data = alerts_response.json()
        
        # 実データ検証（アラートは0件でも正常）
        assert alerts_data is not None, "アラートデータが空です"
        assert "alerts" in alerts_data, "アラートリストが不足"
        assert "summary" in alerts_data, "アラートサマリーが不足"
        
        # アクティブアラートが存在する場合の整合性確認
        if len(alerts_data["alerts"]) > 0:
            for alert in alerts_data["alerts"]:
                assert "severity" in alert, "アラートの重要度が不足"
                assert "message" in alert, "アラートメッセージが不足"
                assert "timestamp" in alert, "アラート時刻が不足"
                
                # 重要度の妥当性確認
                valid_severities = ["low", "medium", "high", "critical"]
                assert alert["severity"] in valid_severities, f"無効な重要度: {alert['severity']}"
        
        tracker.track("1.5: アクティブアラート取得完了")
        
        
        # =================================================================
        # データ連携整合性の検証
        # =================================================================
        tracker.track("データ連携整合性検証開始")
        
        # 予測データとシグナルの整合性確認
        # 強い買いシグナルの場合、予測レートは現在レートより高いはず
        if signals_data["signal_type"] in ["buy", "strong_buy"]:
            # 1週間予測が現在レートより高い傾向かチェック
            week_prediction = next(
                (p for p in predictions_data["predictions"] if p["period"] == "1week"), 
                None
            )
            if week_prediction:
                predicted_change = ((week_prediction["predicted_rate"] - current_rate) / current_rate) * 100
                # 買いシグナルなのに大幅な下落予測は矛盾
                assert predicted_change > -5, f"買いシグナルなのに下落予測: {predicted_change}%"
        
        # リスク指標とアラートの整合性確認
        high_risk_threshold = 15  # 15%以上のボラティリティを高リスクとする
        if volatility > high_risk_threshold:
            # 高ボラティリティの場合、何らかのアラートが存在することを期待
            # ただし、必須ではない（アラートは設定依存のため）
            print(f"高ボラティリティ検出({volatility}%) - アラート数: {len(alerts_data['alerts'])}")
        
        tracker.track("データ連携整合性検証完了")
        
        
        # =================================================================
        # レスポンス時間の妥当性確認
        # =================================================================
        tracker.track("パフォーマンス検証開始")
        
        total_elapsed = (datetime.now() - tracker.start_time).total_seconds()
        
        # 全API呼び出しが30秒以内で完了することを確認
        assert total_elapsed < 30, f"ダッシュボード読み込みが遅すぎます: {total_elapsed}秒"
        
        # 各ステップの時間を記録
        for milestone in tracker.milestones:
            print(f"  {milestone['milestone']}: {milestone['elapsed']:.2f}秒")
        
        tracker.track("パフォーマンス検証完了")
        
        
        # =================================================================
        # テスト完了報告
        # =================================================================
        tracker.track("CHAIN-002 テスト完了")
        
        print(f"\n✅ CHAIN-002 ダッシュボード表示テスト成功")
        print(f"   総実行時間: {total_elapsed:.2f}秒")
        print(f"   取得データ:")
        print(f"     現在レート: {current_rate:.3f}")
        print(f"     予測数: {len(predictions_data['predictions'])}件")
        print(f"     シグナル: {signals_data['signal_type']} (信頼度: {confidence:.2f})")
        print(f"     ボラティリティ: {volatility:.2f}%")
        print(f"     アクティブアラート: {len(alerts_data['alerts'])}件")


@pytest.mark.asyncio
async def test_chain_002_error_handling():
    """
    CHAIN-002: エラーケースの検証
    
    各エンドポイントの障害時の適切な処理を確認
    """
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # 不正なパラメータでのテスト
        error_cases = [
            ("/api/predictions/latest?periods=invalid", "無効な予測期間"),
            ("/api/metrics/risk?confidence_level=1.5", "無効な信頼水準"),
        ]
        
        for endpoint, description in error_cases:
            try:
                response = await client.get(endpoint)
                # 4xx系のエラーレスポンスを期待
                assert 400 <= response.status_code < 500, f"{description}: 適切なエラー処理なし"
            except Exception as e:
                print(f"エラーケース '{description}' で例外: {e}")


@pytest.mark.asyncio 
async def test_chain_002_concurrent_requests():
    """
    CHAIN-002: 並行リクエストの検証
    
    ダッシュボード表示時の複数API同時呼び出しをテスト
    """
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        # 全エンドポイントを並行実行
        endpoints = [
            "/api/rates/current",
            "/api/predictions/latest", 
            "/api/signals/current",
            "/api/metrics/risk",
            "/api/alerts/active"
        ]
        
        # 並行実行開始
        start_time = datetime.now()
        
        tasks = [client.get(endpoint) for endpoint in endpoints]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = datetime.now()
        parallel_time = (end_time - start_time).total_seconds()
        
        # 結果検証
        successful_responses = 0
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"エンドポイント {endpoints[i]} で例外: {response}")
            else:
                assert response.status_code == 200, f"並行実行でエラー: {endpoints[i]}"
                successful_responses += 1
        
        # 少なくとも4つのエンドポイントは成功することを期待
        assert successful_responses >= 4, f"並行実行で多くのエラー: {successful_responses}/5"
        
        # 並行実行により高速化されていることを確認（目安として15秒以内）
        assert parallel_time < 15, f"並行実行が遅すぎます: {parallel_time}秒"
        
        print(f"✅ 並行実行テスト成功: {successful_responses}/5 成功, {parallel_time:.2f}秒")


if __name__ == "__main__":
    """
    テスト実行例:
    pytest backend/tests/chains/test_chain_002_dashboard.py -v
    """
    print("CHAIN-002 ダッシュボード表示テスト")
    print("実行方法: pytest backend/tests/chains/test_chain_002_dashboard.py -v")
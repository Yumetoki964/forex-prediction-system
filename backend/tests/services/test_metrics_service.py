"""
Risk Metrics Service Unit Tests
==============================

Tests for the MetricsService class implementing risk analysis and metrics calculations.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.services.metrics_service import MetricsService
from app.schemas.metrics import (
    RiskMetricsResponse,
    TimeHorizon,
    RiskLevel,
    VolatilityRegime
)
from app.models import PriceData


class TestMetricsService:
    """Test cases for MetricsService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def metrics_service(self, mock_db):
        """Create MetricsService instance with mock database"""
        return MetricsService(mock_db)
    
    @pytest.fixture
    def sample_price_data(self):
        """Sample price data for testing"""
        base_date = date.today() - timedelta(days=30)
        return [
            Mock(
                date=base_date + timedelta(days=i),
                close=150.0 + (i * 0.1),
                high=151.0 + (i * 0.1),
                low=149.0 + (i * 0.1),
                volume=1000000 + (i * 1000)
            ) for i in range(30)
        ]
    
    @pytest.mark.asyncio
    async def test_get_risk_metrics_success(self, metrics_service, mock_db, sample_price_data):
        """Test successful risk metrics calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await metrics_service.get_risk_metrics(
            time_horizon=TimeHorizon.DAILY,
            confidence_level=0.95,
            include_stress_test=True
        )
        
        assert isinstance(result, RiskMetricsResponse)
        assert result.time_horizon == TimeHorizon.DAILY
        assert result.confidence_level == 0.95
        assert result.volatility_metrics is not None
        assert result.var_metrics is not None
        assert result.drawdown_metrics is not None
        assert len(result.stress_test_scenarios) > 0
    
    @pytest.mark.asyncio
    async def test_volatility_calculation(self, metrics_service, mock_db, sample_price_data):
        """Test volatility metrics calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await metrics_service.get_risk_metrics()
        volatility = result.volatility_metrics
        
        # Volatility should be positive
        assert volatility.current_volatility > 0
        assert volatility.historical_volatility > 0
        assert volatility.annualized_volatility > 0
        
        # Volatility regime should be valid
        assert volatility.volatility_regime in [regime.value for regime in VolatilityRegime]
        
        # Percentile should be between 0 and 100
        assert 0 <= volatility.percentile_rank <= 100
    
    @pytest.mark.asyncio
    async def test_var_calculation(self, metrics_service, mock_db, sample_price_data):
        """Test Value at Risk calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await metrics_service.get_risk_metrics(confidence_level=0.95)
        var_metrics = result.var_metrics
        
        # VaR should be negative (representing potential loss)
        assert var_metrics.var_1d < 0
        assert var_metrics.var_5d < 0
        assert var_metrics.var_30d < 0
        
        # Expected shortfall should be worse than VaR
        assert var_metrics.expected_shortfall_1d <= var_metrics.var_1d
        
        # Confidence level should match
        assert var_metrics.confidence_level == 0.95
    
    @pytest.mark.asyncio
    async def test_drawdown_calculation(self, metrics_service, mock_db, sample_price_data):
        """Test drawdown metrics calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await metrics_service.get_risk_metrics()
        drawdown = result.drawdown_metrics
        
        # Drawdown should be non-positive
        assert drawdown.current_drawdown <= 0
        assert drawdown.max_drawdown <= 0
        
        # Recovery time should be non-negative
        assert drawdown.recovery_time >= 0
        
        # Underwater periods should be reasonable
        assert drawdown.underwater_periods >= 0
    
    @pytest.mark.asyncio
    async def test_correlation_calculation(self, metrics_service, mock_db, sample_price_data):
        """Test correlation metrics calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await metrics_service.get_risk_metrics()
        correlation = result.correlation_metrics
        
        # Correlation values should be between -1 and 1
        for asset, corr_value in correlation.major_pairs_correlation.items():
            assert -1 <= corr_value <= 1
        
        # Beta should be reasonable
        assert -5 <= correlation.usd_index_beta <= 5
    
    @pytest.mark.asyncio
    async def test_stress_test_scenarios(self, metrics_service, mock_db, sample_price_data):
        """Test stress test scenario generation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await metrics_service.get_risk_metrics(include_stress_test=True)
        scenarios = result.stress_test_scenarios
        
        assert len(scenarios) > 0
        
        for scenario in scenarios:
            assert scenario.scenario_name is not None
            assert scenario.probability > 0
            assert scenario.impact_magnitude != 0
            assert len(scenario.market_conditions) > 0
    
    @pytest.mark.asyncio
    async def test_different_confidence_levels(self, metrics_service, mock_db, sample_price_data):
        """Test risk metrics with different confidence levels"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result_95 = await metrics_service.get_risk_metrics(confidence_level=0.95)
        result_99 = await metrics_service.get_risk_metrics(confidence_level=0.99)
        
        # Higher confidence should result in more conservative (worse) VaR
        assert result_99.var_metrics.var_1d <= result_95.var_metrics.var_1d
    
    @pytest.mark.asyncio
    async def test_empty_data_handling(self, metrics_service, mock_db):
        """Test handling of empty price data"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result = await metrics_service.get_risk_metrics()
        
        # Should still return valid response with fallback data
        assert isinstance(result, RiskMetricsResponse)
        assert result.data_quality == "fallback"
    
    @pytest.mark.asyncio
    async def test_risk_level_classification(self, metrics_service, mock_db, sample_price_data):
        """Test risk level classification"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await metrics_service.get_risk_metrics()
        
        # Overall risk should be a valid enum value
        assert result.overall_risk in [level.value for level in RiskLevel]
        
        # Risk decomposition should add up reasonably
        decomp = result.risk_decomposition
        assert decomp.market_risk >= 0
        assert decomp.volatility_risk >= 0
        assert decomp.liquidity_risk >= 0
    
    @pytest.mark.asyncio
    async def test_time_horizon_variations(self, metrics_service, mock_db, sample_price_data):
        """Test different time horizons"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        daily_result = await metrics_service.get_risk_metrics(TimeHorizon.DAILY)
        weekly_result = await metrics_service.get_risk_metrics(TimeHorizon.WEEKLY)
        
        # Different horizons should have different characteristics
        assert daily_result.time_horizon != weekly_result.time_horizon
        
        # Weekly VaR should generally be worse than daily
        assert abs(weekly_result.var_metrics.var_1d) >= abs(daily_result.var_metrics.var_1d)
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, metrics_service, mock_db):
        """Test error handling when database operations fail"""
        
        mock_db.execute = AsyncMock(side_effect=Exception("Database connection error"))
        
        with pytest.raises(Exception) as exc_info:
            await metrics_service.get_risk_metrics()
        
        assert "Database connection error" in str(exc_info.value)
"""
Indicators Service Unit Tests
============================

Tests for the IndicatorsService class implementing technical and economic indicator analysis.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.services.indicators_service import IndicatorsService
from app.schemas.indicators import (
    TechnicalIndicatorsResponse,
    EconomicImpactResponse,
    EconomicIndicatorCategory,
    TrendDirection,
    IndicatorSignal
)
from app.models import PriceData, EconomicIndicator


class TestIndicatorsService:
    """Test cases for IndicatorsService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def indicators_service(self, mock_db):
        """Create IndicatorsService instance with mock database"""
        return IndicatorsService(mock_db)
    
    @pytest.fixture
    def sample_price_data(self):
        """Sample price data for testing"""
        base_date = date.today() - timedelta(days=50)
        return [
            Mock(
                date=base_date + timedelta(days=i),
                close=150.0 + (i * 0.1),
                high=151.0 + (i * 0.1),
                low=149.0 + (i * 0.1),
                volume=1000000 + (i * 1000)
            ) for i in range(50)
        ]
    
    @pytest.fixture
    def sample_economic_data(self):
        """Sample economic indicator data"""
        return [
            Mock(
                release_date=date.today() - timedelta(days=5),
                indicator_name="US Non-Farm Payrolls",
                category=EconomicIndicatorCategory.EMPLOYMENT,
                actual_value=180000,
                forecast_value=175000,
                previous_value=165000,
                importance="high"
            ),
            Mock(
                release_date=date.today() - timedelta(days=3),
                indicator_name="Japan CPI",
                category=EconomicIndicatorCategory.INFLATION,
                actual_value=2.8,
                forecast_value=2.6,
                previous_value=2.5,
                importance="high"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_get_technical_indicators_success(self, indicators_service, mock_db, sample_price_data):
        """Test successful technical indicators retrieval"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await indicators_service.get_technical_indicators(
            analysis_date=None,
            include_volume=True
        )
        
        assert isinstance(result, TechnicalIndicatorsResponse)
        assert result.analysis_date is not None
        assert result.moving_averages is not None
        assert result.oscillators is not None
        assert result.momentum_indicators is not None
        assert result.volatility_indicators is not None
        assert result.volume_indicators is not None
        assert result.technical_summary is not None
    
    @pytest.mark.asyncio
    async def test_moving_averages_calculation(self, indicators_service, mock_db, sample_price_data):
        """Test moving averages calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await indicators_service.get_technical_indicators()
        ma_indicators = result.moving_averages
        
        # Should have multiple timeframes
        assert ma_indicators.sma_5 > 0
        assert ma_indicators.sma_20 > 0
        assert ma_indicators.sma_50 > 0
        assert ma_indicators.ema_12 > 0
        assert ma_indicators.ema_26 > 0
        
        # Signal should be valid
        assert ma_indicators.signal in [signal.value for signal in IndicatorSignal]
        
        # Trend direction should be valid
        assert ma_indicators.trend_direction in [trend.value for trend in TrendDirection]
    
    @pytest.mark.asyncio
    async def test_oscillators_calculation(self, indicators_service, mock_db, sample_price_data):
        """Test oscillator indicators calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await indicators_service.get_technical_indicators()
        oscillators = result.oscillators
        
        # RSI should be between 0 and 100
        assert 0 <= oscillators.rsi_14 <= 100
        
        # Stochastic should be between 0 and 100
        assert 0 <= oscillators.stoch_k <= 100
        assert 0 <= oscillators.stoch_d <= 100
        
        # Williams %R should be between -100 and 0
        assert -100 <= oscillators.williams_r <= 0
        
        # CCI can be any value but should be reasonable
        assert -500 <= oscillators.cci <= 500
        
        # Signal should be valid
        assert oscillators.signal in [signal.value for signal in IndicatorSignal]
    
    @pytest.mark.asyncio
    async def test_momentum_indicators(self, indicators_service, mock_db, sample_price_data):
        """Test momentum indicators calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await indicators_service.get_technical_indicators()
        momentum = result.momentum_indicators
        
        # MACD values should be reasonable
        assert isinstance(momentum.macd_line, (int, float))
        assert isinstance(momentum.macd_signal, (int, float))
        assert isinstance(momentum.macd_histogram, (int, float))
        
        # ADX should be between 0 and 100
        assert 0 <= momentum.adx <= 100
        
        # ROC should be reasonable percentage
        assert -50 <= momentum.roc <= 50
        
        # Signal should be valid
        assert momentum.signal in [signal.value for signal in IndicatorSignal]
    
    @pytest.mark.asyncio
    async def test_volatility_indicators(self, indicators_service, mock_db, sample_price_data):
        """Test volatility indicators calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await indicators_service.get_technical_indicators()
        volatility = result.volatility_indicators
        
        # ATR should be positive
        assert volatility.atr_14 > 0
        
        # Bollinger Band width should be positive
        assert volatility.bollinger_band_width > 0
        
        # %B should be between 0 and 1 typically (can go outside in extreme cases)
        assert -1 <= volatility.bollinger_percent_b <= 2
        
        # Standard deviation should be positive
        assert volatility.price_std_dev > 0
        
        # Signal should be valid
        assert volatility.signal in [signal.value for signal in IndicatorSignal]
    
    @pytest.mark.asyncio
    async def test_volume_indicators(self, indicators_service, mock_db, sample_price_data):
        """Test volume indicators calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await indicators_service.get_technical_indicators(include_volume=True)
        volume = result.volume_indicators
        
        if volume:  # Only test if volume data is included
            # OBV can be any value
            assert isinstance(volume.obv, (int, float))
            
            # Volume SMA should be positive
            assert volume.volume_sma > 0
            
            # Volume ratio should be positive
            assert volume.volume_ratio > 0
            
            # Signal should be valid
            assert volume.signal in [signal.value for signal in IndicatorSignal]
    
    @pytest.mark.asyncio
    async def test_technical_summary(self, indicators_service, mock_db, sample_price_data):
        """Test technical summary generation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await indicators_service.get_technical_indicators()
        summary = result.technical_summary
        
        # Overall signal should be valid
        assert summary.overall_signal in [signal.value for signal in IndicatorSignal]
        
        # Strength should be between 0 and 1
        assert 0 <= summary.signal_strength <= 1
        
        # Trend should be valid
        assert summary.trend_direction in [trend.value for trend in TrendDirection]
        
        # Confidence should be between 0 and 1
        assert 0 <= summary.confidence_level <= 1
        
        # Should have key levels
        assert len(summary.key_support_levels) > 0
        assert len(summary.key_resistance_levels) > 0
    
    @pytest.mark.asyncio
    async def test_get_economic_impact_success(self, indicators_service, mock_db, sample_economic_data):
        """Test successful economic impact analysis"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_economic_data)
        
        result = await indicators_service.get_economic_impact(
            analysis_date=None,
            include_calendar=True,
            days_ahead=30
        )
        
        assert isinstance(result, EconomicImpactResponse)
        assert result.analysis_date is not None
        assert result.overall_economic_sentiment is not None
        assert 0 <= result.usd_strength_score <= 1
        assert 0 <= result.jpy_strength_score <= 1
        assert len(result.recent_indicators) > 0
        assert len(result.central_bank_policies) > 0
        assert len(result.macro_trends) > 0
        assert result.market_sentiment is not None
    
    @pytest.mark.asyncio
    async def test_economic_indicators_analysis(self, indicators_service, mock_db, sample_economic_data):
        """Test economic indicators analysis"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_economic_data)
        
        result = await indicators_service.get_economic_impact()
        indicators = result.recent_indicators
        
        for indicator in indicators:
            # Should have valid category
            assert indicator.category in [cat.value for cat in EconomicIndicatorCategory]
            
            # Impact magnitude should be between 0 and 1
            assert 0 <= indicator.impact_magnitude <= 1
            
            # Volatility impact should be between 0 and 1
            assert 0 <= indicator.volatility_impact <= 1
            
            # Should have importance level
            assert indicator.importance in ["low", "medium", "high", "critical"]
    
    @pytest.mark.asyncio
    async def test_central_bank_policies(self, indicators_service, mock_db, sample_economic_data):
        """Test central bank policy analysis"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_economic_data)
        
        result = await indicators_service.get_economic_impact()
        policies = result.central_bank_policies
        
        for policy in policies:
            # Should have valid bank name
            assert policy.bank_name is not None
            
            # Current rate should be reasonable
            assert -5 <= policy.current_rate <= 15
            
            # Rate change probabilities should sum to approximately 1
            total_prob = sum(policy.rate_change_probability.values())
            assert 0.9 <= total_prob <= 1.1
            
            # Confidence level should be between 0 and 1
            assert 0 <= policy.confidence_level <= 1
            
            # USD/JPY impact should be between -1 and 1
            assert -1 <= policy.usd_jpy_impact <= 1
    
    @pytest.mark.asyncio
    async def test_macro_trends_analysis(self, indicators_service, mock_db, sample_economic_data):
        """Test macroeconomic trends analysis"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_economic_data)
        
        result = await indicators_service.get_economic_impact()
        trends = result.macro_trends
        
        for trend in trends:
            # Should have country name
            assert trend.country is not None
            
            # GDP growth should be reasonable percentage
            assert -10 <= trend.gdp_growth_trend <= 15
            
            # Inflation should be reasonable percentage  
            assert -5 <= trend.inflation_trend <= 20
            
            # Employment trend should be reasonable
            assert 0 <= trend.employment_trend <= 30
            
            # Economic strength should be between -1 and 1 relative to US
            assert -1 <= trend.economic_strength_vs_us <= 1
            
            # Currency outlook should be valid
            assert trend.currency_outlook in ["bearish", "neutral", "bullish"]
    
    @pytest.mark.asyncio
    async def test_market_sentiment_analysis(self, indicators_service, mock_db, sample_economic_data):
        """Test market sentiment analysis"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_economic_data)
        
        result = await indicators_service.get_economic_impact()
        sentiment = result.market_sentiment
        
        # Fear & Greed Index should be between 0 and 100
        assert 0 <= sentiment.fear_greed_index <= 100
        
        # VIX should be positive
        assert sentiment.vix_level > 0
        
        # Risk signal should be valid
        assert sentiment.risk_on_off_signal in ["risk_on", "risk_off", "neutral"]
        
        # Safe haven demand should be between 0 and 1
        assert 0 <= sentiment.safe_haven_demand <= 1
        
        # Carry trade appetite should be between 0 and 1
        assert 0 <= sentiment.carry_trade_appetite <= 1
    
    @pytest.mark.asyncio
    async def test_economic_calendar_inclusion(self, indicators_service, mock_db, sample_economic_data):
        """Test economic calendar data inclusion"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_economic_data)
        
        with_calendar = await indicators_service.get_economic_impact(include_calendar=True)
        without_calendar = await indicators_service.get_economic_impact(include_calendar=False)
        
        # With calendar should have upcoming events
        if with_calendar.economic_calendar.upcoming_events:
            assert len(with_calendar.economic_calendar.upcoming_events) > 0
        
        # Calendar impact analysis should exist when included
        assert len(with_calendar.economic_calendar.event_impact_analysis) > 0
        
        # Without calendar might have limited calendar data
        assert len(without_calendar.economic_calendar.upcoming_events) == 0
    
    @pytest.mark.asyncio
    async def test_different_analysis_dates(self, indicators_service, mock_db, sample_price_data):
        """Test analysis with different dates"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        today_result = await indicators_service.get_technical_indicators(analysis_date=None)
        past_result = await indicators_service.get_technical_indicators(
            analysis_date=date.today() - timedelta(days=7)
        )
        
        # Both should return valid results
        assert isinstance(today_result, TechnicalIndicatorsResponse)
        assert isinstance(past_result, TechnicalIndicatorsResponse)
        
        # Analysis dates should be different
        assert today_result.analysis_date != past_result.analysis_date
    
    @pytest.mark.asyncio
    async def test_empty_data_handling(self, indicators_service, mock_db):
        """Test handling of empty data"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result = await indicators_service.get_technical_indicators()
        
        # Should still return valid response with fallback data
        assert isinstance(result, TechnicalIndicatorsResponse)
        assert result.data_quality == "fallback"
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, indicators_service, mock_db):
        """Test error handling when database operations fail"""
        
        mock_db.execute = AsyncMock(side_effect=Exception("Database connection error"))
        
        with pytest.raises(Exception) as exc_info:
            await indicators_service.get_technical_indicators()
        
        assert "Database connection error" in str(exc_info.value)
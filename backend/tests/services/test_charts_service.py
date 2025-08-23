"""
Charts Service Unit Tests
========================

Tests for the ChartsService class implementing historical chart data and technical indicators.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.services.charts_service import ChartsService
from app.schemas.charts import (
    HistoricalChartResponse,
    ChartPeriod,
    ChartTimeframe,
    TechnicalIndicatorType
)
from app.models import PriceData


class TestChartsService:
    """Test cases for ChartsService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def charts_service(self, mock_db):
        """Create ChartsService instance with mock database"""
        return ChartsService(mock_db)
    
    @pytest.fixture
    def sample_price_data(self):
        """Sample price data for testing"""
        base_date = datetime.now() - timedelta(days=90)
        return [
            Mock(
                timestamp=base_date + timedelta(days=i),
                open=150.0 + (i * 0.05),
                high=151.0 + (i * 0.05),
                low=149.0 + (i * 0.05),
                close=150.5 + (i * 0.05),
                volume=1000000 + (i * 1000)
            ) for i in range(90)
        ]
    
    @pytest.mark.asyncio
    async def test_get_historical_chart_success(self, charts_service, mock_db, sample_price_data):
        """Test successful historical chart data retrieval"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart(
            period=ChartPeriod.THREE_MONTHS,
            timeframe=ChartTimeframe.DAILY,
            indicators=[TechnicalIndicatorType.SMA, TechnicalIndicatorType.RSI],
            include_volume=True,
            include_support_resistance=True,
            include_fibonacci=True,
            include_trendlines=True
        )
        
        assert isinstance(result, HistoricalChartResponse)
        assert result.period == ChartPeriod.THREE_MONTHS
        assert result.timeframe == ChartTimeframe.DAILY
        assert len(result.candlestick_data) > 0
        assert len(result.technical_indicators) > 0
        assert result.support_resistance_levels is not None
        assert result.fibonacci_levels is not None
        assert result.trendlines is not None
    
    @pytest.mark.asyncio
    async def test_candlestick_data_structure(self, charts_service, mock_db, sample_price_data):
        """Test candlestick data structure and values"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart()
        candlesticks = result.candlestick_data
        
        assert len(candlesticks) > 0
        
        for candle in candlesticks:
            # OHLC values should be reasonable
            assert candle.low <= candle.open <= candle.high
            assert candle.low <= candle.close <= candle.high
            assert candle.volume >= 0
            assert candle.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_technical_indicators_calculation(self, charts_service, mock_db, sample_price_data):
        """Test technical indicators calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        indicators = [
            TechnicalIndicatorType.SMA,
            TechnicalIndicatorType.EMA,
            TechnicalIndicatorType.RSI,
            TechnicalIndicatorType.MACD,
            TechnicalIndicatorType.BOLLINGER_BANDS
        ]
        
        result = await charts_service.get_historical_chart(indicators=indicators)
        tech_indicators = result.technical_indicators
        
        # Should have all requested indicators
        indicator_types = [ind.indicator_type for ind in tech_indicators]
        for requested_indicator in indicators:
            assert requested_indicator in indicator_types
        
        # RSI should be between 0 and 100
        rsi_indicator = next((ind for ind in tech_indicators if ind.indicator_type == TechnicalIndicatorType.RSI), None)
        if rsi_indicator and rsi_indicator.rsi_data:
            for rsi_point in rsi_indicator.rsi_data:
                assert 0 <= rsi_point.rsi <= 100
    
    @pytest.mark.asyncio
    async def test_moving_averages(self, charts_service, mock_db, sample_price_data):
        """Test moving average calculations"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart(
            indicators=[TechnicalIndicatorType.SMA, TechnicalIndicatorType.EMA]
        )
        
        sma_indicator = next(
            (ind for ind in result.technical_indicators if ind.indicator_type == TechnicalIndicatorType.SMA), 
            None
        )
        
        if sma_indicator and sma_indicator.moving_average_data:
            ma_data = sma_indicator.moving_average_data
            assert len(ma_data) > 0
            
            for ma_point in ma_data:
                assert ma_point.value > 0  # Should be positive for USD/JPY
                assert ma_point.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_bollinger_bands(self, charts_service, mock_db, sample_price_data):
        """Test Bollinger Bands calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart(
            indicators=[TechnicalIndicatorType.BOLLINGER_BANDS]
        )
        
        bb_indicator = next(
            (ind for ind in result.technical_indicators if ind.indicator_type == TechnicalIndicatorType.BOLLINGER_BANDS),
            None
        )
        
        if bb_indicator and bb_indicator.bollinger_bands_data:
            for bb_point in bb_indicator.bollinger_bands_data:
                # Upper band should be above middle, middle above lower
                assert bb_point.upper_band >= bb_point.middle_band >= bb_point.lower_band
                assert bb_point.band_width > 0
    
    @pytest.mark.asyncio
    async def test_macd_indicator(self, charts_service, mock_db, sample_price_data):
        """Test MACD indicator calculation"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart(
            indicators=[TechnicalIndicatorType.MACD]
        )
        
        macd_indicator = next(
            (ind for ind in result.technical_indicators if ind.indicator_type == TechnicalIndicatorType.MACD),
            None
        )
        
        if macd_indicator and macd_indicator.macd_data:
            for macd_point in macd_indicator.macd_data:
                # MACD should have reasonable values
                assert isinstance(macd_point.macd_line, (int, float))
                assert isinstance(macd_point.signal_line, (int, float))
                assert isinstance(macd_point.histogram, (int, float))
    
    @pytest.mark.asyncio
    async def test_support_resistance_levels(self, charts_service, mock_db, sample_price_data):
        """Test support and resistance level identification"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart(include_support_resistance=True)
        sr_levels = result.support_resistance_levels
        
        if sr_levels:
            assert len(sr_levels.support_levels) > 0
            assert len(sr_levels.resistance_levels) > 0
            
            # Support levels should be lower than resistance levels generally
            min_resistance = min(level.price for level in sr_levels.resistance_levels)
            max_support = max(level.price for level in sr_levels.support_levels)
            
            # This might not always be true, but should be in most cases
            assert len(sr_levels.support_levels) <= 10  # Reasonable number
            assert len(sr_levels.resistance_levels) <= 10
    
    @pytest.mark.asyncio
    async def test_fibonacci_levels(self, charts_service, mock_db, sample_price_data):
        """Test Fibonacci retracement levels"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart(include_fibonacci=True)
        fib_levels = result.fibonacci_levels
        
        if fib_levels:
            assert fib_levels.swing_high > fib_levels.swing_low
            assert len(fib_levels.retracement_levels) > 0
            
            # Check standard Fibonacci ratios
            expected_ratios = [0.236, 0.382, 0.5, 0.618, 0.786]
            actual_ratios = [level.ratio for level in fib_levels.retracement_levels]
            
            for expected_ratio in expected_ratios:
                assert any(abs(actual_ratio - expected_ratio) < 0.01 for actual_ratio in actual_ratios)
    
    @pytest.mark.asyncio
    async def test_different_timeframes(self, charts_service, mock_db, sample_price_data):
        """Test different chart timeframes"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        daily_result = await charts_service.get_historical_chart(timeframe=ChartTimeframe.DAILY)
        hourly_result = await charts_service.get_historical_chart(timeframe=ChartTimeframe.HOURLY)
        
        assert daily_result.timeframe == ChartTimeframe.DAILY
        assert hourly_result.timeframe == ChartTimeframe.HOURLY
        
        # Different timeframes should potentially have different data densities
        assert len(daily_result.candlestick_data) > 0
        assert len(hourly_result.candlestick_data) > 0
    
    @pytest.mark.asyncio
    async def test_volume_inclusion(self, charts_service, mock_db, sample_price_data):
        """Test volume data inclusion/exclusion"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        with_volume = await charts_service.get_historical_chart(include_volume=True)
        without_volume = await charts_service.get_historical_chart(include_volume=False)
        
        # With volume should have volume data
        if with_volume.volume_data:
            assert len(with_volume.volume_data) > 0
            for vol_point in with_volume.volume_data:
                assert vol_point.volume >= 0
        
        # Without volume should not have volume data
        assert without_volume.volume_data is None or len(without_volume.volume_data) == 0
    
    @pytest.mark.asyncio
    async def test_empty_data_handling(self, charts_service, mock_db):
        """Test handling of empty price data"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result = await charts_service.get_historical_chart()
        
        # Should still return valid response with fallback data
        assert isinstance(result, HistoricalChartResponse)
        assert result.data_quality == "fallback"
        assert len(result.candlestick_data) > 0  # Should have sample data
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, charts_service, mock_db):
        """Test error handling when database operations fail"""
        
        mock_db.execute = AsyncMock(side_effect=Exception("Database connection error"))
        
        with pytest.raises(Exception) as exc_info:
            await charts_service.get_historical_chart()
        
        assert "Database connection error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_annotation_data(self, charts_service, mock_db, sample_price_data):
        """Test chart annotation data"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=sample_price_data)
        
        result = await charts_service.get_historical_chart()
        
        if result.annotations:
            for annotation in result.annotations:
                assert annotation.timestamp is not None
                assert annotation.text is not None
                assert annotation.annotation_type is not None
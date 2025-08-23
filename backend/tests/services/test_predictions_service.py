"""
Predictions Service Unit Tests
=============================

Tests for the PredictionsService class implementing prediction-related business logic.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.services.predictions_service import PredictionsService
from app.schemas.predictions import (
    LatestPredictionsResponse,
    DetailedPredictionsResponse,
    PredictionPeriod
)
from app.models import Prediction


class TestPredictionsService:
    """Test cases for PredictionsService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def predictions_service(self, mock_db):
        """Create PredictionsService instance with mock database"""
        return PredictionsService(mock_db)
    
    @pytest.mark.asyncio
    async def test_get_latest_predictions_success(self, predictions_service, mock_db):
        """Test successful latest predictions retrieval"""
        
        # Mock database query result
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result = await predictions_service.get_latest_predictions()
        
        assert isinstance(result, LatestPredictionsResponse)
        assert result.generated_at is not None
        assert len(result.predictions) > 0
        
        # Check that all required prediction periods are present
        periods = [pred.period for pred in result.predictions]
        assert PredictionPeriod.ONE_WEEK in periods
        assert PredictionPeriod.ONE_MONTH in periods
    
    @pytest.mark.asyncio
    async def test_get_latest_predictions_with_specific_periods(self, predictions_service, mock_db):
        """Test latest predictions with specific periods"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        periods = [PredictionPeriod.ONE_WEEK, PredictionPeriod.TWO_WEEKS]
        result = await predictions_service.get_latest_predictions(periods)
        
        assert len(result.predictions) == 2
        result_periods = [pred.period for pred in result.predictions]
        assert PredictionPeriod.ONE_WEEK in result_periods
        assert PredictionPeriod.TWO_WEEKS in result_periods
        assert PredictionPeriod.ONE_MONTH not in result_periods
    
    @pytest.mark.asyncio
    async def test_get_detailed_predictions_success(self, predictions_service, mock_db):
        """Test successful detailed predictions retrieval"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result = await predictions_service.get_detailed_predictions(
            PredictionPeriod.ONE_WEEK,
            include_feature_importance=True,
            include_scenario_analysis=True
        )
        
        assert isinstance(result, DetailedPredictionsResponse)
        assert result.period == PredictionPeriod.ONE_WEEK
        assert result.primary_prediction is not None
        assert len(result.model_analyses) > 0
        assert len(result.feature_importance) > 0
        assert len(result.scenario_analysis) > 0
    
    @pytest.mark.asyncio
    async def test_get_detailed_predictions_without_optional_data(self, predictions_service, mock_db):
        """Test detailed predictions without optional analysis"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result = await predictions_service.get_detailed_predictions(
            PredictionPeriod.ONE_WEEK,
            include_feature_importance=False,
            include_scenario_analysis=False
        )
        
        assert len(result.feature_importance) == 0
        assert len(result.scenario_analysis) == 0
        assert result.primary_prediction is not None
    
    @pytest.mark.asyncio
    async def test_prediction_value_ranges(self, predictions_service, mock_db):
        """Test that prediction values are within reasonable ranges"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result = await predictions_service.get_latest_predictions()
        
        for prediction in result.predictions:
            # USD/JPY typically ranges from 100-160
            assert 80.0 <= prediction.predicted_value <= 200.0
            assert 0.0 <= prediction.confidence <= 1.0
            assert prediction.lower_bound <= prediction.predicted_value <= prediction.upper_bound
    
    @pytest.mark.asyncio 
    async def test_database_error_handling(self, predictions_service, mock_db):
        """Test error handling when database operations fail"""
        
        mock_db.execute = AsyncMock(side_effect=Exception("Database connection error"))
        
        with pytest.raises(Exception) as exc_info:
            await predictions_service.get_latest_predictions()
        
        assert "Database connection error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_ml_model_integration(self, predictions_service, mock_db):
        """Test integration with ML models"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        with patch('app.services.predictions_service.SimplePredictorModel') as mock_model_class:
            mock_model = Mock()
            mock_model.predict.return_value = {
                'prediction': 150.0,
                'confidence': 0.85,
                'lower_bound': 148.0,
                'upper_bound': 152.0
            }
            mock_model_class.return_value = mock_model
            
            result = await predictions_service.get_latest_predictions()
            
            # Verify model was called
            mock_model_class.assert_called()
            assert len(result.predictions) > 0
    
    @pytest.mark.asyncio
    async def test_prediction_consistency(self, predictions_service, mock_db):
        """Test consistency across multiple calls"""
        
        mock_db.execute = AsyncMock()
        mock_db.execute.return_value.fetchall = Mock(return_value=[])
        
        result1 = await predictions_service.get_latest_predictions()
        result2 = await predictions_service.get_latest_predictions()
        
        # Basic structure should be consistent
        assert len(result1.predictions) == len(result2.predictions)
        assert result1.data_sources == result2.data_sources
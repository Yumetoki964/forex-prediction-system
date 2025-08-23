import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8173';

export interface ChartDataPoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface TechnicalIndicatorData {
  name: string;
  current_value: number;
  signal: 'bullish' | 'bearish' | 'neutral';
  timestamp: string;
}

export interface EconomicIndicatorData {
  name: string;
  impact_level: 'high' | 'medium' | 'low';
  value: number;
  change_percent: number;
  timestamp: string;
}

export interface DetailedPredictionData {
  prediction_1week: number;
  prediction_1month: number;
  confidence_score: number;
  reasoning: string;
  model_type: string;
}

export interface HistoricalChartsResponse {
  data: ChartDataPoint[];
  period: string;
  currency_pair: string;
}

export interface TechnicalIndicatorsResponse {
  indicators: TechnicalIndicatorData[];
  currency_pair: string;
  timestamp: string;
}

export interface EconomicIndicatorsResponse {
  indicators: EconomicIndicatorData[];
  currency_pair: string;
  timestamp: string;
}

export interface DetailedPredictionsResponse {
  prediction: DetailedPredictionData;
  currency_pair: string;
  timestamp: string;
}

// Hook for historical chart data
export const useHistoricalCharts = (period: string = '6m', currencyPair: string = 'USDJPY') => {
  return useQuery({
    queryKey: ['historicalCharts', period, currencyPair],
    queryFn: async (): Promise<HistoricalChartsResponse> => {
      const { data } = await axios.get(
        `${API_BASE_URL}/api/charts/historical`,
        { 
          params: { 
            period,
            currency_pair: currencyPair
          }
        }
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for technical indicators
export const useTechnicalIndicators = (currencyPair: string = 'USDJPY') => {
  return useQuery({
    queryKey: ['technicalIndicators', currencyPair],
    queryFn: async (): Promise<TechnicalIndicatorsResponse> => {
      const { data } = await axios.get(
        `${API_BASE_URL}/api/indicators/technical`,
        { 
          params: { 
            currency_pair: currencyPair
          }
        }
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for economic indicators
export const useEconomicIndicators = (currencyPair: string = 'USDJPY') => {
  return useQuery({
    queryKey: ['economicIndicators', currencyPair],
    queryFn: async (): Promise<EconomicIndicatorsResponse> => {
      const { data } = await axios.get(
        `${API_BASE_URL}/api/indicators/economic`,
        { 
          params: { 
            currency_pair: currencyPair
          }
        }
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for detailed predictions
export const useDetailedPredictions = (currencyPair: string = 'USDJPY') => {
  return useQuery({
    queryKey: ['detailedPredictions', currencyPair],
    queryFn: async (): Promise<DetailedPredictionsResponse> => {
      const { data } = await axios.get(
        `${API_BASE_URL}/api/predictions/detailed`,
        { 
          params: { 
            currency_pair: currencyPair
          }
        }
      );
      return data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for current rate (reusing from dashboard)
export const useCurrentRate = (currencyPair: string = 'USDJPY') => {
  return useQuery({
    queryKey: ['currentRate', currencyPair],
    queryFn: async () => {
      const { data } = await axios.get(
        `${API_BASE_URL}/api/rates/current`,
        { 
          params: { 
            currency_pair: currencyPair
          }
        }
      );
      return data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 1 * 60 * 1000, // Auto-refetch every minute
  });
};
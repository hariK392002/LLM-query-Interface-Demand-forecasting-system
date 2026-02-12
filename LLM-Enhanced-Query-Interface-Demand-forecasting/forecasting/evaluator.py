import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

class ForecastEvaluator:
    '''Evaluate forecast accuracy'''
    
    @staticmethod
    def calculate_metrics(actual, predicted):
        '''
        Calculate forecast accuracy metrics
        
        Args:
            actual: Array of actual values
            predicted: Array of predicted values
        
        Returns:
            dict with metrics
        '''
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        mape = np.mean(np.abs((actual - predicted) / (actual + 1))) * 100  # +1 to avoid division by zero
        
        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape)
        }
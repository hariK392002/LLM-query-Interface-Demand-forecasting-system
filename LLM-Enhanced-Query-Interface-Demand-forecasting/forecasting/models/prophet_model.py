import pandas as pd
import numpy as np
from .base_model import BaseModel

class ProphetForecaster(BaseModel):
    '''Prophet-based forecasting model'''
    
    def __init__(self, seasonality_mode='multiplicative'):
        super().__init__()
        try:
            from prophet import Prophet
            self.Prophet = Prophet
            self.seasonality_mode = seasonality_mode
        except ImportError:
            raise ImportError("Prophet not installed. Install with: pip install prophet")
    
    def fit(self, df):
        '''
        Fit Prophet model
        Args:
            df: DataFrame with 'date' and 'sales' columns
        '''
        # Prepare data for Prophet (needs 'ds' and 'y' columns)
        prophet_df = df[['date', 'sales']].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Initialize and fit model
        self.model = self.Prophet(
            seasonality_mode=self.seasonality_mode,
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True
        )
        
        # Add custom seasonalities if needed
        self.model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Fit model
        self.model.fit(prophet_df)
        self.is_fitted = True
        
        return self
    
    def predict(self, horizon=30):
        '''
        Generate forecast
        Args:
            horizon: Number of days to forecast
        Returns:
            DataFrame with predictions and uncertainty intervals
        '''
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=horizon)
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract last 'horizon' days (future predictions)
        forecast_future = forecast.tail(horizon).copy()
        
        # Rename columns for consistency
        result = pd.DataFrame({
            'date': forecast_future['ds'],
            'predicted_demand': forecast_future['yhat'].clip(lower=0),  # No negative sales
            'lower_bound': forecast_future['yhat_lower'].clip(lower=0),
            'upper_bound': forecast_future['yhat_upper'].clip(lower=0),
            'confidence': 0.95  # Prophet uses 95% confidence interval by default
        })
        
        return result
    
    def get_model_name(self):
        return "Prophet"
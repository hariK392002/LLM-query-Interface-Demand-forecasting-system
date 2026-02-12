import pandas as pd
from .data_preparation import DataPreparation
from forecasting.custom_data_prep import CustomDataPreparation
from .feature_engineering import FeatureEngineer
from .models.model_selector import ModelSelector

class Forecaster:
    '''Main forecasting orchestrator'''
    
    def __init__(self, model_name='prophet'):
        self.data_prep = CustomDataPreparation()
        self.feature_eng = FeatureEngineer()
        self.model_name = model_name
        self.model = None
    
    def generate_forecast(self, item_id, store_id, horizon=28):
        '''
        Complete forecasting pipeline
        
        Args:
            item_id: Item identifier
            store_id: Store identifier
            horizon: Forecast horizon in days
        
        Returns:
            dict with forecast results and metadata
        '''
        try:
            # Step 1: Prepare data
            df = self.data_prep.prepare_forecast_data(item_id, store_id, horizon)
            
            if df.empty or len(df) < 30:  # Need minimum data
                return {
                    'success': False,
                    'error': 'Insufficient data for forecasting (minimum 30 days required)'
                }
            
            # Step 2: Feature engineering (for Prophet, we mainly need date and sales)
            # For other models, use: df = self.feature_eng.create_all_features(df)
            
            # Step 3: Initialize model
            self.model = ModelSelector.get_model(self.model_name)
            
            # Step 4: Fit model
            self.model.fit(df)
            
            # Step 5: Generate predictions
            forecast_df = self.model.predict(horizon=horizon)
            
            # Step 6: Calculate summary statistics
            summary = self._calculate_summary(df, forecast_df)
            
            return {
                'success': True,
                'item_id': item_id,
                'store_id': store_id,
                'horizon': horizon,
                'model_used': self.model.get_model_name(),
                'forecast': forecast_df.to_dict('records'),
                'summary': summary,
                'historical_data': df[['date', 'sales']].tail(30).to_dict('records')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_summary(self, historical_df, forecast_df):
        '''Calculate summary statistics'''
        return {
            'historical_mean': float(historical_df['sales'].mean()),
            'historical_std': float(historical_df['sales'].std()),
            'forecast_mean': float(forecast_df['predicted_demand'].mean()),
            'forecast_total': float(forecast_df['predicted_demand'].sum()),
            'confidence_level': 0.95
        }
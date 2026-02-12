from .prophet_model import ProphetForecaster

class ModelSelector:
    '''Select and initialize appropriate forecasting model'''
    
    @staticmethod
    def get_model(model_name='prophet', **kwargs):
        '''
        Get forecasting model by name
        
        Args:
            model_name: Name of the model ('prophet', 'lstm', 'tft')
            **kwargs: Additional arguments for model initialization
        
        Returns:
            Initialized model instance
        '''
        if model_name.lower() == 'prophet':
            return ProphetForecaster(**kwargs)
        else:
            raise ValueError(f"Model {model_name} not implemented yet")
    
    @staticmethod
    def get_best_model(df):
        '''
        Automatically select best model based on data characteristics
        Currently defaults to Prophet
        '''
        # Future: Add logic to select based on data size, patterns, etc.
        return ProphetForecaster()
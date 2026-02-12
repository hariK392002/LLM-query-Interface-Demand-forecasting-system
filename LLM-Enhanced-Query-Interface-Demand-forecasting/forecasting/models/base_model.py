from abc import ABC, abstractmethod
import pandas as pd

class BaseModel(ABC):
    '''Base class for all forecasting models'''
    
    def __init__(self):
        self.model = None
        self.is_fitted = False
    
    @abstractmethod
    def fit(self, df):
        '''Fit the model to training data'''
        pass
    
    @abstractmethod
    def predict(self, horizon):
        '''Generate predictions for given horizon'''
        pass
    
    @abstractmethod
    def get_model_name(self):
        '''Return model name'''
        pass
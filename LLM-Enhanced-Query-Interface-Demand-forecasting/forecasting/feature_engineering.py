import pandas as pd
import numpy as np

class FeatureEngineer:
    '''Create features for forecasting models'''
    
    def __init__(self):
        pass
    
    def create_time_features(self, df):
        '''
        Create time-based features
        '''
        df = df.copy()
        
        if 'date' in df.columns:
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_month'] = df['date'].dt.day
            df['week_of_year'] = df['date'].dt.isocalendar().week
            df['month'] = df['date'].dt.month
            df['quarter'] = df['date'].dt.quarter
            df['year'] = df['date'].dt.year
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
            df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        return df
    
    def create_lag_features(self, df, lags=[7, 14, 28]):
        '''
        Create lag features
        '''
        df = df.copy()
        
        for lag in lags:
            df[f'sales_lag_{lag}'] = df['sales'].shift(lag)
        
        return df
    
    def create_rolling_features(self, df, windows=[7, 14, 28]):
        '''
        Create rolling window features
        '''
        df = df.copy()
        
        for window in windows:
            df[f'sales_rolling_mean_{window}'] = df['sales'].rolling(window=window).mean()
            df[f'sales_rolling_std_{window}'] = df['sales'].rolling(window=window).std()
            df[f'sales_rolling_max_{window}'] = df['sales'].rolling(window=window).max()
            df[f'sales_rolling_min_{window}'] = df['sales'].rolling(window=window).min()
        
        return df
    
    def create_event_features(self, df):
        '''
        Create event-based features
        '''
        df = df.copy()
        
        # Event flags
        if 'event_name_1' in df.columns:
            df['has_event'] = (~df['event_name_1'].isna()).astype(int)
            df['event_type_cultural'] = (df['event_type_1'] == 'Cultural').astype(int)
            df['event_type_national'] = (df['event_type_1'] == 'National').astype(int)
            df['event_type_religious'] = (df['event_type_1'] == 'Religious').astype(int)
        
        # SNAP features
        if 'snap_CA' in df.columns:
            df['snap_CA'] = df['snap_CA'].fillna(0).astype(int)
        if 'snap_TX' in df.columns:
            df['snap_TX'] = df['snap_TX'].fillna(0).astype(int)
        if 'snap_WI' in df.columns:
            df['snap_WI'] = df['snap_WI'].fillna(0).astype(int)
        
        return df
    
    def create_price_features(self, df):
        '''
        Create price-based features
        '''
        df = df.copy()
        
        if 'sell_price' in df.columns:
            # Price change
            df['price_change'] = df['sell_price'].diff()
            df['price_change_pct'] = df['sell_price'].pct_change()
            
            # Price momentum
            df['price_momentum'] = df['sell_price'].rolling(window=7).mean()
        
        return df
    
    def create_all_features(self, df):
        '''
        Create all features at once
        '''
        df = self.create_time_features(df)
        df = self.create_lag_features(df)
        df = self.create_rolling_features(df)
        df = self.create_event_features(df)
        df = self.create_price_features(df)
        
        # Drop rows with NaN values created by lags and rolling windows
        df = df.dropna()
        
        return df
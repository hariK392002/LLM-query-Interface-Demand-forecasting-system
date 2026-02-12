import pandas as pd
import numpy as np
from database.connection import get_db_connection
from datetime import datetime, timedelta

class DataPreparation:
    '''Prepare and clean data for forecasting'''
    
    def __init__(self):
        self.conn = None
    
    def get_sales_data(self, item_id=None, store_id=None, days=365):
        '''
        Fetch sales data from database
        Args:
            item_id: Specific item (None for all)
            store_id: Specific store (None for all)
            days: Number of days to fetch
        Returns:
            pandas DataFrame with sales data
        '''
        conn = get_db_connection()
        
        # Build query
        query = "SELECT * FROM sales_train"
        conditions = []
        params = []
        
        if item_id:
            conditions.append("item_id = ?")
            params.append(item_id)
        if store_id:
            conditions.append("store_id = ?")
            params.append(store_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " LIMIT 1000"
        
        # Execute query
        df = pd.read_sql_query(query, conn, params=params if params else None)
        return df
    
    def transform_to_timeseries(self, df):
        '''
        Transform wide format (d_1, d_2, ...) to long format time series
        Args:
            df: DataFrame with sales_train data
        Returns:
            DataFrame with [date, item_id, store_id, sales] columns
        '''
        # Get date columns (d_1, d_2, etc.)
        date_cols = [col for col in df.columns if col.startswith('d_')]
        
        # Melt to long format
        id_cols = ['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id']
        id_cols = [col for col in id_cols if col in df.columns]
        
        melted = df.melt(
            id_vars=id_cols,
            value_vars=date_cols,
            var_name='d',
            value_name='sales'
        )
        
        return melted
    
    def merge_calendar_data(self, sales_df):
        '''
        Merge sales data with calendar information
        '''
        conn = get_db_connection()
        
        # Fetch calendar data
        calendar = pd.read_sql_query("SELECT * FROM calendar LIMIT 10000", conn)
        
        # Merge on 'd' column
        merged = sales_df.merge(calendar, on='d', how='left')
        
        return merged
    
    def merge_price_data(self, sales_df):
        '''
        Merge sales data with pricing information
        '''
        conn = get_db_connection()
        
        # Fetch price data
        prices = pd.read_sql_query("SELECT * FROM sell_prices LIMIT 10000", conn)
        
        # Merge on store_id, item_id, and wm_yr_wk
        if 'wm_yr_wk' in sales_df.columns:
            merged = sales_df.merge(
                prices, 
                on=['store_id', 'item_id', 'wm_yr_wk'], 
                how='left'
            )
        else:
            merged = sales_df
        
        return merged
    
    def prepare_forecast_data(self, item_id, store_id, horizon=28):
        '''
        Complete data preparation pipeline for a specific item-store combination
        
        Args:
            item_id: Item identifier
            store_id: Store identifier
            horizon: Forecast horizon in days
        
        Returns:
            Prepared DataFrame ready for forecasting
        '''
        # Fetch sales data
        sales_df = self.get_sales_data(item_id=item_id, store_id=store_id)
        
        if sales_df.empty:
            raise ValueError(f"No data found for item {item_id} in store {store_id}")
        
        # Transform to time series
        ts_df = self.transform_to_timeseries(sales_df)
        
        # Merge calendar data
        ts_df = self.merge_calendar_data(ts_df)
        
        # Merge price data
        ts_df = self.merge_price_data(ts_df)
        
        # Convert date column to datetime
        if 'date' in ts_df.columns:
            ts_df['date'] = pd.to_datetime(ts_df['date'])
        
        # Sort by date
        ts_df = ts_df.sort_values('date')
        
        # Fill missing values
        ts_df['sales'] = ts_df['sales'].fillna(0)
        
        return ts_df
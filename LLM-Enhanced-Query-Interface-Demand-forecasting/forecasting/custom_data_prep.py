import pandas as pd
import numpy as np
from database.connection import get_db_connection
from datetime import datetime, timedelta

class CustomDataPreparation:
    '''Data preparation for melted/long format dataset'''
    
    def __init__(self):
        self.conn = None
    
    def get_sales_data(self, item_id, store_id):
        '''
        Fetch data from sales_long table (melted format)
        Expected columns: date, item_id, store_id, sales
        '''
        conn = get_db_connection()
        
        query = """
            SELECT date, item_id, store_id, sales
            FROM sales_long
            WHERE item_id = ? AND store_id = ?
            ORDER BY date
        """
        
        print(f"[DEBUG] Fetching data for item={item_id}, store={store_id}")
        
        try:
            df = pd.read_sql_query(query, conn, params=[item_id, store_id])
            print(f"[DEBUG] Fetched {len(df)} rows from sales_long")
            
            if not df.empty:
                print(f"[DEBUG] Columns: {df.columns.tolist()}")
                print(f"[DEBUG] First 5 rows:\n{df.head()}")
            
            return df
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch from sales_long: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def merge_calendar_data(self, sales_df):
        '''Merge with calendar table for events'''
        try:
            conn = get_db_connection()
            
            calendar_query = """
                SELECT date, event_name_1, event_type_1, 
                       snap_CA, snap_TX, snap_WI,
                       wday, month, year
                FROM calendar
            """
            
            calendar = pd.read_sql_query(calendar_query, conn)
            calendar['date'] = pd.to_datetime(calendar['date'])
            
            # Merge on date
            merged = sales_df.merge(calendar, on='date', how='left')
            print(f"[DEBUG] After calendar merge: {len(merged)} rows")
            
            return merged
            
        except Exception as e:
            print(f"[WARN] Calendar merge failed: {e}")
            return sales_df
    
    def merge_price_data(self, sales_df):
        '''Merge with pricing data'''
        try:
            conn = get_db_connection()
            
            price_query = """
                SELECT item_id, store_id, wm_yr_wk, sell_price
                FROM sell_prices
            """
            
            prices = pd.read_sql_query(price_query, conn)
            
            # Need to get wm_yr_wk from calendar first
            cal_query = "SELECT date, wm_yr_wk FROM calendar"
            calendar_weeks = pd.read_sql_query(cal_query, conn)
            calendar_weeks['date'] = pd.to_datetime(calendar_weeks['date'])
            
            # Merge to get wm_yr_wk
            sales_with_week = sales_df.merge(
                calendar_weeks, 
                on='date', 
                how='left'
            )
            
            # Now merge prices
            merged = sales_with_week.merge(
                prices,
                on=['item_id', 'store_id', 'wm_yr_wk'],
                how='left'
            )
            
            print(f"[DEBUG] After price merge: {len(merged)} rows")
            
            return merged
            
        except Exception as e:
            print(f"[WARN] Price merge failed: {e}")
            return sales_df
    
    def prepare_forecast_data(self, item_id, store_id, horizon=28):
        '''
        Complete data preparation pipeline for melted/long format
        
        Args:
            item_id: Item identifier
            store_id: Store identifier  
            horizon: Forecast horizon (not used in data prep)
        
        Returns:
            Prepared DataFrame with columns: date, sales, and optional features
        '''
        print(f"\n{'='*60}")
        print(f"DATA PREPARATION - LONG FORMAT")
        print(f"{'='*60}")
        print(f"Item: {item_id}")
        print(f"Store: {store_id}")
        print(f"{'='*60}\n")
        
        # Step 1: Fetch sales data
        df = self.get_sales_data(item_id, store_id)
        
        if df.empty:
            raise ValueError(
                f"❌ No data found for item '{item_id}' in store '{store_id}'.\n\n"
                f"Suggestions:\n"
                f"1. Check if this item-store combination exists\n"
                f"2. Run: SELECT DISTINCT item_id, store_id FROM sales_long LIMIT 10\n"
                f"3. Try a different combination"
            )
        
        # Step 2: Data type conversions
        df['date'] = pd.to_datetime(df['date'])
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        
        # Step 3: Remove duplicates (keep last if any)
        df = df.drop_duplicates(subset=['date'], keep='last')
        
        # Step 4: Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Step 5: Merge additional data (optional)
        df = self.merge_calendar_data(df)
        df = self.merge_price_data(df)
        
        # Step 6: Validate data quality
        print(f"\n[INFO] Data Quality Check:")
        print(f"  ✓ Total days: {len(df)}")
        print(f"  ✓ Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  ✓ Sales range: {df['sales'].min():.2f} to {df['sales'].max():.2f}")
        print(f"  ✓ Average sales: {df['sales'].mean():.2f}")
        print(f"  ✓ Days with sales > 0: {(df['sales'] > 0).sum()}")
        print(f"  ✓ Zero sales days: {(df['sales'] == 0).sum()}")
        
        # Step 7: Check minimum data requirement
        if len(df) < 30:
            raise ValueError(
                f"❌ Insufficient data for forecasting.\n\n"
                f"Found: {len(df)} days\n"
                f"Required: 30 days minimum\n\n"
                f"This item-store combination doesn't have enough historical data."
            )
        
        print(f"\n✅ Data preparation successful!\n")
        
        return df

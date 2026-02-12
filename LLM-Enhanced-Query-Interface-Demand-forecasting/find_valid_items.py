import sqlite3
import pandas as pd

def find_valid_items():
    """Find items with sufficient data in sales_long table"""
    
    print("="*60)
    print("FINDING VALID ITEMS IN SALES_LONG TABLE")
    print("="*60)
    
    conn = sqlite3.connect('database.db')
    
    # Check what columns exist
    print("\n1. Checking sales_long structure...")
    df_sample = pd.read_sql_query("SELECT * FROM sales_long LIMIT 5", conn)
    print(f"   Columns: {df_sample.columns.tolist()}")
    print(f"\n   Sample data:")
    print(df_sample)
    
    # Find items with enough data
    print("\n2. Finding items with 30+ days of data...")
    query = """
        SELECT 
            item_id, 
            store_id, 
            COUNT(*) as total_days,
            MIN(date) as start_date,
            MAX(date) as end_date,
            AVG(sales) as avg_sales
        FROM sales_long
        GROUP BY item_id, store_id
        HAVING COUNT(*) >= 30
        ORDER BY total_days DESC
        LIMIT 20
    """
    
    try:
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            print("   ❌ No items found with 30+ days of data!")
            print("\n   Checking total unique items...")
            total = pd.read_sql_query(
                "SELECT COUNT(DISTINCT item_id || store_id) as total FROM sales_long", 
                conn
            )
            print(f"   Total unique item-store combinations: {total['total'].iloc[0]}")
        else:
            print(f"\n   ✅ Found {len(df)} valid item-store combinations:\n")
            print(df.to_string(index=False))
            
            print("\n" + "="*60)
            print("TRY THESE IN YOUR FORECAST:")
            print("="*60)
            for idx, row in df.head(5).iterrows():
                print(f"\nOption {idx+1}:")
                print(f"  Item ID: {row['item_id']}")
                print(f"  Store ID: {row['store_id']}")
                print(f"  Days of data: {row['total_days']}")
                print(f"  Date range: {row['start_date']} to {row['end_date']}")
                print(f"  Avg daily sales: {row['avg_sales']:.2f}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    find_valid_items()
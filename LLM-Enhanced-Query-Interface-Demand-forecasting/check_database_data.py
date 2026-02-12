import sqlite3
import pandas as pd
from config import Config

def check_database_data():
    """Check database for available data"""
    
    print("=" * 60)
    print("DATABASE DATA CHECKER")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(Config.DATABASE_PATH)
    
    # 1. Check if tables exist
    print("\n1. Checking tables...")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"   Found tables: {tables}")
    
    # 2. Check sales_train table
    if 'sales_train' in tables:
        print("\n2. Checking sales_train table...")
        
        # Get column names
        cursor.execute("PRAGMA table_info(sales_train);")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"   Columns ({len(columns)}): {columns[:10]}... (showing first 10)")
        
        # Count total rows
        cursor.execute("SELECT COUNT(*) FROM sales_train")
        total_rows = cursor.fetchone()[0]
        print(f"   Total rows: {total_rows}")
        
        # Get sample of items and stores
        cursor.execute("SELECT DISTINCT item_id FROM sales_train LIMIT 10")
        items = [row[0] for row in cursor.fetchall()]
        print(f"   Sample Item IDs: {items}")
        
        cursor.execute("SELECT DISTINCT store_id FROM sales_train LIMIT 10")
        stores = [row[0] for row in cursor.fetchall()]
        print(f"   Sample Store IDs: {stores}")
        
        # Check specific item
        test_item = items[0] if items else None
        test_store = stores[0] if stores else None
        
        if test_item and test_store:
            print(f"\n3. Checking data for Item: {test_item}, Store: {test_store}")
            
            # Check if wide format (d_1, d_2, etc.)
            date_cols = [col for col in columns if col.startswith('d_')]
            
            if date_cols:
                print(f"   ✅ Wide format detected: {len(date_cols)} date columns")
                print(f"   Date columns: {date_cols[:5]} ... {date_cols[-5:]}")
                
                # Get data for this item-store
                query = f"""
                    SELECT * FROM sales_train 
                    WHERE item_id = ? AND store_id = ?
                    LIMIT 1
                """
                df = pd.read_sql_query(query, conn, params=[test_item, test_store])
                
                if not df.empty:
                    # Count non-zero sales days
                    sales_values = df[date_cols].values[0]
                    non_zero_days = sum(1 for val in sales_values if val > 0)
                    total_days = len(date_cols)
                    
                    print(f"   Total days of data: {total_days}")
                    print(f"   Days with sales > 0: {non_zero_days}")
                    print(f"   Sample sales values: {sales_values[:10]}")
                    
                    if total_days >= 30:
                        print(f"   ✅ Sufficient data ({total_days} days)")
                    else:
                        print(f"   ❌ Insufficient data ({total_days} days < 30 required)")
                else:
                    print(f"   ❌ No data found for {test_item} at {test_store}")
            else:
                print("   ℹ️  Long format detected (date column format)")
                
                # Check date column
                if 'date' in columns:
                    query = f"""
                        SELECT date, sales FROM sales_train 
                        WHERE item_id = ? AND store_id = ?
                        ORDER BY date
                        LIMIT 100
                    """
                    df = pd.read_sql_query(query, conn, params=[test_item, test_store])
                    
                    if not df.empty:
                        print(f"   Total records: {len(df)}")
                        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
                        print(f"   Sample data:\n{df.head()}")
                        
                        if len(df) >= 30:
                            print(f"   ✅ Sufficient data ({len(df)} days)")
                        else:
                            print(f"   ❌ Insufficient data ({len(df)} days < 30 required)")
                    else:
                        print(f"   ❌ No data found")
    
    # 4. Check calendar table
    if 'calendar' in tables:
        print("\n4. Checking calendar table...")
        cursor.execute("SELECT COUNT(*) FROM calendar")
        cal_rows = cursor.fetchone()[0]
        print(f"   Calendar rows: {cal_rows}")
        
        # Sample calendar data
        cursor.execute("SELECT * FROM calendar LIMIT 5")
        cal_sample = cursor.fetchall()
        print(f"   Sample: {cal_sample[0] if cal_sample else 'Empty'}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    
    if total_rows == 0:
        print("❌ Database is empty!")
        print("   → Load your M5 data into the database")
    elif not date_cols and 'date' not in columns:
        print("❌ No date columns found!")
        print("   → Check your database schema configuration")
    else:
        print("✅ Database structure looks OK")
        print(f"   → Try these working combinations:")
        if items and stores:
            for i in range(min(3, len(items))):
                print(f"      Item: {items[i]}, Store: {stores[i] if i < len(stores) else stores[0]}")

if __name__ == "__main__":
    check_database_data()
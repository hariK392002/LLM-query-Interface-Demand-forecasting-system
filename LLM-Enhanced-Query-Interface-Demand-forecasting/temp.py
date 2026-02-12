import sqlite3
import pandas as pd

DB_PATH = "database.db"
CHUNK_SIZE = 1000  # Adjust as per memory (1000 = safe for 8 GB RAM)

conn = sqlite3.connect(DB_PATH)

print(" Loading calendar table...")
calendar_df = pd.read_sql("SELECT d, date FROM calendar", conn)

print(" Starting chunked transformation...")
offset = 0
chunk_num = 1

# Fetch total row count
total_rows = pd.read_sql("SELECT COUNT(*) AS cnt FROM sales_train_validation", conn)['cnt'][0]

while offset < total_rows:
    print(f"\n Processing chunk {chunk_num} (rows {offset}–{offset + CHUNK_SIZE})")

    # Read a small batch
    query = f"""
        SELECT * FROM sales_train_validation
        LIMIT {CHUNK_SIZE} OFFSET {offset}
    """
    sales_df = pd.read_sql(query, conn)

    # Melt this chunk
    sales_long = sales_df.melt(
        id_vars=['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id'],
        var_name='d',
        value_name='sales'
    )

    # Merge with calendar to get date
    sales_long = sales_long.merge(calendar_df, on='d', how='left')
    sales_long.dropna(subset=['date'], inplace=True)

    # Append to database incrementally
    sales_long.to_sql('sales_long', conn, if_exists='append', index=False)

    print(f"✅ Chunk {chunk_num} written with {len(sales_long):,} rows")

    # Clean up memory
    del sales_df, sales_long

    offset += CHUNK_SIZE
    chunk_num += 1

print("\n All chunks processed successfully!")
conn.close()

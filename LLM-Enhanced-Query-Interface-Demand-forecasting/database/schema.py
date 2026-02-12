from .connection import get_db_connection

def get_schema():
    '''
    Retrieve complete database schema
    Returns dict with table names as keys and column info as values
    '''
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = {}
    for table in tables:
        table_name = table['name']
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        schema[table_name] = {
            'columns': [col['name'] for col in columns],
            'types': {col['name']: col['type'] for col in columns}
        }
    
    return schema

def create_schema_context(schema):
    '''
    Create formatted schema description for LLM context
    '''
    schema_text = "Database Schema:\\n\\n"
    
    for table_name, table_info in schema.items():
        schema_text += f"Table: {table_name}\\n"
        schema_text += "Columns:\\n"
        
        # Limit columns to avoid token overflow
        for col in table_info['columns'][:30]:
            col_type = table_info['types'].get(col, 'TEXT')
            schema_text += f"  - {col} ({col_type})\\n"
        
        if len(table_info['columns']) > 30:
            schema_text += f"  ... and {len(table_info['columns']) - 30} more columns\\n"
        schema_text += "\\n"
    
    return schema_text
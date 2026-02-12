from database.connection import get_db_connection

def execute_query(sql):
    '''
    Execute SQL query and return results
    Returns: dict with success status, columns, data, and row_count
    '''
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Fetch results
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        
        return {
            'success': True,
            'columns': columns,
            'data': results,
            'row_count': len(results)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
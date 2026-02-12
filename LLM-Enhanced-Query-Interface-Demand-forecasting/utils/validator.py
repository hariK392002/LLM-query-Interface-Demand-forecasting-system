import re
from config import Config

def validate_sql(sql):
    '''
    Validate SQL query for safety
    Returns: (is_valid, error_message, modified_sql)
    '''
    sql_lower = sql.lower().strip()
    
    # Check for dangerous operations
    for keyword in Config.DANGEROUS_KEYWORDS:
        if keyword in sql_lower:
            return False, f"Dangerous operation detected: {keyword.upper()}", sql
    
    # Ensure it's a SELECT query
    if not sql_lower.startswith('select'):
        return False, "Only SELECT queries are allowed", sql
    
    # Ensure LIMIT clause exists
    if 'limit' not in sql_lower:
        sql = sql.strip()
        sql += f' LIMIT {Config.DEFAULT_QUERY_LIMIT}'
        return True, None, sql
    
    # Check LIMIT value
    limit_match = re.search(r'limit\\s+(\\d+)', sql_lower)
    if limit_match:
        limit_value = int(limit_match.group(1))
        if limit_value > Config.MAX_QUERY_LIMIT:
            return False, f"LIMIT cannot exceed {Config.MAX_QUERY_LIMIT} rows", sql
    
    return True, None, sql
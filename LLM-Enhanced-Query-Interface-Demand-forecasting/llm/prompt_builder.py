from database.schema import create_schema_context

def build_sql_prompt(natural_query, schema):
    '''
    Build prompt for SQL generation
    '''
    schema_context = create_schema_context(schema)
    
    prompt = f"""You are an expert SQL query generator for an M5 forecasting inventory database.

{schema_context}

Important Rules:
1.ALWAYS include a LIMIT clause (max 1000 rows)
2.Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
3.Use the sales_long table for sales data instead of wide-format columns
4.Each row in sales_long represents daily sales with columns (item_id, store_id, date, sales)
5.Use the most recent date column for current sales analysis
6.Return ONLY the SQL query without any explanation, markdown, or code blocks
7.Do not include semicolons at the end
8.Use proper SQL syntax for SQLite

Natural Language Query: {natural_query}

Generate the SQL query:"""
    
    return prompt

def build_explanation_prompt(sql):
    '''
    Build prompt for SQL explanation
    '''
    prompt = f"""Explain this SQL query in one concise sentence:
{sql}

Explanation:"""
    
    return prompt

def build_natural_language_answer_prompt(natural_query, sql, results):
    '''
    Build prompt to convert query results into natural language answer
    '''
    # Format results for the prompt (limit to avoid token overflow)
    results_summary = format_results_for_prompt(results)
    
    prompt = f"""You are a helpful data analyst assistant. Convert the SQL query results into a clear, natural language answer.

Original Question: {natural_query}

SQL Query Used: {sql}

Query Results:
{results_summary}

Instructions:
1. Provide a direct, conversational answer to the original question
2. Include specific numbers and facts from the results
3. Be concise but informative
4. If there are multiple results, summarize key insights
5. Use bullet points for lists when appropriate
6. Don't mention SQL or technical details unless relevant

Natural Language Answer:"""
    
    return prompt

def format_results_for_prompt(results):
    '''
    Format query results into a readable string for the LLM prompt
    '''
    if not results['success']:
        return "No results available"
    
    data = results['data']
    columns = results['columns']
    row_count = results['row_count']
    
    if row_count == 0:
        return "No data found"
    
    # Limit rows to avoid token overflow
    max_rows = min(50, row_count)
    
    formatted = f"Total Rows: {row_count}\nColumns: {', '.join(columns)}\n\n"
    formatted += "Sample Data:\n"
    
    for i, row in enumerate(data[:max_rows]):
        formatted += f"Row {i+1}: "
        row_parts = []
        for col in columns:
            value = row.get(col, 'NULL')
            row_parts.append(f"{col}={value}")
        formatted += ", ".join(row_parts)
        formatted += "\n"
    
    if row_count > max_rows:
        formatted += f"\n... and {row_count - max_rows} more rows\n"
    
    return formatted
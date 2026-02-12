from flask import Blueprint, jsonify, request
from database.schema import get_schema
from llm.gemini_client import GeminiClient
from llm.prompt_builder import (
    build_sql_prompt, 
    build_explanation_prompt,
    build_natural_language_answer_prompt
)
from utils.validator import validate_sql
from utils.executor import execute_query

api_bp = Blueprint('api', __name__, url_prefix='/api')
gemini_client = GeminiClient()

@api_bp.route('/query', methods=['POST'])
def api_query():
    '''
    API endpoint for programmatic query access
    POST /api/query
    Body: {"query": "natural language query", "include_raw_data": true/false}
    '''
    data = request.get_json()
    natural_query = data.get('query', '')
    include_raw_data = data.get('include_raw_data', True)
    
    if not natural_query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    schema = get_schema()
    
    try:
        # Generate SQL using Gemini
        sql_prompt = build_sql_prompt(natural_query, schema)
        sql = gemini_client.generate_sql(sql_prompt)
        
        # Generate explanation
        explanation_prompt = build_explanation_prompt(sql)
        explanation = gemini_client.generate_explanation(explanation_prompt)
        
        # Validate SQL
        is_valid, error_msg, sql = validate_sql(sql)
        
        if not is_valid:
            return jsonify({
                'error': error_msg,
                'sql': sql,
                'explanation': explanation
            }), 400
        
        # Execute query
        result = execute_query(sql)
        
        if result['success']:
            # Generate natural language answer
            nl_prompt = build_natural_language_answer_prompt(
                natural_query, sql, result
            )
            natural_answer = gemini_client.generate_natural_language_answer(nl_prompt)
            
            response = {
                'sql': sql,
                'explanation': explanation,
                'natural_answer': natural_answer,
                'row_count': result['row_count'],
                'columns': result['columns']
            }
            
            # Optionally include raw data
            if include_raw_data:
                response['results'] = result
            
            return jsonify(response)
        else:
            return jsonify({
                'error': result['error'],
                'sql': sql,
                'explanation': explanation
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/schema', methods=['GET'])
def api_schema():
    '''
    Get database schema
    GET /api/schema
    '''
    try:
        schema = get_schema()
        return jsonify({'schema': schema})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
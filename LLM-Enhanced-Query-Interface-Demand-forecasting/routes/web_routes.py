from flask import Blueprint, render_template, request
from database.schema import get_schema
from llm.gemini_client import GeminiClient
from llm.prompt_builder import (
    build_sql_prompt, 
    build_explanation_prompt,
    build_natural_language_answer_prompt
)
from utils.validator import validate_sql
from utils.executor import execute_query

web_bp = Blueprint('web', __name__)
gemini_client = GeminiClient()

@web_bp.route('/', methods=['GET', 'POST'])
def index():
    schema = get_schema()
    context = {
        'schema': schema,
        'query': None,
        'sql_query': None,
        'explanation': None,
        'natural_answer': None,
        'results': None,
        'error': None
    }
    
    if request.method == 'POST':
        natural_query = request.form.get('query', '').strip()
        context['query'] = natural_query
        
        if natural_query:
            try:
                # Generate SQL using Gemini
                sql_prompt = build_sql_prompt(natural_query, schema)
                sql = gemini_client.generate_sql(sql_prompt)
                
                # Generate explanation
                explanation_prompt = build_explanation_prompt(sql)
                explanation = gemini_client.generate_explanation(explanation_prompt)
                context['explanation'] = explanation
                
                # Validate SQL
                is_valid, error_msg, sql = validate_sql(sql)
                context['sql_query'] = sql
                
                if not is_valid:
                    context['error'] = error_msg
                else:
                    # Execute query
                    result = execute_query(sql)
                    
                    if result['success']:
                        context['results'] = result
                        
                        # Generate natural language answer from results
                        nl_prompt = build_natural_language_answer_prompt(
                            natural_query, sql, result
                        )
                        natural_answer = gemini_client.generate_natural_language_answer(nl_prompt)
                        context['natural_answer'] = natural_answer
                    else:
                        context['error'] = result['error']
                        
            except Exception as e:
                context['error'] = f"Error processing query: {str(e)}"
    
    return render_template('index.html', **context)
import google.generativeai as genai
from config import Config

class GeminiClient:
    def __init__(self):
        '''Initialize Gemini client with API key'''
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def generate_content(self, prompt):
        '''
        Generate content using Gemini
        Args:
            prompt (str): The prompt to send to Gemini
        Returns:
            str: Generated response
        '''
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_sql(self, prompt):
        '''
        Generate SQL query from prompt
        '''
        response = self.generate_content(prompt)
        # Clean up response
        sql = response.replace('```sql', '').replace('```', '').strip()
        sql = sql.replace(';', '').strip()
        return sql
    
    def generate_explanation(self, prompt):
        '''
        Generate explanation from prompt
        '''
        return self.generate_content(prompt)
    
    def generate_natural_language_answer(self, prompt):
        '''
        Generate natural language answer from query results
        '''
        return self.generate_content(prompt)
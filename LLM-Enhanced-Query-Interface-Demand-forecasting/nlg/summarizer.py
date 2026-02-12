from llm.gemini_client import GeminiClient

class NLGSummarizer:
    '''Generate natural language summaries using Gemini'''
    
    def __init__(self):
        self.gemini = GeminiClient()
    
    def generate_forecast_summary(self, forecast_result, inventory_metrics, 
                                  alerts, recommendations):
        '''
        Generate comprehensive natural language summary
        
        Args:
            forecast_result: Forecast results dict
            inventory_metrics: Inventory calculations dict
            alerts: List of alerts
            recommendations: List of recommendations
        
        Returns:
            Natural language summary string
        '''
        prompt = self._build_summary_prompt(
            forecast_result, inventory_metrics, alerts, recommendations
        )
        
        try:
            summary = self.gemini.generate_content(prompt)
            return summary
        except:
            # Fallback to template-based summary
            return self._template_summary(
                forecast_result, inventory_metrics, recommendations
            )
    
    def _build_summary_prompt(self, forecast_result, inventory_metrics, 
                             alerts, recommendations):
        '''Build prompt for Gemini'''
        
        prompt = f"""You are an inventory management assistant. Create a clear, concise summary for a business user.

Item: {forecast_result.get('item_id')}
Store: {forecast_result.get('store_id')}

FORECAST DATA:
- Forecast Horizon: {forecast_result.get('horizon')} days
- Average Daily Demand: {inventory_metrics['avg_daily_demand']:.1f} units
- Total Forecasted Demand: {inventory_metrics['total_forecast']:.1f} units
- Historical Average: {forecast_result['summary']['historical_mean']:.1f} units/day

INVENTORY METRICS:
- Reorder Point: {inventory_metrics['reorder_point']:.0f} units
- Safety Stock: {inventory_metrics['safety_stock']:.0f} units
- Economic Order Quantity: {inventory_metrics['eoq']:.0f} units
- Service Level: {inventory_metrics['service_level']*100:.0f}%

ALERTS:
{self._format_alerts(alerts)}

RECOMMENDATIONS:
{self._format_recommendations(recommendations)}

Instructions:
1. Start with a brief overview of the forecast
2. Explain what the numbers mean in simple business terms
3. Highlight any important alerts or concerns
4. End with clear action items
5. Use a friendly, professional tone
6. Keep it under 200 words

Summary:"""
        
        return prompt
    
    def _format_alerts(self, alerts):
        '''Format alerts for prompt'''
        if not alerts:
            return "No alerts"
        return "\n".join([f"- [{a['urgency']}] {a['message']}" for a in alerts])
    
    def _format_recommendations(self, recommendations):
        '''Format recommendations for prompt'''
        if not recommendations:
            return "No specific recommendations"
        return "\n".join([f"- [{r['priority']}] {r['message']}" for r in recommendations])
    
    def _template_summary(self, forecast_result, inventory_metrics, recommendations):
        '''Fallback template-based summary'''
        item_id = forecast_result.get('item_id', 'Unknown')
        store_id = forecast_result.get('store_id', 'Unknown')
        horizon = forecast_result.get('horizon', 0)
        avg_demand = inventory_metrics['avg_daily_demand']
        total_forecast = inventory_metrics['total_forecast']
        rop = inventory_metrics['reorder_point']
        
        summary = f"""📊 Forecast Summary for {item_id} at {store_id}

Expected to sell approximately {avg_demand:.0f} units per day over the next {horizon} days, 
totaling {total_forecast:.0f} units.

💡 Key Recommendations:
"""
        
        for rec in recommendations[:3]:  # Top 3 recommendations
            summary += f"\n• {rec['message']}"
        
        summary += f"\n\n📌 Reorder when inventory reaches {rop:.0f} units to maintain optimal stock levels."
        
        return summary

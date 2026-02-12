import json
from datetime import datetime

class ChartGenerator:
    '''Generate charts for visualization'''
    
    @staticmethod
    def create_forecast_chart(forecast_data, historical_data=None):
        '''
        Create forecast chart data for Chart.js visualization
        
        Args:
            forecast_data: List of dicts with forecast predictions
            historical_data: Optional list of dicts with historical sales
        
        Returns:
            dict with chart configuration for Chart.js
        '''
        # Extract dates and values from forecast
        forecast_dates = []
        predicted = []
        lower = []
        upper = []
        
        for f in forecast_data:
            # Handle date formatting
            date_val = f.get('date')
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%Y-%m-%d')
            elif isinstance(date_val, str):
                date_str = date_val
            else:
                date_str = str(date_val)
            
            forecast_dates.append(date_str)
            predicted.append(float(f.get('predicted_demand', 0)))
            lower.append(float(f.get('lower_bound', 0)))
            upper.append(float(f.get('upper_bound', 0)))
        
        # Build chart configuration
        chart_data = {
            'type': 'line',
            'labels': [],
            'datasets': []
        }
        
        # Add historical data if available
        if historical_data:
            hist_dates = []
            hist_sales = []
            
            for h in historical_data:
                date_val = h.get('date')
                if hasattr(date_val, 'strftime'):
                    date_str = date_val.strftime('%Y-%m-%d')
                elif isinstance(date_val, str):
                    date_str = date_val
                else:
                    date_str = str(date_val)
                
                hist_dates.append(date_str)
                hist_sales.append(float(h.get('sales', 0)))
            
            chart_data['labels'] = hist_dates + forecast_dates
            
            # Historical sales dataset
            chart_data['datasets'].append({
                'label': 'Historical Sales',
                'data': hist_sales + [None] * len(forecast_dates),  # Pad with None
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.1)',
                'borderWidth': 2,
                'fill': False,
                'pointRadius': 2,
                'pointHoverRadius': 5
            })
        else:
            chart_data['labels'] = forecast_dates
        
        # Predicted demand dataset
        predicted_offset = [None] * (len(historical_data) if historical_data else 0)
        chart_data['datasets'].append({
            'label': 'Predicted Demand',
            'data': predicted_offset + predicted,
            'borderColor': 'rgb(75, 192, 192)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderWidth': 3,
            'fill': False,
            'pointRadius': 3,
            'pointHoverRadius': 6
        })
        
        # Lower bound dataset
        chart_data['datasets'].append({
            'label': 'Lower Bound (95% CI)',
            'data': predicted_offset + lower,
            'borderColor': 'rgba(75, 192, 192, 0.4)',
            'backgroundColor': 'rgba(75, 192, 192, 0.05)',
            'borderWidth': 1,
            'borderDash': [5, 5],
            'fill': False,
            'pointRadius': 0
        })
        
        # Upper bound dataset
        chart_data['datasets'].append({
            'label': 'Upper Bound (95% CI)',
            'data': predicted_offset + upper,
            'borderColor': 'rgba(75, 192, 192, 0.4)',
            'backgroundColor': 'rgba(75, 192, 192, 0.1)',
            'borderWidth': 1,
            'borderDash': [5, 5],
            'fill': '-1',  # Fill to previous dataset (lower bound)
            'pointRadius': 0
        })
        
        return chart_data
    
    @staticmethod
    def create_metrics_chart(inventory_metrics):
        '''
        Create bar chart for inventory metrics
        
        Args:
            inventory_metrics: Dict with inventory calculations
        
        Returns:
            dict with chart configuration for Chart.js
        '''
        chart_data = {
            'type': 'bar',
            'labels': ['Avg Daily Demand', 'Safety Stock', 'Reorder Point', 'EOQ'],
            'datasets': [{
                'label': 'Inventory Metrics (Units)',
                'data': [
                    round(inventory_metrics.get('avg_daily_demand', 0), 2),
                    round(inventory_metrics.get('safety_stock', 0), 2),
                    round(inventory_metrics.get('reorder_point', 0), 2),
                    round(inventory_metrics.get('eoq', 0), 2)
                ],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.7)',   # Blue
                    'rgba(255, 206, 86, 0.7)',   # Yellow
                    'rgba(75, 192, 192, 0.7)',   # Teal
                    'rgba(153, 102, 255, 0.7)'   # Purple
                ],
                'borderColor': [
                    'rgb(54, 162, 235)',
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)'
                ],
                'borderWidth': 2
            }]
        }
        
        return chart_data
    
    @staticmethod
    def create_demand_comparison_chart(historical_mean, forecast_mean):
        '''
        Create comparison chart for historical vs forecasted demand
        
        Args:
            historical_mean: Historical average demand
            forecast_mean: Forecasted average demand
        
        Returns:
            dict with chart configuration for Chart.js
        '''
        chart_data = {
            'type': 'bar',
            'labels': ['Historical Average', 'Forecasted Average'],
            'datasets': [{
                'label': 'Average Daily Demand',
                'data': [
                    round(historical_mean, 2),
                    round(forecast_mean, 2)
                ],
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(75, 192, 192, 0.7)'
                ],
                'borderColor': [
                    'rgb(54, 162, 235)',
                    'rgb(75, 192, 192)'
                ],
                'borderWidth': 2
            }]
        }
        
        return chart_data
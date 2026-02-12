class AlertGenerator:
    '''Generate inventory alerts'''
    
    @staticmethod
    def check_stockout_risk(current_inventory, reorder_point):
        '''Check if inventory is below reorder point'''
        if current_inventory is None:
            return None
        
        if current_inventory <= reorder_point:
            urgency = 'CRITICAL' if current_inventory < reorder_point * 0.5 else 'HIGH'
            return {
                'type': 'STOCKOUT_RISK',
                'urgency': urgency,
                'message': f'Inventory ({current_inventory:.0f} units) is below reorder point ({reorder_point:.0f} units)'
            }
        return None
    
    @staticmethod
    def check_overstock(current_inventory, avg_daily_demand, threshold_days=90):
        '''Check for overstock situation'''
        if current_inventory is None or avg_daily_demand <= 0:
            return None
        
        days_of_stock = current_inventory / avg_daily_demand
        
        if days_of_stock > threshold_days:
            return {
                'type': 'OVERSTOCK',
                'urgency': 'MEDIUM',
                'message': f'Excess inventory: {days_of_stock:.0f} days of stock (threshold: {threshold_days} days)'
            }
        return None
    
    @staticmethod
    def check_demand_surge(forecast_mean, historical_mean, threshold=2.0):
        '''Check for unusual demand surge'''
        if forecast_mean > historical_mean * threshold:
            return {
                'type': 'DEMAND_SURGE',
                'urgency': 'HIGH',
                'message': f'Forecasted demand ({forecast_mean:.0f}) is {forecast_mean/historical_mean:.1f}x higher than historical average'
            }
        return None
    
    @staticmethod
    def generate_all_alerts(inventory_metrics, forecast_summary, current_inventory=None):
        '''Generate all applicable alerts'''
        alerts = []
        
        # Stockout risk
        if current_inventory:
            alert = AlertGenerator.check_stockout_risk(
                current_inventory, inventory_metrics['reorder_point']
            )
            if alert:
                alerts.append(alert)
        
        # Overstock
        if current_inventory:
            alert = AlertGenerator.check_overstock(
                current_inventory, inventory_metrics['avg_daily_demand']
            )
            if alert:
                alerts.append(alert)
        
        # Demand surge
        alert = AlertGenerator.check_demand_surge(
            forecast_summary['forecast_mean'],
            forecast_summary['historical_mean']
        )
        if alert:
            alerts.append(alert)
        
        return alerts
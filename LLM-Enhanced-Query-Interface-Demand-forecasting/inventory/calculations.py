import numpy as np

class InventoryCalculations:
    '''Calculate inventory metrics'''
    
    @staticmethod
    def calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock):
        '''
        Calculate Reorder Point (ROP)
        ROP = (Average Daily Demand × Lead Time) + Safety Stock
        '''
        rop = (avg_daily_demand * lead_time_days) + safety_stock
        return max(0, rop)
    
    @staticmethod
    def calculate_safety_stock(demand_std, lead_time_days, service_level=0.95):
        '''
        Calculate Safety Stock
        Safety Stock = Z-score × σ × √(Lead Time)
        
        Service levels:
        - 90% = Z-score 1.28
        - 95% = Z-score 1.65
        - 99% = Z-score 2.33
        '''
        z_scores = {
            0.90: 1.28,
            0.95: 1.65,
            0.99: 2.33
        }
        
        z_score = z_scores.get(service_level, 1.65)
        safety_stock = z_score * demand_std * np.sqrt(lead_time_days)
        
        return max(0, safety_stock)
    
    @staticmethod
    def calculate_eoq(annual_demand, order_cost, holding_cost_per_unit):
        '''
        Calculate Economic Order Quantity (EOQ)
        EOQ = √(2 × Annual Demand × Order Cost / Holding Cost)
        '''
        if holding_cost_per_unit <= 0:
            return 0
        
        eoq = np.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)
        return max(0, eoq)
    
    @staticmethod
    def calculate_days_of_stock(current_inventory, avg_daily_demand):
        '''
        Calculate days of stock remaining
        '''
        if avg_daily_demand <= 0:
            return float('inf')
        
        return current_inventory / avg_daily_demand
    
    @staticmethod
    def calculate_all_metrics(forecast_data, current_inventory=None, 
                             lead_time_days=7, service_level=0.95,
                             order_cost=50, holding_cost_per_unit=2):
        '''
        Calculate all inventory metrics at once
        
        Args:
            forecast_data: List of dicts with forecast predictions
            current_inventory: Current inventory level
            lead_time_days: Supplier lead time
            service_level: Desired service level (0.90, 0.95, 0.99)
            order_cost: Fixed cost per order
            holding_cost_per_unit: Annual holding cost per unit
        
        Returns:
            dict with all metrics
        '''
        # Extract predicted demands
        demands = [f['predicted_demand'] for f in forecast_data]
        
        # Calculate statistics
        avg_daily_demand = np.mean(demands)
        demand_std = np.std(demands)
        total_forecast = np.sum(demands)
        
        # Calculate metrics
        safety_stock = InventoryCalculations.calculate_safety_stock(
            demand_std, lead_time_days, service_level
        )
        
        reorder_point = InventoryCalculations.calculate_reorder_point(
            avg_daily_demand, lead_time_days, safety_stock
        )
        
        annual_demand = avg_daily_demand * 365
        eoq = InventoryCalculations.calculate_eoq(
            annual_demand, order_cost, holding_cost_per_unit
        )
        
        days_of_stock = None
        if current_inventory is not None:
            days_of_stock = InventoryCalculations.calculate_days_of_stock(
                current_inventory, avg_daily_demand
            )
        
        return {
            'avg_daily_demand': round(avg_daily_demand, 2),
            'demand_std': round(demand_std, 2),
            'total_forecast': round(total_forecast, 2),
            'safety_stock': round(safety_stock, 2),
            'reorder_point': round(reorder_point, 2),
            'eoq': round(eoq, 2),
            'days_of_stock': round(days_of_stock, 2) if days_of_stock else None,
            'service_level': service_level,
            'lead_time_days': lead_time_days
        }
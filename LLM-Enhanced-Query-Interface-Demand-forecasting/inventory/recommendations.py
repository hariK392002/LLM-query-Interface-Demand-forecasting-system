class RecommendationEngine:
    '''Generate actionable recommendations'''
    
    @staticmethod
    def generate_recommendations(inventory_metrics, alerts, current_inventory=None):
        '''
        Generate inventory recommendations based on metrics and alerts
        
        Returns:
            List of recommendation dicts
        '''
        recommendations = []
        
        rop = inventory_metrics['reorder_point']
        safety_stock = inventory_metrics['safety_stock']
        eoq = inventory_metrics['eoq']
        
        # Check if we need to reorder
        if current_inventory is not None:
            if current_inventory <= rop:
                order_qty = max(eoq, rop - current_inventory + safety_stock)
                recommendations.append({
                    'priority': 'HIGH',
                    'action': 'PLACE_ORDER',
                    'message': f'Place order for {order_qty:.0f} units immediately',
                    'details': f'Current inventory ({current_inventory:.0f}) is at or below reorder point ({rop:.0f})'
                })
            elif current_inventory <= rop * 1.2:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'action': 'MONITOR',
                    'message': f'Monitor inventory closely - approaching reorder point',
                    'details': f'Reorder when inventory reaches {rop:.0f} units'
                })
            else:
                days_of_stock = inventory_metrics.get('days_of_stock')
                recommendations.append({
                    'priority': 'LOW',
                    'action': 'OK',
                    'message': f'Inventory levels are healthy',
                    'details': f'Current stock will last approximately {days_of_stock:.0f} days'
                })
        else:
            recommendations.append({
                'priority': 'INFO',
                'action': 'SET_REORDER_POINT',
                'message': f'Set reorder point to {rop:.0f} units',
                'details': f'Maintain safety stock of {safety_stock:.0f} units'
            })
        
        # Add alert-based recommendations
        for alert in alerts:
            if alert['type'] == 'OVERSTOCK':
                recommendations.append({
                    'priority': 'MEDIUM',
                    'action': 'REDUCE_STOCK',
                    'message': 'Consider promotion or discount to clear excess inventory',
                    'details': alert['message']
                })
            elif alert['type'] == 'DEMAND_SURGE':
                recommendations.append({
                    'priority': 'HIGH',
                    'action': 'INCREASE_STOCK',
                    'message': 'Prepare for demand surge - consider additional safety stock',
                    'details': alert['message']
                })
        
        return recommendations
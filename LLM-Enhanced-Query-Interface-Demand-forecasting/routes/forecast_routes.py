from flask import Blueprint, render_template, request, jsonify
from forecasting.forecaster import Forecaster
from inventory.calculations import InventoryCalculations
from inventory.alerts import AlertGenerator
from inventory.recommendations import RecommendationEngine
from nlg.summarizer import NLGSummarizer
from visualization.charts import ChartGenerator
from database.connection import get_db_connection
import traceback

forecast_bp = Blueprint('forecast', __name__, url_prefix='/forecast')

@forecast_bp.route('/', methods=['GET', 'POST'])
def forecast_page():
    '''Forecast web interface'''
    context = {
        'forecast_result': None,
        'inventory_metrics': None,
        'alerts': None,
        'recommendations': None,
        'summary': None,
        'chart_data': None,
        'metrics_chart': None,
        'comparison_chart': None,
        'error': None,
        'item_id': '',
        'store_id': '',
        'horizon': 28,
        'current_inventory': ''
    }
    
    if request.method == 'POST':
        item_id = request.form.get('item_id', '').strip()
        store_id = request.form.get('store_id', '').strip()
        horizon = int(request.form.get('horizon', 28))
        current_inventory = request.form.get('current_inventory', '').strip()
        
        # Store form values for re-display
        context['item_id'] = item_id
        context['store_id'] = store_id
        context['horizon'] = horizon
        context['current_inventory'] = current_inventory
        
        # Convert current_inventory to float if provided
        current_inv = None
        if current_inventory:
            try:
                current_inv = float(current_inventory)
            except ValueError:
                context['error'] = "Invalid current inventory value. Please enter a number."
                return render_template('forecast.html', **context)
        
        if not item_id or not store_id:
            context['error'] = "Item ID and Store ID are required"
            return render_template('forecast.html', **context)
        
        try:
            # Generate forecast
            print(f"Generating forecast for item: {item_id}, store: {store_id}, horizon: {horizon}")
            forecaster = Forecaster(model_name='prophet')
            forecast_result = forecaster.generate_forecast(item_id, store_id, horizon)
            
            if not forecast_result['success']:
                context['error'] = forecast_result.get('error', 'Forecast generation failed')
                return render_template('forecast.html', **context)
            
            context['forecast_result'] = forecast_result
            print(f"Forecast generated successfully: {len(forecast_result['forecast'])} predictions")
            
            # Calculate inventory metrics
            inventory_metrics = InventoryCalculations.calculate_all_metrics(
                forecast_result['forecast'],
                current_inventory=current_inv,
                lead_time_days=7,
                service_level=0.95
            )
            context['inventory_metrics'] = inventory_metrics
            print(f"Inventory metrics calculated: ROP={inventory_metrics['reorder_point']}")
            
            # Generate alerts
            alerts = AlertGenerator.generate_all_alerts(
                inventory_metrics,
                forecast_result['summary'],
                current_inventory=current_inv
            )
            context['alerts'] = alerts
            print(f"Generated {len(alerts)} alerts")
            
            # Generate recommendations
            recommendations = RecommendationEngine.generate_recommendations(
                inventory_metrics,
                alerts,
                current_inventory=current_inv
            )
            context['recommendations'] = recommendations
            print(f"Generated {len(recommendations)} recommendations")
            
            # Generate NLG summary
            try:
                nlg = NLGSummarizer()
                summary = nlg.generate_forecast_summary(
                    forecast_result,
                    inventory_metrics,
                    alerts,
                    recommendations
                )
                context['summary'] = summary
                print("NLG summary generated successfully")
            except Exception as e:
                print(f"NLG summary generation failed: {e}")
                context['summary'] = f"⚠️ AI summary unavailable. Using basic summary.\n\n"
                context['summary'] += f"Expected to sell {inventory_metrics['avg_daily_demand']:.1f} units/day "
                context['summary'] += f"over the next {horizon} days (total: {inventory_metrics['total_forecast']:.0f} units). "
                context['summary'] += f"Reorder when inventory reaches {inventory_metrics['reorder_point']:.0f} units."
            
            # Generate chart data
            try:
                chart_gen = ChartGenerator()
                
                # Main forecast chart
                chart_data = chart_gen.create_forecast_chart(
                    forecast_result['forecast'],
                    forecast_result.get('historical_data')
                )
                context['chart_data'] = chart_data
                
                # Metrics chart
                metrics_chart = chart_gen.create_metrics_chart(inventory_metrics)
                context['metrics_chart'] = metrics_chart
                
                # Comparison chart
                comparison_chart = chart_gen.create_demand_comparison_chart(
                    forecast_result['summary']['historical_mean'],
                    forecast_result['summary']['forecast_mean']
                )
                context['comparison_chart'] = comparison_chart
                
                print("Charts generated successfully")
            except Exception as e:
                print(f"Chart generation failed: {e}")
                traceback.print_exc()
            
        except Exception as e:
            context['error'] = f"Error: {str(e)}"
            print(f"Forecast error: {e}")
            traceback.print_exc()
    
    return render_template('forecast.html', **context)


@forecast_bp.route('/api/generate', methods=['POST'])
def api_generate_forecast():
    '''
    API endpoint for forecast generation
    
    POST /forecast/api/generate
    Body: {
        "item_id": "FOODS_3_090",
        "store_id": "CA_1",
        "horizon": 28,
        "current_inventory": 150,
        "lead_time_days": 7,
        "service_level": 0.95
    }
    '''
    try:
        data = request.get_json()
        
        item_id = data.get('item_id')
        store_id = data.get('store_id')
        horizon = data.get('horizon', 28)
        current_inventory = data.get('current_inventory')
        lead_time_days = data.get('lead_time_days', 7)
        service_level = data.get('service_level', 0.95)
        
        if not item_id or not store_id:
            return jsonify({'error': 'item_id and store_id are required'}), 400
        
        # Generate forecast
        forecaster = Forecaster(model_name='prophet')
        forecast_result = forecaster.generate_forecast(item_id, store_id, horizon)
        
        if not forecast_result['success']:
            return jsonify(forecast_result), 400
        
        # Calculate inventory metrics
        inventory_metrics = InventoryCalculations.calculate_all_metrics(
            forecast_result['forecast'],
            current_inventory=current_inventory,
            lead_time_days=lead_time_days,
            service_level=service_level
        )
        
        # Generate alerts
        alerts = AlertGenerator.generate_all_alerts(
            inventory_metrics,
            forecast_result['summary'],
            current_inventory=current_inventory
        )
        
        # Generate recommendations
        recommendations = RecommendationEngine.generate_recommendations(
            inventory_metrics,
            alerts,
            current_inventory=current_inventory
        )
        
        # Generate NLG summary
        try:
            nlg = NLGSummarizer()
            summary = nlg.generate_forecast_summary(
                forecast_result,
                inventory_metrics,
                alerts,
                recommendations
            )
        except Exception as e:
            summary = f"Forecast generated. Expected demand: {inventory_metrics['avg_daily_demand']:.1f} units/day"
        
        return jsonify({
            'success': True,
            'forecast': forecast_result,
            'inventory_metrics': inventory_metrics,
            'alerts': alerts,
            'recommendations': recommendations,
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@forecast_bp.route('/api/items', methods=['GET'])
def api_list_items():
    '''
    Get list of available items and stores
    
    GET /forecast/api/items
    Query params: limit (default: 100)
    '''
    try:
        limit = request.args.get('limit', 100, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try to get distinct item-store combinations
        try:
            cursor.execute("""
                SELECT DISTINCT item_id, store_id 
                FROM sales_train 
                LIMIT ?
            """, (limit,))
        except:
            # Fallback if column names are different
            cursor.execute("""
                SELECT DISTINCT * 
                FROM sales_train 
                LIMIT ?
            """, (limit,))
        
        items = []
        for row in cursor.fetchall():
            items.append({
                'item_id': row[0] if len(row) > 0 else None,
                'store_id': row[1] if len(row) > 1 else None
            })
        
        return jsonify({
            'success': True,
            'count': len(items),
            'items': items
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@forecast_bp.route('/api/batch', methods=['POST'])
def api_batch_forecast():
    '''
    Generate forecasts for multiple items in batch
    
    POST /forecast/api/batch
    Body: {
        "items": [
            {"item_id": "ITEM1", "store_id": "STORE1"},
            {"item_id": "ITEM2", "store_id": "STORE2"}
        ],
        "horizon": 28
    }
    '''
    try:
        data = request.get_json()
        items = data.get('items', [])
        horizon = data.get('horizon', 28)
        
        if not items:
            return jsonify({'error': 'items list is required'}), 400
        
        forecaster = Forecaster(model_name='prophet')
        results = []
        
        for item in items:
            item_id = item.get('item_id')
            store_id = item.get('store_id')
            
            if not item_id or not store_id:
                results.append({
                    'item_id': item_id,
                    'store_id': store_id,
                    'success': False,
                    'error': 'Missing item_id or store_id'
                })
                continue
            
            try:
                forecast_result = forecaster.generate_forecast(item_id, store_id, horizon)
                
                if forecast_result['success']:
                    # Calculate basic metrics
                    inventory_metrics = InventoryCalculations.calculate_all_metrics(
                        forecast_result['forecast'],
                        current_inventory=None,
                        lead_time_days=7,
                        service_level=0.95
                    )
                    
                    results.append({
                        'item_id': item_id,
                        'store_id': store_id,
                        'success': True,
                        'avg_daily_demand': inventory_metrics['avg_daily_demand'],
                        'total_forecast': inventory_metrics['total_forecast'],
                        'reorder_point': inventory_metrics['reorder_point'],
                        'safety_stock': inventory_metrics['safety_stock']
                    })
                else:
                    results.append({
                        'item_id': item_id,
                        'store_id': store_id,
                        'success': False,
                        'error': forecast_result.get('error')
                    })
                    
            except Exception as e:
                results.append({
                    'item_id': item_id,
                    'store_id': store_id,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'total': len(items),
            'successful': sum(1 for r in results if r.get('success')),
            'failed': sum(1 for r in results if not r.get('success')),
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@forecast_bp.route('/test', methods=['GET'])
def test_forecast():
    '''Test endpoint to verify forecast system is working'''
    return jsonify({
        'status': 'ok',
        'message': 'Forecast system is running',
        'endpoints': {
            'web_interface': '/forecast/',
            'api_generate': '/forecast/api/generate',
            'api_items': '/forecast/api/items',
            'api_batch': '/forecast/api/batch'
        }
    })

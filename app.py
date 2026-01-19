"""
AI Sales Agent - Flask Web Application
Daily Sales Monitoring Dashboard
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from agent_engine import SalesAgentEngine
import os
from datetime import datetime
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'csv'}

# Initialize agent engine
DATA_PATH = os.path.join('data', 'daily_sales.csv')
agent = SalesAgentEngine(DATA_PATH)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Redirect to overview dashboard"""
    return overview()


@app.route('/overview')
def overview():
    """Overview Dashboard - Main metrics and status"""
    try:
        # Run analysis
        summary = agent.run_analysis()
        
        # Format currency for display
        summary['total_sales_formatted'] = f"Rp {summary['total_sales']:,.0f}"
        summary['total_target_formatted'] = f"Rp {summary['total_target']:,.0f}"
        
        # Calculate gap
        gap = summary['total_sales'] - summary['total_target']
        summary['gap_formatted'] = f"Rp {abs(gap):,.0f}"
        summary['gap_direction'] = 'above' if gap >= 0 else 'below'
        
        # Status styling
        status_classes = {
            'OK': 'success',
            'WARNING': 'warning',
            'CRITICAL': 'danger'
        }
        summary['status_class'] = status_classes.get(summary['overall_status'], 'secondary')
        
        # Get top performer for quick display
        if summary['top_performers']:
            top = summary['top_performers'][0]
            summary['top_performer_text'] = f"{top['region']} - {top['product']}"
        else:
            summary['top_performer_text'] = "N/A"
        
        return render_template('overview.html', data=summary)
    
    except Exception as e:
        print(f"Error in overview: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/insight')
def insight():
    """AI Daily Insight - Generated sales brief"""
    try:
        # Run analysis
        summary = agent.run_analysis()
        
        # Parse AI insight into sections for better display
        ai_text = summary.get('ai_insight', '')
        
        # Split into sections (basic parsing)
        sections = {
            'full_text': ai_text,
            'date': summary['date'],
            'day_name': summary['day_name'],
            'status': summary['overall_status']
        }
        
        # Status styling
        status_classes = {
            'OK': 'success',
            'WARNING': 'warning',
            'CRITICAL': 'danger'
        }
        sections['status_class'] = status_classes.get(summary['overall_status'], 'secondary')
        
        return render_template('insight.html', data=sections, summary=summary)
    
    except Exception as e:
        print(f"Error in insight: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/alerts')
def alerts():
    """Alerts & Issues - Flagged items list"""
    try:
        # Run analysis
        summary = agent.run_analysis()
        
        # Combine critical and warning issues
        all_alerts = []
        
        # Add critical issues
        for item in summary.get('critical_issues', []):
            item['severity'] = 'CRITICAL'
            item['severity_class'] = 'danger'
            item['icon'] = '🚨'
            all_alerts.append(item)
        
        # Add warning issues
        for item in summary.get('warning_issues', []):
            item['severity'] = 'WARNING'
            item['severity_class'] = 'warning'
            item['icon'] = '⚠️'
            all_alerts.append(item)
        
        # Format currency for each alert
        for alert in all_alerts:
            alert['total_sales_formatted'] = f"Rp {alert.get('total_sales', 0):,.0f}"
            alert['target_daily_formatted'] = f"Rp {alert.get('target_daily', 0):,.0f}"
            
            # Get primary issue message
            violations = alert.get('violations', [])
            if violations:
                alert['issue_description'] = violations[0].get('message', 'Performance issue detected')
            else:
                alert['issue_description'] = 'Performance below expectations'
        
        data = {
            'alerts': all_alerts,
            'critical_count': summary['critical_count'],
            'warning_count': summary['warning_count'],
            'total_count': len(all_alerts),
            'date': summary['date'],
            'overall_status': summary['overall_status']
        }
        
        return render_template('alerts.html', data=data)
    
    except Exception as e:
        print(f"Error in alerts: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/workflow')
def workflow():
    """AI Agent Workflow - How it works explanation"""
    
    # Static content explaining the agent workflow
    workflow_data = {
        'title': 'How the AI Sales Agent Works',
        'description': 'An autonomous system that monitors daily sales performance, detects issues, and generates actionable insights.',
        'steps': [
            {
                'number': 1,
                'icon': '📊',
                'title': 'Data Ingestion',
                'description': 'Reads daily sales data from CSV files containing sales, targets, and historical trends for each region-product combination.'
            },
            {
                'number': 2,
                'icon': '🔍',
                'title': 'Rule Evaluation',
                'description': 'Applies 4 rule categories: Target Achievement, Day-over-Day Performance, Trend Anomaly, and Weekend Adjustment to classify each item as OK, WARNING, or CRITICAL.'
            },
            {
                'number': 3,
                'icon': '🤖',
                'title': 'AI Analysis',
                'description': 'Generates natural language insights using structured data and business context. Explains what happened, why it matters, and what to do about it.'
            },
            {
                'number': 4,
                'icon': '📢',
                'title': 'Alert Delivery',
                'description': 'Delivers insights through this dashboard, with potential for email, Slack, or mobile notifications in production.'
            }
        ],
        'rules': [
            {
                'category': 'R1: Target Achievement',
                'ok': 'Met or exceeded target (≥0%)',
                'warning': 'Slightly below target (0% to -10%)',
                'critical': 'Significantly missed target (<-10%)'
            },
            {
                'category': 'R2: Day-over-Day',
                'ok': 'Stable or growing (≥-5%)',
                'warning': 'Moderate decline (-5% to -15%)',
                'critical': 'Sharp drop (<-15%)'
            },
            {
                'category': 'R3: Trend Anomaly',
                'ok': 'Within normal range (≥85% of 7-day avg)',
                'warning': 'Below trend (70-85% of 7-day avg)',
                'critical': 'Severe deviation (<70% of 7-day avg)'
            },
            {
                'category': 'R4: Weekend Adjustment',
                'ok': 'N/A',
                'warning': 'Downgrades CRITICAL to WARNING on weekends',
                'critical': 'Prevents false alarms during low-traffic days'
            }
        ],
        'tech_stack': [
            {'name': 'Python', 'purpose': 'Backend logic and data processing'},
            {'name': 'Flask', 'purpose': 'Web framework for routing and templates'},
            {'name': 'Pandas', 'purpose': 'Data manipulation and analysis'},
            {'name': 'Bootstrap', 'purpose': 'Responsive UI components'},
            {'name': 'LLM (Optional)', 'purpose': 'Advanced natural language insights'}
        ]
    }
    
    return render_template('workflow.html', data=workflow_data)


@app.route('/import', methods=['GET', 'POST'])
def import_data():
    """Import Data - Upload new CSV file"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(request.url)
        
        # Check if file is allowed
        if file and allowed_file(file.filename):
            try:
                # Backup existing file
                backup_path = os.path.join(app.config['UPLOAD_FOLDER'], 'daily_sales_backup.csv')
                if os.path.exists(DATA_PATH):
                    shutil.copy2(DATA_PATH, backup_path)
                
                # Save new file
                filename = secure_filename('daily_sales.csv')
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Reload agent with new data
                global agent
                agent = SalesAgentEngine(DATA_PATH)
                
                # Test if data can be loaded
                test_summary = agent.run_analysis()
                
                flash(f'File berhasil diupload! Data dari {test_summary["date"]} telah dimuat.', 'success')
                return redirect(url_for('overview'))
                
            except Exception as e:
                # Restore backup if error occurs
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, DATA_PATH)
                
                flash(f'Error: {str(e)}. File harus berformat CSV yang valid.', 'danger')
                return redirect(request.url)
        else:
            flash('File harus berformat .csv', 'danger')
            return redirect(request.url)
    
    # GET request - show upload form
    try:
        # Get current data info
        summary = agent.run_analysis()
        current_data = {
            'date': summary['date'],
            'total_rows': summary['total_rows'],
            'regions': len(set([item['region'] for item in summary.get('flagged_items', [])])) if summary.get('flagged_items') else 0
        }
    except:
        current_data = {
            'date': 'N/A',
            'total_rows': 0,
            'regions': 0
        }
    
    return render_template('import.html', current_data=current_data)


@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics (for potential AJAX updates)"""
    try:
        summary = agent.run_analysis()
        
        # Return JSON for API consumption
        return jsonify({
            'status': 'success',
            'data': {
                'date': summary['date'],
                'overall_status': summary['overall_status'],
                'total_sales': summary['total_sales'],
                'total_target': summary['total_target'],
                'achievement': summary['portfolio_achievement'],
                'critical_count': summary['critical_count'],
                'warning_count': summary['warning_count'],
                'ok_count': summary['ok_count']
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('error.html', error='Internal server error'), 500


# Template filters for formatting
@app.template_filter('currency')
def currency_filter(value):
    """Format number as Indonesian Rupiah"""
    try:
        return f"Rp {float(value):,.0f}"
    except:
        return "Rp 0"


@app.template_filter('percentage')
def percentage_filter(value):
    """Format number as percentage"""
    try:
        return f"{float(value):.1f}%"
    except:
        return "0.0%"


@app.template_filter('signed_percentage')
def signed_percentage_filter(value):
    """Format number as signed percentage"""
    try:
        val = float(value)
        return f"{val:+.1f}%"
    except:
        return "0.0%"


if __name__ == '__main__':
    print("🤖 Starting AI Sales Agent Dashboard...")
    print("📊 Access the dashboard at: http://localhost:5000")
    print("\nPages available:")
    print("  - Overview Dashboard: http://localhost:5000/overview")
    print("  - AI Daily Insight: http://localhost:5000/insight")
    print("  - Alerts & Issues: http://localhost:5000/alerts")
    print("  - Agent Workflow: http://localhost:5000/workflow")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

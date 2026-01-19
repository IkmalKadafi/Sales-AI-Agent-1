# AI Sales Agent - Daily Sales Monitoring Dashboard

![Status](https://img.shields.io/badge/status-demo-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/flask-3.0.0-lightgrey)

An autonomous AI agent that monitors daily sales performance, detects issues, and generates actionable insights. Built as a proof-of-concept for portfolio demonstration.

## 🎯 Overview

This web application demonstrates an intelligent sales monitoring system that:
- **Automatically evaluates** daily sales performance across regions and products
- **Detects anomalies** using rule-based logic (target achievement, day-over-day trends, historical patterns)
- **Generates AI insights** in natural language for executive consumption
- **Classifies issues** by severity (OK, WARNING, CRITICAL)
- **Provides actionable recommendations** for sales teams

## 🚀 Features

### 1. Overview Dashboard
- Real-time sales metrics and KPIs
- Overall status indicator (OK/WARNING/CRITICAL)
- Quick summary of critical issues and warnings
- Top performer highlights

### 2. AI Daily Insight
- AI-generated executive sales brief
- Natural language analysis of performance
- Root cause hypotheses
- Recommended actions for today

### 3. Alerts & Issues
- Detailed list of flagged region-product combinations
- Severity badges and metrics
- Issue descriptions and recommendations

### 4. Agent Workflow
- Visual explanation of how the AI agent works
- Rule-based evaluation logic
- Technology stack overview
- Data flow diagram

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🛠️ Installation

1. **Clone or navigate to the project directory**
```bash
cd "d:\Kadafi workspace\Entropiata Agency\Sales-AI-Agent-1"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 📊 Data Setup

The application expects a CSV file at `data/daily_sales.csv` with the following columns:

- `date` - Transaction date (YYYY-MM-DD)
- `region` - City or branch name
- `product` - Product line/category
- `total_sales` - Total sales revenue
- `target_daily` - Daily sales target
- `sales_yesterday` - Previous day's sales
- `avg_7d_sales` - 7-day rolling average
- `delta_vs_yesterday` - % change from yesterday
- `delta_vs_target` - % difference from target
- `day_name` - Day of week
- `is_weekend` - Boolean (True/False)

A sample dataset is included in `data/daily_sales.csv`.

## 🎮 Usage

### Start the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Access the Dashboard

Open your browser and navigate to:
- **Overview Dashboard**: http://localhost:5000/overview
- **AI Daily Insight**: http://localhost:5000/insight
- **Alerts & Issues**: http://localhost:5000/alerts
- **Agent Workflow**: http://localhost:5000/workflow

## 🏗️ Project Structure

```
Sales-AI-Agent-1/
├── app.py                      # Flask application (routing, API)
├── agent_engine.py             # Rule-based evaluation engine
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── data/
│   └── daily_sales.csv        # Daily sales data
│
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── overview.html          # Dashboard overview
│   ├── insight.html           # AI-generated insights
│   ├── alerts.html            # Flagged issues list
│   ├── workflow.html          # How it works page
│   └── error.html             # Error page
│
└── static/
    └── css/
        └── style.css          # Custom styling
```

## 🤖 How It Works

### Agent Workflow

1. **Data Ingestion**: Reads `daily_sales.csv` and filters to most recent date
2. **Rule Evaluation**: Applies 4 rule categories to each region-product:
   - R1: Target Achievement
   - R2: Day-over-Day Performance
   - R3: Trend Anomaly (vs 7-day average)
   - R4: Weekend Adjustment
3. **AI Analysis**: Generates natural language insights based on findings
4. **Alert Delivery**: Displays results in web dashboard

### Rule Logic

| Rule | OK | WARNING | CRITICAL |
|------|-------|---------|----------|
| **R1: Target** | ≥0% | 0% to -10% | <-10% |
| **R2: Day-over-Day** | ≥-5% | -5% to -15% | <-15% |
| **R3: Trend** | ≥85% of 7-day avg | 70-85% of 7-day avg | <70% of 7-day avg |
| **R4: Weekend** | N/A | Downgrades CRITICAL to WARNING | Prevents false alarms |

## 🎨 Technology Stack

- **Backend**: Flask (Python)
- **Data Processing**: Pandas, NumPy
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Visualization**: Chart.js (ready for integration)
- **AI Insights**: Template-based generation (can be upgraded to LLM API)

## 📈 Future Enhancements

### Phase 1 (POC) - ✅ Complete
- Rule-based evaluation
- Template-based AI insights
- Web dashboard

### Phase 2 (Potential Extensions)
- Real LLM integration (OpenAI GPT-4, Anthropic Claude)
- Historical trend visualization (30-day charts)
- Email/Slack alert delivery
- Custom threshold configuration

### Phase 3 (Production Features)
- Database integration (PostgreSQL)
- User authentication and roles
- Multi-tenant support
- Real-time data streaming
- Mobile app

## 🧪 Testing

To test with different scenarios, modify `data/daily_sales.csv`:

- **All OK**: Set all `delta_vs_target` > 0
- **Warnings**: Set some `delta_vs_target` between -10 and 0
- **Critical**: Set some `delta_vs_target` < -10

Restart the Flask app to see changes.

## 📝 API Endpoints

- `GET /` - Redirects to overview
- `GET /overview` - Dashboard overview page
- `GET /insight` - AI daily insight page
- `GET /alerts` - Alerts and issues page
- `GET /workflow` - Agent workflow explanation
- `GET /api/metrics` - JSON API for metrics (for AJAX)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py (last line):
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Data File Not Found
- Ensure `data/daily_sales.csv` exists
- Check file path in `agent_engine.py` (line 13)

### Template Not Found
- Verify `templates/` folder exists
- Check Flask is finding the correct directory

## 📄 License

This is a proof-of-concept project for portfolio demonstration.

## 👤 Author

**Ikmal Kadafi**
- Portfolio: Entropiata Agency
- Project: Sales AI Agent Demo

## 🙏 Acknowledgments

- Dataset inspired by retail sales analysis use cases
- Built with Flask and Bootstrap
- AI agent design based on modern MLOps practices

---

**Note**: This is a demo/POC application. For production use, implement proper security, authentication, database integration, and error handling.
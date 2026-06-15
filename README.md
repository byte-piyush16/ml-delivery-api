# ML Delivery API

FastAPI backend for real‑time delivery delay prediction, sentiment analysis, and demand forecasting.

## 🚀 Live API
- Base URL: `https://your-backend.onrender.com`
- Swagger Docs: `https://your-backend.onrender.com/docs`

## 🛠️ Tech Stack
- FastAPI
- Databricks Model Serving
- SQL Warehouse (for demand forecast)

## 📦 Setup

1. Clone repo
2. `pip install -r requirements.txt`
3. Create `.env` file (see `.env.example`)
4. `uvicorn main:app --reload`

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict-delay` | Delivery delay probability |
| POST | `/analyze-sentiment` | Aspect‑based sentiment |
| GET  | `/forecast` | Next 7 days demand forecast |

## 🧪 Example Request (cURL)

```bash
curl -X POST "http://localhost:8000/predict-delay" -H "Content-Type: application/json" -d '{"platform_name":"blinkit","order_value_inr":450,"delivery_time_min":25,"customer_delay_rate":0.24}'

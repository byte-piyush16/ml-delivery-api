# ML Delivery API

A production-ready FastAPI backend that serves machine learning models for:
- **Delivery delay prediction** (real-time)
- **Aspect‑based sentiment analysis** (zero-shot NLP)
- **Demand forecasting** (next 7 days)

The API is deployed live on Render. All endpoints accept JSON requests and return predictions (cold start may take 30–60 seconds due to free tier).

## 🚀 Live API

Base URL: **`https://ml-delivery-api-1.onrender.com`**

Interactive API documentation (Swagger UI):  
👉 [`https://ml-delivery-api-1.onrender.com/docs`](https://ml-delivery-api-1.onrender.com/docs)

## 📦 Tech Stack

- **FastAPI** – REST API framework  
- **Uvicorn** – ASGI server  
- **Databricks Model Serving** – delivery delay & sentiment endpoints  
- **Databricks SQL Warehouse** – demand forecast (Delta table query)  
- **Render** – free‑tier deployment  

## 🔌 API Endpoints

### 1. Health Check
http
GET /health

Response:

json
{"status": "ok"}
2. Delivery Delay Prediction
http
POST /predict-delay
Content-Type: application/json
Request body:

json
{
  "platform_name": "blinkit",
  "order_value_inr": 450,
  "delivery_time_min": 25,
  "customer_delay_rate": 0.24
}
Response:

json
{
  "delay_probability": 0.82,
  "predicted_delay": 1,
  "status": "Delayed"
}
3. Sentiment Analysis (Aspect‑Based)
http
POST /analyze-sentiment
Content-Type: application/json
Request body:

json
{
  "text": "Delivery was very slow, but product quality is great."
}
Response:

json
{
  "aspect_sentiments": {
    "delivery": "negative",
    "product quality": "positive"
  }
}
4. Demand Forecast (Next 7 days)
http
GET /forecast
Response:

json
[
  {"forecast_date": "2025-06-15", "predicted_units": 26500},
  {"forecast_date": "2025-06-16", "predicted_units": 26800}
]
🧪 Testing the API (cURL)
bash
# Delivery delay
curl -X POST "https://ml-delivery-api-1.onrender.com/predict-delay" \
     -H "Content-Type: application/json" \
     -d '{"platform_name":"blinkit","order_value_inr":450,"delivery_time_min":25,"customer_delay_rate":0.24}'

# Sentiment analysis
curl -X POST "https://ml-delivery-api-1.onrender.com/analyze-sentiment" \
     -H "Content-Type: application/json" \
     -d '{"text":"Delivery was late"}'

# Demand forecast
curl -X GET "https://ml-delivery-api-1.onrender.com/forecast"
📁 Project Structure
text
ml-delivery-api/
├── main.py                  # FastAPI application
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── runtime.txt              # Python version (3.12.10)
├── render.yaml              # (optional) Render config
└── README.md
🛠️ Local Development
Clone the repository:

bash
git clone https://github.com/byte-piyush16/ml-delivery-api.git
cd ml-delivery-api
Create a virtual environment and install dependencies:

bash
python -m venv venv
source venv/bin/activate   # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
Set environment variables (copy .env.example to .env and fill in your Databricks credentials).

Run the server:

bash
uvicorn main:app --reload --port 8000
Open Swagger UI at http://localhost:8000/docs.

☁️ Deployment (Render)
The service is automatically deployed from the main branch.
Build command: pip install -r requirements.txt
Start command: uvicorn main:app --host 0.0.0.0 --port $PORT

Environment variables required on Render:

DATABRICKS_HOST

DATABRICKS_TOKEN

DATABRICKS_SERVER_HOSTNAME

DATABRICKS_HTTP_PATH

Note: The free tier on Render may cause a cold start (30–60 seconds) after 15 minutes of inactivity. The API timeout is set to 90 seconds to handle this.

👨‍💻 Author
Piyush Madhukar – GitHub




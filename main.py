# ---------------------------------------------------------
# 1. Imports – Required libraries load karna
# ---------------------------------------------------------
import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
from dotenv import load_dotenv

# .env file se environment variables load karna (local testing ke liye)
load_dotenv()

# ---------------------------------------------------------
# 2. FastAPI app create karna
# ---------------------------------------------------------
app = FastAPI(
    title="ML Models API",
    description="APIs for Delivery Delay Prediction and Sentiment Analysis",
    version="1.0.0"
)

# ---------------------------------------------------------
# 3. Databricks configuration (environment variables se lo)
# ---------------------------------------------------------
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")      # e.g., "https://dbc-7eee2e54-d86b.cloud.databricks.com"
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")    # Personal Access Token

# Agar token missing hai to error throw karo
if not DATABRICKS_TOKEN:
    raise ValueError("DATABRICKS_TOKEN environment variable not set")

# Endpoint URLs (jo Databricks Serving mein banaye the)
DELIVERY_URL = f"{DATABRICKS_HOST}/serving-endpoints/delivery-delay-endpoint/invocations"
SENTIMENT_URL = f"{DATABRICKS_HOST}/serving-endpoints/sentiment-analysis-endpoint/invocations"

# ---------------------------------------------------------
# 4. Delivery Delay – Request aur Response Models
# ---------------------------------------------------------
class DeliveryRequest(BaseModel):
    """User se kya input lena hai (frontend se). Baaki features default value daal denge."""
    platform_name: str
    order_value_inr: float
    delivery_time_min: int
    customer_delay_rate: float = 0.24   # default value

class DeliveryResponse(BaseModel):
    """Backend se frontend ko kya response bhejna hai."""
    delay_probability: float
    predicted_delay: int          # 0 ya 1
    status: str                   # "Delayed" ya "On Time"

# ---------------------------------------------------------
# 5. Delivery Delay Prediction Endpoint
# ---------------------------------------------------------
@app.post("/predict-delay", response_model=DeliveryResponse)
async def predict_delay(order: DeliveryRequest):
    # Payload exactly match karo jo Databricks endpoint expect karta hai
    payload = {
        "dataframe_records": [{
            "order_datetime": "17-05-2025 19:30",
            "platform_name": order.platform_name,
            "product_category_name": "grocery",
            "order_value_inr": order.order_value_inr,
            "delivery_time_min": order.delivery_time_min,
            "service_rating": 4,
            "sla_delay": "No",
            "refund_flag": 0,
            "Segment": "Loyalist",
            "customer_delay_rate": order.customer_delay_rate,
            "customer_avg_rating": 4.2,
            "customer_order_count": 5,
            "customer_refund_rate": 0.0
        }]
    }
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(DELIVERY_URL, json=payload, headers=headers, timeout=90)
        resp.raise_for_status()
        result = resp.json()
        prob = result["predictions"][0]
        pred_delay = 1 if prob > 0.5 else 0
        status = "Delayed" if pred_delay else "On Time"
        return DeliveryResponse(delay_probability=prob, predicted_delay=pred_delay, status=status)
    except Exception as e:
        # Print error for debugging
        print("Error response from Databricks:", resp.text if 'resp' in locals() else str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
# 6. Sentiment Analysis – Request aur Response Models
# ---------------------------------------------------------
class SentimentRequest(BaseModel):
    text: str   # user ka feedback text

class SentimentResponse(BaseModel):
    aspect_sentiments: Dict[str, str]   # e.g., {"delivery": "negative", "quality": "positive"}

# ---------------------------------------------------------
# 7. Sentiment Analysis Endpoint
# ---------------------------------------------------------
@app.post("/analyze-sentiment", response_model=SentimentResponse)
async def analyze_sentiment(req: SentimentRequest):
    """
    Feedback text lega, Databricks sentiment endpoint ko call karega,
    aur aspect-wise sentiment return karega.
    """
    payload = {
        "dataframe_records": [{"text": req.text}]
    }
    headers = {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(SENTIMENT_URL, json=payload, headers=headers, timeout=90)
        resp.raise_for_status()
        result = resp.json()
        # result["predictions"][0] is a dict like {"delivery": "negative", ...}
        return SentimentResponse(aspect_sentiments=result["predictions"][0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

# ---------------------------------------------------------
# 8. Demand Forecast – Alternative (without serving endpoint)
# ---------------------------------------------------------
from databricks import sql
import pandas as pd
import os

@app.get("/forecast")
async def get_forecast():
    try:
        with sql.connect(
            server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_TOKEN")
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT forecast_date, predicted_units FROM workspace.default.demand_forecast ORDER BY forecast_date")
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
        df['forecast_date'] = df['forecast_date'].astype(str)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ---------------------------------------------------------
# 9. Health check endpoint – server alive hai ya nahi
# ---------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------------------------------------------------------
# 10. Main function – server start karna
# ---------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

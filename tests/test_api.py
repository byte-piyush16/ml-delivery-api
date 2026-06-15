import requests

BASE_URL = "http://localhost:8000"

def test_health():
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_predict_delay():
    payload = {
        "platform_name": "blinkit",
        "order_value_inr": 450,
        "delivery_time_min": 25,
        "customer_delay_rate": 0.24
    }
    resp = requests.post(f"{BASE_URL}/predict-delay", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "delay_probability" in data
    assert 0 <= data["delay_probability"] <= 1

def test_sentiment():
    resp = requests.post(f"{BASE_URL}/analyze-sentiment", json={"text": "late delivery"})
    assert resp.status_code == 200
    assert "aspect_sentiments" in resp.json()
    
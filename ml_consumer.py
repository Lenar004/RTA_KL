from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import json
import requests

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='broker:9092',
    auto_offset_reset='earliest',
    group_id='ml-scoring',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

alert_producer = KafkaProducer(
    bootstrap_servers='broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

API_URL = "http://localhost:8001/score"
# jeśli consumer działa w Dockerze, zmień na:
# API_URL = "http://host.docker.internal:8001/score"

for msg in consumer:
    transaction = msg.value

    try:
        amount = float(transaction.get("amount", 0))

        timestamp = transaction.get("timestamp")
        if timestamp:
            try:
                hour = datetime.fromisoformat(timestamp).hour
            except Exception:
                hour = 12
        else:
            hour = 12

        category = str(transaction.get("category", "")).lower()
        is_electronics = 1 if category == "electronics" else 0

        features = {
            "amount": amount,
            "hour": hour,
            "is_electronics": is_electronics,
            "tx_per_day": 5
        }

        response = requests.post(API_URL, json=features, timeout=5)
        response.raise_for_status()
        result = response.json()

        if result["is_fraud"]:
            alert = {
                "alert_time": datetime.now().isoformat(),
                "transaction": transaction,
                "score_result": result
            }
            alert_producer.send("alerts", alert)
            print("ALERT:", alert)
        else:
            print("OK:", transaction, result)

    except Exception as e:
        print("Błąd:", e)
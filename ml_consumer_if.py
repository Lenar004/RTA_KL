from kafka import KafkaConsumer, KafkaProducer
import json
import requests

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='broker:9092',
    auto_offset_reset='earliest',
    group_id='ml-scoring-if',  # inny group_id niż ml-scoring!
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

alert_producer = KafkaProducer(
    bootstrap_servers='broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

API_URL = "http://localhost:8001/score"

print("Konsument IF uruchomiony...\n")

for message in consumer:
    tx = message.value
    is_electronics = 1 if tx.get('category') == 'elektronika' else 0
    features = {
        "amount": tx['amount'],
        "is_electronics": is_electronics,
        "tx_per_minute": 5,
    }

    try:
        response = requests.post(API_URL, json=features, timeout=2)
        result = response.json()
    except requests.RequestException as e:
        print(f"API niedostępne: {e}")
        continue

    if result['is_fraud']:
        alert = {**tx, 'fraud_probability': result['fraud_probability'], 'alert_source': 'isolation_forest'}
        alert_producer.send('alerts', value=alert)
        print(f"IF FRAUD [{result['fraud_probability']:.0%}] {tx['tx_id']} | {tx['amount']:.2f} PLN")

alert_producer.flush()
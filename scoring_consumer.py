from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import json

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='broker:9092',
    auto_offset_reset='earliest',
    group_id='scoring-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

alert_producer = KafkaProducer(
    bootstrap_servers='broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def score_transaction(tx):
    score = 0
    rules = []

    # R1: wysoka kwota
    if tx['amount'] > 3000:
        score += 3
        rules.append('R1:high_amount')

    # R2: elektronika + wysoka kwota
    if tx.get('category') == 'elektronika' and tx['amount'] > 1500:
        score += 2
        rules.append('R2:electronics_high')

    # R3: godzina nocna (0-5)
    hour = tx.get('hour')
    if hour is None:
        try:
            hour = datetime.fromisoformat(tx['timestamp']).hour
        except:
            hour = 12
    if hour < 6:
        score += 2
        rules.append('R3:night')

    return score, rules

print("Konsument scoringowy uruchomiony...\n")

for message in consumer:
    tx = message.value
    score, rules = score_transaction(tx)

    if score >= 3:
        alert = {**tx, 'score': score, 'rules': rules, 'alert': True}
        alert_producer.send('alerts', value=alert)
        print(f"ALERT [{score}p] {tx['tx_id']} | {tx['amount']:.2f} PLN | reguły: {rules}")

alert_producer.flush()
import pickle
import numpy as np

# Załaduj model ML
with open("/Users/kacperlenarcik/Desktop/jupyterlab-project/jupyterlab-project/notebooks/fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

# ── SCORING REGUŁOWY ──────────────────────────────────────
def score_transaction(tx):
    score = 0
    rules = []
    if tx['amount'] > 3000:
        score += 3
        rules.append('R1:high_amount')
    if tx.get('category') == 'elektronika' and tx['amount'] > 1500:
        score += 2
        rules.append('R2:electronics_high')
    hour = tx.get('hour', 12)
    if hour < 6:
        score += 2
        rules.append('R3:night')
    return score >= 3, rules

# ── MODEL ML ──────────────────────────────────────────────
def ml_score(tx):
    is_electronics = 1 if tx.get('category') == 'elektronika' else 0
    hour = tx.get('hour', 12)
    x = np.array([[tx['amount'], hour, is_electronics, 5]])
    proba = float(model.predict_proba(x)[0][1])
    return proba >= 0.5, round(proba, 2)

# ── TESTOWE TRANSAKCJE ────────────────────────────────────
transactions = [
    {'tx_id': 'TX001', 'amount': 4500, 'category': 'elektronika', 'hour': 3},
    {'tx_id': 'TX002', 'amount': 150,  'category': 'żywność',     'hour': 14},
    {'tx_id': 'TX003', 'amount': 3500, 'category': 'odzież',      'hour': 10},
    {'tx_id': 'TX004', 'amount': 200,  'category': 'elektronika', 'hour': 2},
    {'tx_id': 'TX005', 'amount': 4900, 'category': 'elektronika', 'hour': 14},
    {'tx_id': 'TX006', 'amount': 50,   'category': 'książki',     'hour': 20},
]

# ── PORÓWNANIE ────────────────────────────────────────────
print(f"\n{'='*70}")
print(f"{'TX':<8} {'Kwota':>8} {'Kategoria':<14} {'Godz':>5} {'Reguły':>8} {'ML':>6} {'Różnica'}")
print(f"{'='*70}")

for tx in transactions:
    reguly_fraud, rules = score_transaction(tx)
    ml_fraud, proba = ml_score(tx)

    roznica = ''
    if reguly_fraud and not ml_fraud:
        roznica = '<- tylko reguły'
    elif ml_fraud and not reguly_fraud:
        roznica = '<- tylko ML'
    elif reguly_fraud and ml_fraud:
        roznica = 'oba!'

    print(
        f"{tx['tx_id']:<8} "
        f"{tx['amount']:>8.0f} "
        f"{tx['category']:<14} "
        f"{tx['hour']:>5} "
        f"{'FRAUD' if reguly_fraud else 'ok':>8} "
        f"{'FRAUD' if ml_fraud else 'ok':>6}  "
        f"{roznica}"
    )

print(f"{'='*70}\n")
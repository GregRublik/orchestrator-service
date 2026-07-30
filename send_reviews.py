"""Отправляет отзывы из reviews.json на обработку оркестратору."""
import json, sys, time
import requests

ORCHESTRATOR = "http://localhost:9800"
REVIEWS_FILE = "reviews.json"

with open(REVIEWS_FILE) as f:
    feedbacks = json.load(f)["data"]["feedbacks"]

print(f"Отзывов для отправки: {len(feedbacks)}")

for i, review in enumerate(feedbacks, 1):
    resp = requests.post(f"{ORCHESTRATOR}/reviews", json=review, timeout=30)
    status = "✓" if resp.status_code == 200 else f"✗ {resp.status_code}"
    name = review.get("productDetails", {}).get("productName", "?")[:70]
    print(f"[{i:2}/{len(feedbacks)}] {status} | {name}")
    if resp.status_code != 200:
        print(f"       {resp.text[:200]}", file=sys.stderr)

print(f"\nГотово. Отправлено {len(feedbacks)} отзывов.")

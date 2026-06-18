# Test API Application

Асинхронное REST API приложение на Sanic + SQLAlchemy + PostgreSQL.

## Требования

- Python 3.12+
- PostgreSQL 16+
- Docker & Docker Compose (опционально)

## Учётные записи по умолчанию

### Администратор
- Email: `admin@test.com`
- Password: `admin123`

### Пользователь
- Email: `user@test.com`
- Password: `user123`

## Запуск с Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно на http://localhost:8000

## Запуск без Docker

1. Установите зависимости:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Настройте переменные окружения (скопируйте `.env.example` в `.env`):
```bash
cp .env.example .env
```

3. Запустите PostgreSQL (или используйте существующий):
```bash
docker run -d --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=testdb -p 5432:5432 postgres:16-alpine
```

4. Примените миграции:
```bash
alembic upgrade head
```

5. Запустите приложение:
```bash
sanic app.main:app --host=0.0.0.0 --port=8000
```

## API Endpoints

### Авторизация

**POST /api/auth/login**
```json
{
  "email": "user@test.com",
  "password": "user123"
}
```

Ответ:
```json
{
  "token": "eyJ..."
}
```

### Пользователь

**GET /api/users/me** — Получить данные о себе

**GET /api/accounts** — Получить список своих счетов

**GET /api/payments** — Получить список своих платежей

### Администратор

**GET /api/admin/users** — Получить список пользователей с счетами

**POST /api/admin/users** — Создать пользователя
```json
{
  "email": "new@test.com",
  "password": "password123",
  "full_name": "New User",
  "is_admin": false
}
```

**PUT /api/admin/users/<id>** — Обновить пользователя
```json
{
  "email": "updated@test.com",
  "full_name": "Updated Name"
}
```

**DELETE /api/admin/users/<id>** — Удалить пользователя

### Webhook (платежи)

**POST /api/webhook/payment**
```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 2,
  "account_id": 1,
  "amount": 100,
  "signature": "48c42941e65822114a136ec0bee75b12644347407a47c897989a8329d39bb62e"
}
```

Подпись формируется как SHA256 хеш от конкатенации значений в алфавитном порядке ключей + секретный ключ:
`{account_id}{amount}{transaction_id}{user_id}{secret_key}`

Секретный ключ по умолчанию: `gfdmhghif38yrf9ew0jkf32`

## Примеры использования с curl

### Авторизация пользователя
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@test.com", "password": "user123"}'
```

### Получить свои данные
```bash
TOKEN="your_token_here"
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Получить свои счета
```bash
curl -X GET http://localhost:8000/api/accounts \
  -H "Authorization: Bearer $TOKEN"
```

### Отправить webhook
```bash
curl -X POST http://localhost:8000/api/webhook/payment \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 2,
    "account_id": 1,
    "amount": 100,
    "signature": "48c42941e65822114a136ec0bee75b12644347407a47c897989a8329d39bb62e"
  }'
```

# Kittygram

Kittygram — учебный веб-проект для публикации карточек котиков. Проект состоит из Django REST API, React frontend, PostgreSQL и Nginx gateway. Приложение подготовлено к запуску через Docker Compose и к деплою на локальный виртуальный сервер Ubuntu.

## Стек технологий

Backend:

- Python 3.10
- Django
- Django REST Framework
- Djoser
- Gunicorn
- PostgreSQL
- drf-yasg для Swagger/ReDoc

Frontend:

- React
- JavaScript
- npm

Инфраструктура:

- Docker
- Docker Compose
- Nginx
- Ubuntu Server
- VirtualBox


## Возможности проекта

Пользователь может:

- зарегистрироваться;
- авторизоваться;
- просматривать карточки котиков;
- создавать карточки котиков;
- редактировать свои карточки;
- удалять свои карточки;
- загружать изображения;
- просматривать API-документацию через Swagger и ReDoc.

## CRUD

В проекте реализован CRUD для карточек котиков и достижений.

CRUD — это базовые операции с объектами:

| Операция | HTTP-метод | Назначение |
|---|---|---|
| Create | POST | Создание объекта |
| Read | GET | Получение списка или одного объекта |
| Update | PUT/PATCH | Полное или частичное обновление |
| Delete | DELETE | Удаление объекта |

Основные CRUD-эндпоинты:

```text
GET     /api/cats/
POST    /api/cats/
GET     /api/cats/{id}/
PUT     /api/cats/{id}/
PATCH   /api/cats/{id}/
DELETE  /api/cats/{id}/
```

CRUD реализован средствами Django REST Framework через `ModelViewSet`, serializers и router.

## Переменные окружения

Перед запуском нужно создать файл `.env` в корне проекта.

Можно скопировать пример:

```bash
cp .env.example .env
```

Пример `.env`:

```env
POSTGRES_DB=kittygram
POSTGRES_USER=kittygram_user
POSTGRES_PASSWORD=kittygram_password
DB_HOST=db
DB_PORT=5432

SECRET_KEY=django-insecure-local-server-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,backend,localhost:8080,127.0.0.1:8080
```

Описание переменных:

| Переменная | Назначение |
|---|---|
| POSTGRES_DB | Название базы данных PostgreSQL |
| POSTGRES_USER | Пользователь PostgreSQL |
| POSTGRES_PASSWORD | Пароль пользователя PostgreSQL |
| DB_HOST | Хост базы данных внутри Docker network |
| DB_PORT | Порт PostgreSQL |
| SECRET_KEY | Секретный ключ Django |
| DEBUG | Режим отладки Django |
| ALLOWED_HOSTS | Разрешённые хосты Django |

Файл `.env` не должен попадать в GitHub.

## Локальный запуск через Docker Compose

### 1. Клонировать репозиторий

```bash
git clone https://github.com/p0nevole/kittigram-xp-profile.git
cd kittigram-xp-profile
git checkout current-rating
```

### 2. Создать `.env`

```bash
cp .env.example .env
```

При необходимости отредактировать файл:

```bash
nano .env
```

### 3. Запустить контейнеры

```bash
docker compose up --build -d
```

### 4. Проверить контейнеры

```bash
docker compose ps
```

Должны быть запущены контейнеры:

```text
db
backend
gateway
```

Контейнер `frontend` может завершиться после копирования собранных файлов в volume. Это нормально.

### 5. Выполнить миграции

```bash
docker compose exec backend python manage.py migrate
```

### 6. Собрать статику backend

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

### 7. Создать суперпользователя

```bash
docker compose exec backend python manage.py createsuperuser
```

### 8. Открыть проект

Если проект запускается локально на компьютере:

```text
http://localhost/
```

Если проект запускается на виртуальном сервере Ubuntu через проброс порта VirtualBox:

```text
http://localhost:8080/
```

Админка:

```text
http://localhost:8080/admin/
```

API:

```text
http://localhost:8080/api/cats/
```

Swagger:

```text
http://localhost:8080/swagger/
```

ReDoc:

```text
http://localhost:8080/redoc/
```


## Примеры API-запросов

### Получить токен

```bash
curl -X POST http://localhost:8080/api/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "Kittygram2026!"}'
```

Пример ответа:

```json
{
  "auth_token": "your_token"
}
```

### Получить список котиков

```bash
curl -X GET http://localhost:8080/api/cats/ \
  -H "Authorization: Token your_token"
```

### Создать котика

```bash
curl -X POST http://localhost:8080/api/cats/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Барсик",
    "color": "#000000",
    "birth_year": 2020
  }'
```

### Обновить котика

```bash
curl -X PATCH http://localhost:8080/api/cats/1/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Мурзик"
  }'
```

### Удалить котика

```bash
curl -X DELETE http://localhost:8080/api/cats/1/ \
  -H "Authorization: Token your_token"
```



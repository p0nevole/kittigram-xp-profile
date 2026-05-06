# Kittygram XP Profile

Проект Kittygram с добавленной функцией **уровней профиля и XP за действия пользователя**.

Пользователь получает опыт за активность в сервисе: создание карточек котов, редактирование карточек, добавление достижений и изображений. На основе накопленного опыта рассчитывается уровень профиля.

## Технологии

- Python
- Django
- Django REST Framework
- Djoser Token Auth
- PostgreSQL
- React
- Docker
- Nginx
- Swagger / ReDoc

## Запуск проекта через Docker

## Клонировать репозиторий:

```bash
git clone https://github.com/<your-username>/kittigram-xp-profile.git
cd kittigram-xp-profile
```


## Запустить контейнеры:

```bash
docker compose -f docker-compose.production.yml up -d --build
```

## Применить миграции:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

## Собрать static-файлы:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
```

## Создать администратора:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## Проект будет доступен по адресам:

- Frontend: `http://localhost/`
- Админка: `http://localhost/admin/`
- Swagger: `http://localhost/swagger/`
- ReDoc: `http://localhost/redoc/`



## Остановка проекта

Остановить контейнеры:

```bash
docker compose -f docker-compose.production.yml down
```

Остановить контейнеры и удалить данные базы:

```bash
docker compose -f docker-compose.production.yml down -v
```

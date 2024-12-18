# Инструкции по запуску проекта

Данный файл содержит инструкции по клонированию и запуску проекта.

## Клонирование проекта

Для начала необходимо клонировать репозиторий проекта на ваш локальный компьютер. Откройте терминал и выполните следующую команду:

```bash
git clone https://github.com/olegalll/Medical_Django.git

или

git clone git@github.com:olegalll/Medical_Django.git
```

## Настройка и запуск проекта
После клонирования репозитория необходимо перейти в папку проекта, и запустить докер
При создании в Докер инициализируется БД, создается пользователь, для джаного устанавиливаются requirements.txt, применяются миграции джанго и запускается проект по адресу http://127.0.0.1:8000
```bash
cd Medical_Django
docker-compose up
```

## Приложение покрыто тестами medical/tests
test_consultations.py - тестирование работы с консультациями от лица разных пользователей (админ, доктор, пациент)
test_users_creation.py - тестирование создание пользователя (админ, доктор, пациент)

Тесты запускаются при помощи pytest в докере либо перейдя в bash докера в /app/medical, либо через команду 

```bash
docker-compose exec web sh -c "cd /app/medical && pytest"
```
Эта команда запустит тесты.

Документация по API написана в API_DOCS.md

Если есть проблемы с запуском docker postgres_db
Она может быть связана с
```bash
volumes:
- ./data:/var/lib/postgresql/data
```
Можно поменять /var/lib/postgresql/data например на /tmp/data

## System Information

- **Ubuntu Version**: 24.04.1 LTS (Codename: noble)
- **Docker Version**: 27.3.1
- **Docker Compose Version**: v2.29.2

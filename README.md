# UMT Python Web HW-08

REST API для управління контактами на FastAPI.

## Встановлення

pip install -r requirements.txt

## Запуск

uvicorn main:app --reload

## Swagger

http://127.0.0.1:8000/docs

## Реалізовано

- Create Contact
- Get All Contacts
- Get Contact By ID
- Update Contact
- Delete Contact
- Search by first_name / last_name / email
- Upcoming birthdays (7 days)
- PostgreSQL
- SQLAlchemy
- Pydantic validation

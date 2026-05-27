# Задание 1-2

## Локальный запуск

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Запуск тестов

```powershell
pytest
```

![Запуск тестов](docs/pytest.png)

## Запуск через Docker Compose

```powershell
docker compose up --build
```

![Запуск Docker Compose](docs/docker-up.png)

## Проверка API

```powershell
curl http://localhost:8000/health
```

![Проверка API](docs/health.png)

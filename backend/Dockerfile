# Вибираємо Python-образ
FROM python:3.11-slim-bookworm

# Update system packages to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Оточення
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Робоча директорія
WORKDIR /backend

# Копіюємо requirements та встановлюємо залежності
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копіюємо решту коду
COPY . .

# Команда запуску
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

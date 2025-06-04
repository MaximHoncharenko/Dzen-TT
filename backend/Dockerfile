FROM python:3.11.8-slim-bookworm

# Встановлюємо netcat і build tools
RUN apt-get update && apt-get install -y netcat-openbsd build-essential && apt-get clean

# Робоча директорія
WORKDIR /backend

# Встановлення залежностей
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копіюємо проєкт
COPY . .

# Копіюємо скрипт очікування БД
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Команда запуску
CMD ["/wait-for-db.sh", "daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]

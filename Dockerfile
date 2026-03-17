FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Стандартная переменная окружения
    STORAGE_PATH=data 

WORKDIR /app

# Не создаю нвоого пользователя, потому что код после запуска созадет папку,
# путь которой определяется переменной окружения, которая неизвестна
# RUN adduser appuser \
#     -D -H && \
#     chown -R appuser:appuser /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py"]
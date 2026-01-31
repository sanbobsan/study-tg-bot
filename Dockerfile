FROM python:3.13-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Стандартная переменная окружения
ENV STORAGE_PATH=data 

CMD [ "python", "main.py"]
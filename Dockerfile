FROM python:3.12.1 AS history

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]

FROM mariadb:latest as database

FROM phpmyadmin:latest as dbadmin
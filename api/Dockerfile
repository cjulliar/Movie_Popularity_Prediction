
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /app/

RUN python3 -m pip install --upgrade pip \
pip install -r requirements.txt

COPY . /app/

EXPOSE 8042

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8042"]

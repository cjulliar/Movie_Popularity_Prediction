FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat-openbsd

COPY requirements.txt /app/


RUN python3 -m venv /opt/env/
ENV PATH="opt/env/bin:$PATH"

RUN python3 -m pip install --upgrade pip \
pip install -r requirements.txt 


COPY . /app/

EXPOSE 8000

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "sh", "/app/entrypoint.sh" ]
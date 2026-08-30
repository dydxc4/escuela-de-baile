# syntax=docker/dockerfile:1

FROM python:3.14.7-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev build-essential pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia el proyecto Django/Python
COPY edb /app/

# Copia explícitamente el script de entrada desde la raíz
COPY entrypoint.sh /app/entrypoint.sh

# Corrige formatos de línea Windows (CRLF a LF) y otorga permisos de ejecución
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD ["gunicorn", "edb.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
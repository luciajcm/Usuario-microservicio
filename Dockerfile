FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Crear directorio para datos (como theaters)
RUN mkdir -p /app/data

EXPOSE 5000

# Usar variable de entorno para BD
ENV DATABASE_URL=sqlite:///./data/usuarios.db

CMD ["python", "app/main.py"]
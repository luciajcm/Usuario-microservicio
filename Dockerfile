FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema para MySQL
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src/ .

EXPOSE 5000

CMD ["python", "app.py"]
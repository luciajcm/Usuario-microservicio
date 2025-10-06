FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario con UID 1000 para que coincida con tu usuario en la VM
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Crear directorios necesarios
RUN mkdir -p /app && \
    chown -R appuser:appuser /app

EXPOSE 5000

# Valores por defecto (serán sobrescritos por .env)
ENV DATABASE_URL=mysql+pymysql://default:default@localhost:3306/default_db
ENV JWT_SECRET=default-secret-change-in-production

# Cambiar al usuario no-root
USER appuser

CMD ["python", "app/main.py"]
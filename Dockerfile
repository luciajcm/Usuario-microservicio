FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario específico para la aplicación
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Crear directorio de datos y dar permisos al usuario appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app/data

EXPOSE 5000

# Usar directorio persistente
ENV DATABASE_URL=sqlite:///./data/usuarios.db

# Cambiar al usuario no-root
USER appuser

CMD ["python", "app/main.py"]
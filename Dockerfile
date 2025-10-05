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

# Crear directorios necesarios y dar permisos
RUN mkdir -p /app/data /app/instance && \
    chown -R appuser:appuser /app

EXPOSE 5000

# Usar directorio persistente
ENV DATABASE_URL=sqlite:///./data/usuarios.db

# Cambiar al usuario no-root
USER appuser

CMD ["python", "app/main.py"]
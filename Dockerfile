FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario con UID 1000 para que coincida con tu usuario en la VM
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Crear directorios necesarios
RUN mkdir -p /app/data /app/instance && \
    chown -R appuser:appuser /app

EXPOSE 5000

# Usar ruta ABSOLUTA para la base de datos (nota las 4 barras)
ENV DATABASE_URL=sqlite:////app/data/usuarios.db

# Cambiar al usuario no-root
USER appuser

CMD ["python", "app/main.py"]
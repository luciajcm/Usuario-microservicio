# app/database.py
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/usuarios.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Para SQLite, agregar parámetros de conexión
    if DATABASE_URL.startswith("sqlite"):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'connect_args': {
                'check_same_thread': False,
                'isolation_level': None  # Esto ayuda con las foreign keys
            }
        }
    
    db.init_app(app)
    return db
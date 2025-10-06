import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL no está configurada en las variables de entorno")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    db.init_app(app)
    print(f"✅ Conectado a MySQL")
    return db
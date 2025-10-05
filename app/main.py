from flask import Flask
from database import db
from models import Usuario, PerfilUsuario
import os
import sqlite3
from pathlib import Path

def create_app():
    app = Flask(__name__)
    
    # Configuración desde variables de entorno
    database_url = os.getenv('DATABASE_URL', 'sqlite:///./data/usuarios.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print(f"🔧 Configurando base de datos: {database_url}")
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Crear tablas con manejo robusto de errores
    with app.app_context():
        try:
            # Si es SQLite, asegurar que el directorio existe
            if database_url.startswith('sqlite'):
                # Extraer la ruta del archivo de la URL
                db_path = database_url.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                
                print(f"📁 Ruta de BD: {db_path}")
                print(f"📂 Directorio: {db_dir}")
                
                # Crear directorio si no existe
                if db_dir and not os.path.exists(db_dir):
                    print(f"🛠️ Creando directorio: {db_dir}")
                    os.makedirs(db_dir, mode=0o755, exist_ok=True)
                
                # Verificar permisos de escritura
                test_file = os.path.join(db_dir if db_dir else '.', 'test_permisos.txt')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    print("✅ Permisos de escritura verificados")
                except Exception as e:
                    print(f"❌ Error de permisos: {e}")
                    # Crear en directorio temporal como fallback
                    temp_db_path = '/tmp/usuarios.db'
                    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db_path}'
                    print(f"🔄 Usando base de datos temporal: {temp_db_path}")
            
            # Crear tablas
            print("🔄 Creando tablas de la base de datos...")
            db.create_all()
            
            # Verificar que las tablas se crearon
            user_count = Usuario.query.count()
            print(f"✅ Usuarios Microservice - Tablas creadas (Usuarios: {user_count})")
            
        except Exception as e:
            print(f"❌ Error crítico creando tablas: {str(e)}")
            # Intentar con base de datos en memoria como último recurso
            try:
                print("🔄 Intentando con base de datos en memoria...")
                app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
                db.create_all()
                print("✅ Tablas creadas en base de datos en memoria")
            except Exception as e2:
                print(f"💥 Error fatal: {e2}")
                raise
    
    # Health check
    @app.route('/health')
    def health():
        try:
            user_count = Usuario.query.count()
            return {
                "status": "healthy", 
                "service": "usuarios",
                "version": "1.0.0",
                "total_usuarios": user_count
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}, 500
    
    # API Info
    @app.route('/')
    def api_info():
        return {
            "service": "usuarios",
            "version": "1.0.0",
            "endpoints": {
                "auth": ["POST /auth/register", "POST /auth/login"],
                "users": ["GET /users/profile", "GET /users/"]
            }
        }
    
    # Importar y registrar rutas
    from routers import auth, users
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(users.bp, url_prefix='/users')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
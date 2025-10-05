# app/main.py
from flask import Flask
from database import init_db, db
from models import Usuario, PerfilUsuario
import os
import sqlite3

def create_app():
    app = Flask(__name__)
    
    # Inicializar base de datos
    init_db(app)
    
    # Crear tablas con manejo robusto de errores
    with app.app_context():
        try:
            print("🔄 Intentando crear tablas de la base de datos...")
            
            # Verificar que podemos escribir en el directorio
            test_file = '/app/data/test_permissions.txt'
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("✅ Permisos de escritura verificados en /app/data/")
            except Exception as e:
                print(f"❌ Error de permisos en /app/data/: {e}")
                return None
            
            # Crear tablas
            db.create_all()
            
            # Verificar que las tablas se crearon
            user_count = Usuario.query.count()
            print(f"✅ Microservicio Usuario - Tablas creadas (Usuarios: {user_count})")
            
        except Exception as e:
            print(f"❌ Error crítico creando tablas: {str(e)}")
            print("💡 Posibles soluciones:")
            print("1. Verificar permisos del volumen Docker")
            print("2. Verificar que SQLite está instalado")
            print("3. Verificar espacio en disco")
            return None
    
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
            "description": "Microservicio de gestión de usuarios y autenticación",
            "endpoints": {
                "auth": ["POST /auth/register", "POST /auth/login"],
                "users": ["GET /users/profile", "GET /users/", "PUT /users/profile/tipo"]
            }
        }
    
    # Importar y registrar rutas
    from routers import auth, users
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(users.bp, url_prefix='/users')
    
    return app

if __name__ == '__main__':
    app = create_app()
    if app:
        print("🚀 Microservicio Usuario iniciado correctamente en puerto 5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("💥 No se pudo iniciar el microservicio")
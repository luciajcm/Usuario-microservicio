from flask import Flask
from database import db
from models import Usuario, PerfilUsuario
import os

def create_app():
    app = Flask(__name__)
    
    # Configuración desde variables de entorno
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///./data/usuarios.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Crear tablas
    with app.app_context():
        db.create_all()
        print("✅ Usuarios Microservice - Tablas creadas")
    
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
# app/main.py - VERSIÓN SIMPLE
from flask import Flask
from database import init_db, db
from models import Usuario, PerfilUsuario

def create_app():
    app = Flask(__name__)
    
    # Inicializar base de datos
    init_db(app)
    
    # Crear tablas SIN manejo complejo de errores
    with app.app_context():
        db.create_all()
        print("✅ Tablas creadas exitosamente")
    
    # Health check simple
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "usuarios"}
    
    # Importar y registrar rutas
    from routers import auth, users
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(users.bp, url_prefix='/users')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Servicio iniciado en puerto 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
from flask import Flask
from flask_restx import Api, Resource  # 👈 NUEVOS IMPORTS
from database import init_db, db

def create_app():
    app = Flask(__name__)
    init_db(app)
    
    # ✅ CONFIGURAR SWAGGER
    api = Api(
        app, 
        version='1.0', 
        title='Microservicio de Usuarios API',
        description='API para gestión de usuarios con MySQL',
        doc='/docs/',  # 👈 URL de la documentación Swagger
        prefix='/api'
    )
    
    # ✅ IMPORTAR MODELOS
    from models import Usuario
    
    with app.app_context():
        try:
            print("🔄 Intentando crear tablas en MySQL...")
            db.create_all()
            
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            print(f"✅ Tablas creadas exitosamente en MySQL: {tablas}")
                
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
    
    # ✅ HEALTH CHECK ENDPOINT
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "usuarios", "database": "MySQL"}
    
    # ✅ NAMESPACES PARA SWAGGER
    from routers import auth, users
    api.add_namespace(auth.ns, path='/auth')  # 👈 CAMBIO: usar api.add_namespace
    api.add_namespace(users.ns, path='/users')  # 👈 CAMBIO: usar api.add_namespace
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Servicio de usuarios iniciado en puerto 5000 (MySQL)")
    print("📚 Swagger UI disponible en: http://0.0.0.0:5000/docs/")
    app.run(host='0.0.0.0', port=5000, debug=False)
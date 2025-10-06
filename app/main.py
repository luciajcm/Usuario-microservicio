from flask import Flask
from database import init_db, db

def create_app():
    app = Flask(__name__)
    init_db(app)
    
    # ✅ IMPORTAR LOS MODELOS ANTES de crear las tablas
    # Esto es ESSENCIAL para que SQLAlchemy reconozca las tablas
    from models import Usuario
    
    with app.app_context():
        try:
            print("🔄 Intentando crear tablas en MySQL...")
            
            # Crear todas las tablas definidas en los modelos
            db.create_all()
            
            # Verificar que las tablas se crearon
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            
            print(f"✅ Tablas creadas exitosamente en MySQL: {tablas}")
            
            # Verificar específicamente la tabla 'usuarios'
            if 'usuarios' in tablas:
                print("🎉 Tabla 'usuarios' creada correctamente")
            else:
                print("❌ Tabla 'usuarios' NO se creó")
                
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            print("💡 Posibles soluciones:")
            print("   1. Verificar conexión a la base de datos")
            print("   2. Verificar que el usuario tiene permisos CREATE")
            print("   3. Verificar que la base de datos existe")
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "usuarios", "database": "MySQL"}
    
    # Importar y registrar blueprints
    from routers import auth, users
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(users.bp, url_prefix='/users')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Servicio de usuarios iniciado en puerto 5000 (MySQL)")
    app.run(host='0.0.0.0', port=5000, debug=False)
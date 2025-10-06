from flask import Flask
from database import init_db, db

def create_app():
    app = Flask(__name__)
    
    init_db(app)
    
    with app.app_context():
        try:
            # Forzar creación de tablas
            db.create_all()
            print("✅ Tablas creadas exitosamente en MySQL")
            
            # Verificar que la tabla existe
            from sqlalchemy import text
            result = db.session.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"✅ Tablas en la base de datos: {tables}")
            
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            # Intentar recrear desde cero
            try:
                db.drop_all()
                db.create_all()
                print("✅ Tablas recreadas exitosamente")
            except Exception as e2:
                print(f"❌ Error crítico: {e2}")
    
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "usuarios", "database": "MySQL"}
    
    from routers import auth, users
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(users.bp, url_prefix='/users')
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Servicio de usuarios iniciado en puerto 5000 (MySQL)")
    app.run(host='0.0.0.0', port=5000, debug=False)
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from database import db
from models import Usuario, PerfilUsuario
import os
from datetime import datetime

app = Flask(__name__)

# Configuración
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'secret-key')

# Inicializar extensiones
db.init_app(app)
jwt = JWTManager(app)

# Crear tablas al iniciar
with app.app_context():
    db.create_all()
    print("✅ Tablas de Usuarios creadas: usuarios, perfiles_usuario")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service": "usuarios",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "MySQL"
    })

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Datos JSON requeridos"}), 400
            
        # Validaciones básicas
        required_fields = ['nombre', 'apellidos', 'login', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Campo {field} es requerido"}), 400
        
        # Verificar si usuario ya existe
        if Usuario.query.filter_by(login=data['login']).first():
            return jsonify({"error": "El usuario ya existe"}), 400
        
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400

        # Crear usuario
        usuario = Usuario(
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            login=data['login'],
            email=data['email'],
            phone_number=data.get('phone_number', '')
        )
        usuario.set_password(data['password'])
        
        db.session.add(usuario)
        db.session.flush()  # Obtener ID sin commit
        
        # Crear perfil automáticamente
        perfil = PerfilUsuario(usuario_id=usuario.id)
        db.session.add(perfil)
        db.session.commit()

        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user_id": usuario.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('login') or not data.get('password'):
            return jsonify({"error": "Login y password requeridos"}), 400
        
        usuario = Usuario.query.filter_by(login=data['login']).first()

        if usuario and usuario.check_password(data['password']):
            token = create_access_token(identity=usuario.id)
            return jsonify({
                "access_token": token,
                "user": usuario.to_dict()
            }), 200

        return jsonify({"error": "Credenciales inválidas"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        usuario = Usuario.query.get(user_id)
        
        if usuario:
            return jsonify(usuario.to_dict()), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
    except Exception as e:
        return jsonify({"error": "Token inválido"}), 401

@app.route('/usuarios', methods=['GET'])
def list_usuarios():
    try:
        usuarios = Usuario.query.all()
        return jsonify([usuario.to_dict() for usuario in usuarios]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
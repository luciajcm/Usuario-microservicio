from flask import Blueprint, request, jsonify
from database import db
from models import Usuario
from auth_utils import create_jwt_token

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Datos JSON requeridos"}), 400
            
        required_fields = ['nombre', 'apellidos', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Campo {field} es requerido"}), 400
        
        # Solo verificar email (eliminado login)
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400

        usuario = Usuario(
            nombre=data['nombre'],
            apellidos=data['apellidos'],
            email=data['email'],
            phone_number=data.get('phone_number', '')
        )
        usuario.set_password(data['password'])
        
        db.session.add(usuario)
        db.session.commit()

        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user_id": usuario.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Cambiar 'login' por 'email'
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email y password requeridos"}), 400
        
        # Buscar solo por email
        usuario = Usuario.query.filter_by(email=data['email']).first()

        if usuario and usuario.check_password(data['password']):
            token = create_jwt_token(usuario.id)
            
            return jsonify({
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "apellidos": usuario.apellidos,
                    "email": usuario.email,
                    "phone_number": usuario.phone_number
                }
            }), 200

        return jsonify({"error": "Credenciales inválidas"}), 401

    except Exception as e:
        return jsonify({"error": f"Error del servidor: {str(e)}"}), 500
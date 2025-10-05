from flask import Blueprint, jsonify, request
from database import db
from models import Usuario
from auth_utils import token_required

bp = Blueprint('users', __name__)

@bp.route('/profile', methods=['GET'])
@token_required
def profile(user_id):
    try:
        usuario = Usuario.query.get(user_id)
        
        if usuario:
            return jsonify({
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellidos": usuario.apellidos,
                "email": usuario.email,
                "phone_number": usuario.phone_number
            }), 200
        
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@bp.route('/', methods=['GET'])
def list_users():
    usuarios = Usuario.query.all()
    return jsonify([{
        "id": u.id,
        "nombre": u.nombre,
        "apellidos": u.apellidos,
        "email": u.email,
        "phone_number": u.phone_number
    } for u in usuarios]), 200

@bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(user_id):
    try:
        data = request.get_json()
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Campos que se pueden actualizar
        if 'nombre' in data:
            usuario.nombre = data['nombre']
        if 'apellidos' in data:
            usuario.apellidos = data['apellidos']
        if 'phone_number' in data:
            usuario.phone_number = data['phone_number']
        
        db.session.commit()
        
        return jsonify({
            "message": "Perfil actualizado exitosamente",
            "user": {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellidos": usuario.apellidos,
                "email": usuario.email,
                "phone_number": usuario.phone_number
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error: {str(e)}"}), 500

@bp.route('/profile/password', methods=['PUT'])
@token_required
def update_password(user_id):
    try:
        data = request.get_json()
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Verificar password actual
        if not usuario.check_password(data.get('current_password')):
            return jsonify({"error": "Password actual incorrecto"}), 400
        
        # Actualizar nuevo password
        usuario.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({"message": "Password actualizado exitosamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error: {str(e)}"}), 500
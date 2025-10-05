# app/routers/users.py
from flask import Blueprint, jsonify, request  # ← AGREGAR request aquí
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
                "login": usuario.login,
                "email": usuario.email,
                "phone_number": usuario.phone_number,
                "tipo_usuario": usuario.perfil.tipo_usuario
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
        "login": u.login,
        "email": u.email,
        "tipo_usuario": u.perfil.tipo_usuario
    } for u in usuarios]), 200

@bp.route('/profile/tipo', methods=['PUT'])
@token_required
def update_tipo_usuario(user_id):
    try:
        data = request.get_json()
        nuevo_tipo = data.get('tipo_usuario')
        
        if nuevo_tipo not in ['regular', 'estudiante', 'vip']:
            return jsonify({"error": "Tipo de usuario inválido"}), 400
        
        usuario = Usuario.query.get(user_id)
        if usuario:
            usuario.perfil.tipo_usuario = nuevo_tipo
            db.session.commit()
            return jsonify({"message": "Tipo de usuario actualizado"}), 200
        
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500
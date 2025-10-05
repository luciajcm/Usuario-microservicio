from flask import Blueprint, jsonify
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
        "login": u.login,
        "email": u.email
    } for u in usuarios]), 200
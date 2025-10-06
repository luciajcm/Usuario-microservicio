from flask import request, jsonify
from flask_restx import Namespace, Resource, fields  # 👈 NUEVOS IMPORTS
from database import db
from models import Usuario
import jwt
import os

# ✅ DEFINIR NAMESPACE PARA SWAGGER
ns = Namespace('users', description='Operaciones con usuarios')

# ✅ MODELO PARA RESPUESTA DE USUARIO
user_model = ns.model('User', {
    'id': fields.Integer(description='ID del usuario'),
    'nombre': fields.String(description='Nombre del usuario'),
    'apellidos': fields.String(description='Apellidos del usuario'),
    'email': fields.String(description='Email del usuario'),
    'phone_number': fields.String(description='Número de teléfono'),
    'created_at': fields.String(description='Fecha de creación')
})

# ✅ FUNCIÓN PARA VERIFICAR TOKEN
def verify_token(token):
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ✅ ENDPOINTS CON DOCUMENTACIÓN SWAGGER
@ns.route('/')
class UserList(Resource):
    @ns.doc(security='Bearer Auth')
    @ns.response(200, 'Lista de usuarios obtenida', [user_model])
    @ns.response(401, 'Token inválido o faltante')
    def get(self):
        """Obtener lista de todos los usuarios (requiere autenticación)"""
        try:
            # Verificar token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {"error": "Token de autorización requerido"}, 401
            
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if not payload:
                return {"error": "Token inválido o expirado"}, 401
            
            # Obtener usuarios
            users = Usuario.query.all()
            return [
                {
                    "id": user.id,
                    "nombre": user.nombre,
                    "apellidos": user.apellidos,
                    "email": user.email,
                    "phone_number": user.phone_number,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in users
            ], 200
            
        except Exception as e:
            return {"error": f"Error interno del servidor: {str(e)}"}, 500

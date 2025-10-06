from flask import request
from flask_restx import Namespace, Resource, fields
from database import db
from models import Usuario
import jwt
import os
from functools import wraps

# ✅ DEFINIR NAMESPACE PARA SWAGGER
ns = Namespace('users', description='Operaciones con usuarios')

# ✅ MODELOS PARA SWAGGER
user_model = ns.model('User', {
    'id': fields.Integer(description='ID del usuario'),
    'nombre': fields.String(description='Nombre del usuario'),
    'apellidos': fields.String(description='Apellidos del usuario'),
    'email': fields.String(description='Email del usuario'),
    'phone_number': fields.String(description='Número de teléfono'),
    'created_at': fields.String(description='Fecha de creación')
})

update_profile_model = ns.model('UpdateProfile', {
    'nombre': fields.String(description='Nombre del usuario'),
    'apellidos': fields.String(description='Apellidos del usuario'),
    'phone_number': fields.String(description='Número de teléfono')
})

update_password_model = ns.model('UpdatePassword', {
    'current_password': fields.String(required=True, description='Password actual'),
    'new_password': fields.String(required=True, description='Nuevo password')
})

# ✅ DECORATOR PARA VERIFICAR TOKEN (reemplaza tu auth_utils)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verificar si el token está en el header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
            except:
                pass
        
        if not token:
            return {"error": "Token de autorización requerido"}, 401
        
        try:
            # Decodificar el token
            data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            current_user_id = data['user_id']
            
        except jwt.ExpiredSignatureError:
            return {"error": "Token expirado"}, 401
        except jwt.InvalidTokenError:
            return {"error": "Token inválido"}, 401
        
        # Pasar el user_id a la función decorada
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# ✅ ENDPOINTS

@ns.route('/')
class UserList(Resource):
    @ns.doc(security='Bearer Auth')
    @ns.response(200, 'Lista de usuarios obtenida', [user_model])
    @ns.response(401, 'Token inválido o faltante')
    def get(self):
        """Obtener lista de todos los usuarios (requiere autenticación)"""
        try:
            # Verificar token usando nuestro decorator
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {"error": "Token de autorización requerido"}, 401
            
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            except:
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

@ns.route('/profile')
class UserProfile(Resource):
    @ns.doc(security='Bearer Auth')
    @ns.response(200, 'Perfil obtenido exitosamente', user_model)
    @ns.response(401, 'Token inválido')
    @ns.response(404, 'Usuario no encontrado')
    def get(self):
        """Obtener perfil del usuario autenticado"""
        try:
            # Usar el decorator manualmente para obtener el user_id
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {"error": "Token de autorización requerido"}, 401
            
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
                user_id = payload['user_id']
            except:
                return {"error": "Token inválido o expirado"}, 401
            
            usuario = Usuario.query.get(user_id)
            if not usuario:
                return {"error": "Usuario no encontrado"}, 404
            
            return {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "apellidos": usuario.apellidos,
                "email": usuario.email,
                "phone_number": usuario.phone_number,
                "created_at": usuario.created_at.isoformat() if usuario.created_at else None
            }, 200
            
        except Exception as e:
            return {"error": f"Error: {str(e)}"}, 500

    @ns.doc(security='Bearer Auth')
    @ns.expect(update_profile_model)
    @ns.response(200, 'Perfil actualizado exitosamente', user_model)
    @ns.response(401, 'Token inválido')
    @ns.response(404, 'Usuario no encontrado')
    def put(self):
        """Actualizar perfil del usuario autenticado"""
        try:
            # Obtener user_id del token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {"error": "Token de autorización requerido"}, 401
            
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
                user_id = payload['user_id']
            except:
                return {"error": "Token inválido o expirado"}, 401
            
            data = request.get_json()
            usuario = Usuario.query.get(user_id)
            
            if not usuario:
                return {"error": "Usuario no encontrado"}, 404
            
            # Campos que se pueden actualizar
            if 'nombre' in data:
                usuario.nombre = data['nombre']
            if 'apellidos' in data:
                usuario.apellidos = data['apellidos']
            if 'phone_number' in data:
                usuario.phone_number = data['phone_number']
            
            db.session.commit()
            
            return {
                "message": "Perfil actualizado exitosamente",
                "user": {
                    "id": usuario.id,
                    "nombre": usuario.nombre,
                    "apellidos": usuario.apellidos,
                    "email": usuario.email,
                    "phone_number": usuario.phone_number,
                    "created_at": usuario.created_at.isoformat() if usuario.created_at else None
                }
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error: {str(e)}"}, 500

@ns.route('/profile/password')
class UpdatePassword(Resource):
    @ns.doc(security='Bearer Auth')
    @ns.expect(update_password_model)
    @ns.response(200, 'Password actualizado exitosamente')
    @ns.response(400, 'Password actual incorrecto')
    @ns.response(401, 'Token inválido')
    @ns.response(404, 'Usuario no encontrado')
    def put(self):
        """Actualizar password del usuario"""
        try:
            # Obtener user_id del token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {"error": "Token de autorización requerido"}, 401
            
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
                user_id = payload['user_id']
            except:
                return {"error": "Token inválido o expirado"}, 401
            
            data = request.get_json()
            usuario = Usuario.query.get(user_id)
            
            if not usuario:
                return {"error": "Usuario no encontrado"}, 404
            
            # Verificar password actual
            if not usuario.check_password(data.get('current_password')):
                return {"error": "Password actual incorrecto"}, 400
            
            # Actualizar nuevo password
            usuario.set_password(data['new_password'])
            db.session.commit()
            
            return {"message": "Password actualizado exitosamente"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error: {str(e)}"}, 500
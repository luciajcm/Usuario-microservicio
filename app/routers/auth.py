from flask import request, jsonify
from flask_restx import Namespace, Resource, fields  # 👈 NUEVOS IMPORTS
from database import db
from models import Usuario, UserCreate, UserLogin, validate_user_data
import jwt
import os
from datetime import datetime, timedelta

# ✅ DEFINIR NAMESPACE PARA SWAGGER
ns = Namespace('auth', description='Operaciones de autenticación')

# ✅ MODELOS PARA SWAGGER DOCUMENTATION
register_model = ns.model('Register', {
    'nombre': fields.String(required=True, description='Nombre del usuario'),
    'apellidos': fields.String(required=True, description='Apellidos del usuario'),
    'email': fields.String(required=True, description='Email del usuario'),
    'password': fields.String(required=True, description='Contraseña'),
    'phone_number': fields.String(description='Número de teléfono (opcional)')
})

login_model = ns.model('Login', {
    'email': fields.String(required=True, description='Email del usuario'),
    'password': fields.String(required=True, description='Contraseña')
})

# ✅ ENDPOINTS CON DOCUMENTACIÓN SWAGGER
@ns.route('/register')
class Register(Resource):
    @ns.expect(register_model)
    @ns.response(201, 'Usuario creado exitosamente')
    @ns.response(400, 'Datos inválidos')
    @ns.response(409, 'El usuario ya existe')
    def post(self):
        """Registrar un nuevo usuario"""
        try:
            data = request.get_json()
            
            # Validar datos
            is_valid, message = validate_user_data(data)
            if not is_valid:
                return {"error": message}, 400
            
            # Verificar si el usuario ya existe
            existing_user = Usuario.query.filter_by(email=data['email']).first()
            if existing_user:
                return {"error": "El usuario ya existe"}, 409
            
            # Crear nuevo usuario
            new_user = Usuario(
                nombre=data['nombre'],
                apellidos=data['apellidos'],
                email=data['email'],
                phone_number=data.get('phone_number')
            )
            new_user.set_password(data['password'])
            
            db.session.add(new_user)
            db.session.commit()
            
            return {
                "message": "Usuario creado exitosamente",
                "user": {
                    "id": new_user.id,
                    "nombre": new_user.nombre,
                    "apellidos": new_user.apellidos,
                    "email": new_user.email
                }
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Error interno del servidor: {str(e)}"}, 500

@ns.route('/login')
class Login(Resource):
    @ns.expect(login_model)
    @ns.response(200, 'Login exitoso')
    @ns.response(401, 'Credenciales inválidas')
    def post(self):
        """Iniciar sesión y obtener token JWT"""
        try:
            data = request.get_json()
            user = Usuario.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                return {"error": "Credenciales inválidas"}, 401
            
            # Generar token JWT
            payload = {
                'user_id': user.id,
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
            
            return {
                "message": "Login exitoso",
                "token": token,
                "user": {
                    "id": user.id,
                    "nombre": user.nombre,
                    "apellidos": user.apellidos,
                    "email": user.email
                }
            }, 200
            
        except Exception as e:
            return {"error": f"Error interno del servidor: {str(e)}"}, 500
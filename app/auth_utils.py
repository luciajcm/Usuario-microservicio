import jwt
import datetime
from functools import wraps
from flask import request, jsonify
import os

# Configuración desde variables de entorno
JWT_SECRET = os.getenv('JWT_SECRET', 'clave-secreta-produccion-2025')
JWT_ALGORITHM = 'HS256'

def create_jwt_token(user_id):
    """Crear token JWT manualmente"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    # Convertir bytes a string si es necesario
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return token

def verify_jwt_token(token):
    """Verificar token JWT manualmente"""
    try:
        # Asegurar que el token es string
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
        
    except jwt.ExpiredSignatureError:
        raise Exception('Token expirado')
    except jwt.InvalidTokenError:
        raise Exception('Token inválido')
    except Exception:
        raise Exception('Error verificando token')

def token_required(f):
    """Decorator para proteger endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Obtener token del header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token es requerido'}), 401
        
        try:
            user_id = verify_jwt_token(token)
            # Pasar el user_id a la función
            return f(user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated
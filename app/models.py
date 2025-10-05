from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Eliminar PerfilUsuario ya que no necesitas tipo_usuario

class UserCreate:
    def __init__(self, nombre, apellidos, email, password, phone_number=None):
        self.nombre = nombre
        self.apellidos = apellidos
        self.email = email
        self.password = password
        self.phone_number = phone_number

class UserLogin:
    def __init__(self, email, password):
        self.email = email
        self.password = password

class UserProfile:
    def __init__(self, id, nombre, apellidos, email, phone_number):
        self.id = id
        self.nombre = nombre
        self.apellidos = apellidos
        self.email = email
        self.phone_number = phone_number

def validate_user_data(data):
    required_fields = ['nombre', 'apellidos', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return False, f"Campo {field} es requerido"
    return True, "OK"
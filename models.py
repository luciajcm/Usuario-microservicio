from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación 1-a-1 con Perfil
    perfil = db.relationship('PerfilUsuario', backref='usuario', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'login': self.login,
            'email': self.email,
            'phone_number': self.phone_number,
            'created_at': self.created_at.isoformat()
        }

class PerfilUsuario(db.Model):
    __tablename__ = 'perfiles_usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    tipo_usuario = db.Column(db.String(20), default='regular')
    idioma = db.Column(db.String(10), default='es')
    tema_oscuro = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'tipo_usuario': self.tipo_usuario,
            'idioma': self.idioma,
            'tema_oscuro': self.tema_oscuro
        }
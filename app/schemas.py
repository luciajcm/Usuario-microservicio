class UserCreate:
    def __init__(self, nombre, apellidos, login, email, password, phone_number=None):
        self.nombre = nombre
        self.apellidos = apellidos
        self.login = login
        self.email = email
        self.password = password
        self.phone_number = phone_number

class UserLogin:
    def __init__(self, login, password):
        self.login = login
        self.password = password

# Funciones de utilidad para validación
def validate_user_data(data):
    required_fields = ['nombre', 'apellidos', 'login', 'email', 'password']
    for field in required_fields:
        if not data.get(field):
            return False, f"Campo {field} es requerido"
    return True, "OK"
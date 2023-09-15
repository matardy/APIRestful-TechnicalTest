from cryptography.fernet import Fernet
import jwt
# Generar clave de cifrado
def generate_key():
    return Fernet.generate_key()

# Cifrar datos
def encrypt_data(data, key):
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

# Descifrar datos
def decrypt_data(encrypted_data, key):
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data

def validate_jwt(token, secret_key):
    try:
        # Si el token tiene el prefijo "Bearer ", quítalo
        if token and token.startswith("Bearer "):
            token = token[7:]

        if token is None:
            return False, "No authorization token provided"

        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        return True, decoded_token
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"





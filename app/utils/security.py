
import os
import hashlib
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWTError
from dotenv import load_dotenv

load_dotenv()

# Configuración JWT
JWT_SECRET = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or "dev-secret"
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
security = HTTPBearer()

# Configuración password
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "static_salt_please_change")

def hash_password(password: str) -> str:
    """Genera un hash SHA256 con sal."""
    return hashlib.sha256((password + PASSWORD_SALT).encode("utf-8")).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return hash_password(password) == hashed

def create_jwt_token(firstname: str, lastname: str, email: str, active: bool, admin: bool, id: str, expires_hours: int = 1) -> str:
    """Crea un token JWT con los datos del usuario."""
    expiration = datetime.utcnow() + timedelta(hours=expires_hours)
    payload = {
        "id": id,
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "active": active,
        "admin": admin,
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Valida un token JWT y devuelve la información del usuario."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        email = payload.get("email")
        exp = payload.get("exp")
        active = payload.get("active", True)
        admin = payload.get("admin", False)
        user_id = payload.get("id")
        firstname = payload.get("firstname")
        lastname = payload.get("lastname")

        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expirado")

        if not active:
            raise HTTPException(status_code=401, detail="Usuario inactivo")

        return {
            "id": user_id,
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "active": active,
            "role": "admin" if admin else "user"
        }

    except PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

def validateuser(user: dict = Depends(validate_token)):
    """Permite acceso a cualquier usuario autenticado."""
    if not isinstance(user, dict):
        raise HTTPException(status_code=500, detail="Formato de usuario inválido")
    return user

def validateadmin(user: dict = Depends(validate_token)):
    """Permite acceso solo a usuarios con rol admin."""
    if not isinstance(user, dict):
        raise HTTPException(status_code=500, detail="Formato de usuario inválido")

    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acceso solo para administradores")
    return user

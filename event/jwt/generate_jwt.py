import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from django.core.cache import cache
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY')


def generate_jwt(user_data):
    payload = {
        'id': user_data.id,
        'cpf': user_data.cpf,
        'cnpj': user_data.cnpj,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=1440)
        # Define expiração para 10 minutos
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def generate_jwt_session(user):
    payload = {
        'id': user.id,
        'cpf': user.cpf,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=10080)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def blacklist_jwt(token):
    # Calcular o tempo restante de expiração
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"],
                                  options={"verify_exp": False})
        exp_timestamp = decoded_data.get("exp")
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        time_to_expire = (exp_datetime - datetime.now(timezone.utc)
                          ).total_seconds()
        token_hash = hashlib.md5(token.encode()).hexdigest()
        cache.set(f'blacklisted_token_{token_hash}', True,
                  timeout=int(time_to_expire))
    except jwt.InvalidTokenError:
        pass


def is_token_blacklisted(token):
    token_hash = hashlib.md5(token.encode()).hexdigest()
    return cache.get(f'blacklisted_token_{token_hash}') is not None


def validate_jwt(token):
    if is_token_blacklisted(token):
        return {"error": "Token já foi revogado."}
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return {"error": "Token expirado."}
    except jwt.InvalidTokenError:
        return {"error": "Token inválido."}


def extract_email_from_jwt(token):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded_data.get('email')  # Extraindo o email
        return email
    except jwt.ExpiredSignatureError:
        return None  # O token expirou
    except jwt.InvalidTokenError:
        return None  # O token é inválido

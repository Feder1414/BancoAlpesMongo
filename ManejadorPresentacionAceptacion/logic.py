import jwt

def validate_jwt(token):
    try:
        # Replace 'your_secret_key' with your actual secret key
        # If the secret key from the token issuer is not known, you cannot validate the token
        payload = jwt.decode(token, 'django-insecure-0%eqg^5(^sps_c31(j1lsm6ffnac2unepfv8^&2f5ycd0)p0u3', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Signature has expired.')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token.')
    

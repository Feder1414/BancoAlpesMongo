import jwt



def validate_jwt(token):
    try:
        # Replace 'your_secret_key' with your actual secret key
        # If the secret key from the token issuer is not known, you cannot validate the token
        payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Signature has expired.')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError('Invalid token.')
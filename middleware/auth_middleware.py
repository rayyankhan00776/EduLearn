from fastapi import HTTPException, Header
import jwt

def auth_middleware(x_auth_token = Header()):
    try:
        if not x_auth_token:
            raise HTTPException(401, "No auth token provided")
        
        # Decode JWT token
        verified_token = jwt.decode(x_auth_token, 'education_app_secret', algorithms=["HS256"])
        uid = verified_token.get('id')
        user_type = verified_token.get('user_type')

        if not uid or not user_type:
            raise HTTPException(401, "Token invalid, authorization denied")

        return {'uid': uid, 'user_type': user_type, 'token': x_auth_token}

    except jwt.PyJWTError:
        raise HTTPException(401, "Token is not valid, authorization failed")
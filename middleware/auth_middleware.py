from fastapi import HTTPException, Header
import jwt
import os

# Load JWT secret from environment variable
JWT_SECRET = os.getenv("JWT_SECRET", "fallback_secret")  # Fallback is optional but useful for dev

def auth_middleware(x_auth_token: str = Header(default=None)):
    try:
        if not x_auth_token:
            raise HTTPException(status_code=401, detail="No auth token provided")
        
        # Decode JWT token using environment secret
        verified_token = jwt.decode(x_auth_token, JWT_SECRET, algorithms=["HS256"])
        uid = verified_token.get('id')
        user_type = verified_token.get('user_type')

        if not uid or not user_type:
            raise HTTPException(status_code=401, detail="Token invalid, authorization denied")

        return {'uid': uid, 'user_type': user_type, 'token': x_auth_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired, please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token is not valid, authorization failed")
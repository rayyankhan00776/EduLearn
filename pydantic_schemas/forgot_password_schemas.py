from pydantic import BaseModel, EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    user_type: str  

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    user_type: str
    otp: str
    new_password: str

from pydantic import BaseModel, EmailStr

class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    education_level: str

class TeacherCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    subject: str
    years_of_experience: int
    highest_qualification: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class StudentResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    education_level: str
    
    class Config:
        from_attributes = True

class TeacherResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    subject: str
    years_of_experience: int
    highest_qualification: str
    
    class Config:
        from_attributes = True
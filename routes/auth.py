import uuid
import bcrypt
import jwt
import os
import random
import string
import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models.user import Student, Teacher
from pydantic_schemas.users_schemas import StudentCreate, TeacherCreate, UserLogin, StudentResponse, TeacherResponse
from pydantic_schemas.forgot_password_schemas import ForgotPasswordRequest, VerifyOtpRequest
from middleware.auth_middleware import auth_middleware
from middleware.email_utils import send_otp_email
from typing import Dict, Union

# Load environment variables (only for local)
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "fallback_secret")  # fallback just in case

# In-memory store for OTPs: { (email, user_type): { 'otp': str, 'expires': float } }
otp_store = {}

# Register a new student
@router.post("/student/signup", response_model=StudentResponse, status_code=201)
def signup_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(400, "This email already exists")

    existing_teacher = db.query(Teacher).filter(Teacher.email == student.email).first()
    if existing_teacher:
        raise HTTPException(400, "This email already exists")

    hashed_pw = bcrypt.hashpw(student.password.encode('utf-8'), bcrypt.gensalt())

    student_db = Student(
        id=str(uuid.uuid4()),
        name=student.name,
        email=student.email,
        password=hashed_pw,
        education_level=student.education_level
    )

    db.add(student_db)
    db.commit()
    db.refresh(student_db)

    return student_db

# Register a new teacher
@router.post("/teacher/signup", response_model=TeacherResponse, status_code=201)
def signup_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    existing_teacher = db.query(Teacher).filter(Teacher.email == teacher.email).first()
    if existing_teacher:
        raise HTTPException(400, "This email already exists")

    existing_student = db.query(Student).filter(Student.email == teacher.email).first()
    if existing_student:
        raise HTTPException(400, "This email already exists")

    hashed_pw = bcrypt.hashpw(teacher.password.encode('utf-8'), bcrypt.gensalt())

    teacher_db = Teacher(
        id=str(uuid.uuid4()),
        name=teacher.name,
        email=teacher.email,
        password=hashed_pw,
        subject=teacher.subject,
        years_of_experience=teacher.years_of_experience,
        highest_qualification=teacher.highest_qualification
    )

    db.add(teacher_db)
    db.commit()
    db.refresh(teacher_db)

    return teacher_db

# Login student and return token
@router.post('/student/login')
def login_student(user: UserLogin, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == user.email).first()
    if not student:
        raise HTTPException(400, "Student with this email doesn't exist")

    if not bcrypt.checkpw(user.password.encode(), student.password):
        raise HTTPException(400, "Incorrect Password")

    token = jwt.encode({
        'id': student.id,
        'user_type': 'student'
    }, JWT_SECRET, algorithm='HS256')

    return {
        'token': token, 
        'user': {
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'education_level': student.education_level,
            'user_type': 'student'
        }
    }

# Login teacher and return token
@router.post('/teacher/login')
def login_teacher(user: UserLogin, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.email == user.email).first()
    if not teacher:
        raise HTTPException(400, "Teacher with this email doesn't exist")

    if not bcrypt.checkpw(user.password.encode(), teacher.password):
        raise HTTPException(400, "Incorrect Password")

    token = jwt.encode({
        'id': teacher.id,
        'user_type': 'teacher'
    }, JWT_SECRET, algorithm='HS256')

    return {
        'token': token, 
        'user': {
            'id': teacher.id,
            'name': teacher.name,
            'email': teacher.email,
            'subject': teacher.subject,
            'years_of_experience': teacher.years_of_experience,
            'highest_qualification': teacher.highest_qualification,
            'user_type': 'teacher'
        }
    }

# Protected route to fetch current user info
@router.get('/me')
def current_user_data(db: Session = Depends(get_db), auth_dict=Depends(auth_middleware)):
    user_id = auth_dict['uid']
    user_type = auth_dict['user_type']
    
    if user_type == 'student':
        user = db.query(Student).filter(Student.id == user_id).first()
        if not user:
            raise HTTPException(404, "Student not found")
        
        return {
            "user": {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'education_level': user.education_level,
                'user_type': 'student'
            }
        }
    
    elif user_type == 'teacher':
        user = db.query(Teacher).filter(Teacher.id == user_id).first()
        if not user:
            raise HTTPException(404, "Teacher not found")
        
        return {
            "user": {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'subject': user.subject,
                'years_of_experience': user.years_of_experience,
                'highest_qualification': user.highest_qualification,
                'user_type': 'teacher'
            }
        }
    
    else:
        raise HTTPException(400, "Invalid user type")

# Forgot password - send OTP
@router.post('/forgot-password')
def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = None
    if request.user_type == 'student':
        user = db.query(Student).filter(Student.email == request.email).first()
    elif request.user_type == 'teacher':
        user = db.query(Teacher).filter(Teacher.email == request.email).first()
    if not user:
        raise HTTPException(404, 'User not found')

    otp = ''.join(random.choices(string.digits, k=6))
    otp_store[(request.email, request.user_type)] = {
        'otp': otp,
        'expires': time.time() + 600  # 10 minutes
    }
    background_tasks.add_task(send_otp_email, request.email, otp)
    return {'message': 'OTP sent to your email'}

# Reset password using OTP
@router.post('/reset-password')
def reset_password(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    key = (request.email, request.user_type)
    otp_data = otp_store.get(key)
    if not otp_data or otp_data['otp'] != request.otp or time.time() > otp_data['expires']:
        raise HTTPException(400, 'Invalid or expired OTP')

    user = None
    if request.user_type == 'student':
        user = db.query(Student).filter(Student.email == request.email).first()
    elif request.user_type == 'teacher':
        user = db.query(Teacher).filter(Teacher.email == request.email).first()
    if not user:
        raise HTTPException(404, 'User not found')

    hashed_pw = bcrypt.hashpw(request.new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_pw
    db.commit()
    del otp_store[key]
    return {'message': 'Password reset successful'}

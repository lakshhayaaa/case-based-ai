from pydantic import BaseModel, EmailStr

class SignUpRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
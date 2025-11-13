"""Authentication schemas"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserSignup(BaseModel):
    """User signup request model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=72)
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Validate password doesn't exceed bcrypt's 72-byte limit"""
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError("Password cannot exceed 72 bytes (approximately 72 characters)")
        return v


class UserLogin(BaseModel):
    """User login request model"""
    username: str
    password: str = Field(..., max_length=72)


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User information response model"""
    username: str
    email: str
    full_name: str


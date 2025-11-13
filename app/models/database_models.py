"""SQLAlchemy database models"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for PostgreSQL database"""
    __tablename__ = "users"

    username = Column(String(50), primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"



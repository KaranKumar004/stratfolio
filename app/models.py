from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Subscription status: free, pro
    tier = Column(String, default="free")

    portfolios = relationship("Portfolio", back_populates="owner")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # The slug used for hosting, e.g. stratfolio.com/slug
    slug = Column(String, unique=True, index=True, nullable=True)
    
    template_name = Column(String, default="executive_dark.html")
    
    # Portfolio Content (JSON strings for lists to keep it simple, or separate tables)
    # Storing structured JSON data instead of multiple tables for faster reads/writes 
    # since portfolios are unstructured and varied.
    name = Column(String, nullable=False)
    title = Column(String)
    summary = Column(Text)
    skills = Column(Text)  # Comma separated or JSON string
    
    # JSON strings for complex types (we'll parse them in the API/Frontend)
    experiences_json = Column(Text, default="[]")
    education_json = Column(Text, default="[]")
    contact_json = Column(Text, default="{}")
    
    # Profile image can be stored as a URL to an S3 bucket or locally.
    # We will use base64 for now as the current code does, or a local path.
    profile_image_url = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="portfolios")

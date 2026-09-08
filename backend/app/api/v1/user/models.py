from app.core.database import Base
from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ ="users"
    id = Column(Integer,primary_key=True,nullable=False, index=True, unique=True)
    first_name = Column(String,nullable=False)
    last_name = Column(String,nullable=False)
    email = Column(String,nullable=False,unique=True)
    phone = Column(String)
    password_hash = Column(String) 
    is_active = Column(Boolean,default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),server_default=func.now())

    role = relationship("UserRole",back_populates="user")


class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer,primary_key=True) 
    name = Column(String)


    userrolid= relationship("UserRole",back_populates="roleid")



class UserRole(Base):
    __tablename__ = "userrole"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"))
    role_id = Column(Integer,ForeignKey("roles.id"))


    user = relationship("Users",back_populates="role")
    roleid = relationship("Roles", back_populates="userrolid")


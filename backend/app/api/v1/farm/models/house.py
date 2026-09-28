from app.core.database import Base
from sqlalchemy import Column,Integer,String,Text,DateTime,ForeignKey,Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class House(Base):
    __tablename__ = "houses"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    location = Column(String(255))
    capacity = Column(Integer)
    description = Column(Text)
    status = Column(Boolean, default=True)
    created_by = Column(Integer,ForeignKey("users.id" ,ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True),server_default=func.now())
    updated_at = Column(DateTime(timezone=True),onupdate=func.now(),server_default=func.now())

    # Relationships
    user = relationship("Users", back_populates="house")
    flocks = relationship("Flock", back_populates="house", cascade="all, delete-orphan")

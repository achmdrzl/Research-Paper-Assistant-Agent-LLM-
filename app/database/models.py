from sqlalchemy import Column, Integer, Text, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Paper(Base):
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    source = Column(String(50))  # 'internal_upload' or 'web_search'
    created_at = Column(DateTime, default=func.now())
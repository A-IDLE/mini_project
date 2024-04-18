from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.routers.database import Base

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    title = Column(String(1000))
    description = Column(String(1000))
    org_link = Column(String(1000))
    link = Column(String(1000))
    full_text = Column(String(10000))
    summarized_text = Column(String(1000))
    keyword = Column(String(100))
    emotion = Column(String(100))
    postive_percent = Column(Integer)
    negative_percent = Column(Integer)
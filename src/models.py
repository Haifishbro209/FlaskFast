from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import *

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    encoded_id= Column(String, default='', nullable=False)
    google_id = Column(String, nullable=False, unique= True)
    first_name = Column(String, default=None)
    last_name =  Column(String, default=None)
    email = Column(String, unique=True, nullable=False)
    profile_picture = Column(String)

    session_cookies = relationship('Session_Cookie', back_populates='user')

class Session_Cookie(Base):
    __tablename__ = 'session_cookies'

    token = Column(String(65), primary_key=True, nullable= False)
    user_id = Column(Integer, ForeignKey('users.id'),nullable= False)
    timestamp = Column(DateTime,default= datetime.utcnow())
    expiry = Column(DateTime, nullable=False) 

    ip_address = Column(String(46))    
    user_agent = Column(String(257)) #browser and device infos

    user = relationship('User', back_populates='session_cookies')
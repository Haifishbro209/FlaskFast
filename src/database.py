from dotenv import load_dotenv
import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, date

from src.models import *
import src.encoder as encoder
from src.argon2_encrypter import encode

print(os.getcwd())

load_dotenv() 
DB_URL = os.getenv("DB_URL")

print('Succesfully got the DB_URL')

engine = create_engine(DB_URL)  
with engine.connect() as conn:
    print("Succesfull connect to db")

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def new_user(user_data):
    '''{'id': '134583495834171768',
      'email': 'kaloyan.nikolov@gmail.com', 
      'verified_email': True, 
      'name': 'Kaloyan Nikolov', 
      'given_name': 'Kaloyan', 
      'family_name': 'Nikolov',
      'picture': 'https://lh3.googleusercontenta/ACg8ocLd234jdJerJJpI6vwVUQeKQ4K7zzadMQKM_ACzTLPWk7HDKSDNNZI=s96-c'}'''
    session = Session()
    try:
        existing_user = session.query(User).filter_by(google_id=user_data['id']).first()
        if existing_user:
            print("User already exists.")
            return existing_user.id

        new_user = User(
            google_id=user_data['id'],
            first_name=user_data.get('given_name'),
            last_name=user_data.get('family_name'),
            email=user_data['email'],
            profile_picture=user_data.get('picture'),
        )
        session.add(new_user)
        session.flush()

        new_user.encoded_id = encoder.encode(new_user.id)

        session.commit()
        print("New user added successfully.")
        return new_user.id
    except Exception as e:
        session.rollback()
        print(f"Error adding new user: {e}")
        raise
    finally:
        session.close()


def save_cookie(user_id, token,expiry,ip,user_agent):
    session = Session()
    try:
       new_cookie = Session_Cookie(
           token = token,
           user_id = user_id,
           expiry = expiry,
           ip_address = ip,
           user_agent = user_agent
       )
       session.add(new_cookie)
       session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()        

def get_user_id(hash):
    """Get user ID from encoded hash"""
    session = Session()
    try:
        user = session.query(User).filter(User.encoded_id == hash).first()
        if user:
            return user.id
        return None
    except Exception as e:
        session.rollback()
        print(f"Error getting user ID: {e}")
        return None
    finally:
        session.close()

def verify_token(token, user_id):
    """Verify if token is valid for the given user"""
    from argon2_encrypter import check_pwd
    from datetime import datetime
    
    session = Session()
    try:
        # Get all active sessions for this user
        active_sessions = session.query(Session_Cookie).filter(
            Session_Cookie.user_id == user_id,
            Session_Cookie.expiry > datetime.utcnow()
        ).all()
        
        # Check if any session matches the provided token
        for session_cookie in active_sessions:
            if check_pwd(token, session_cookie.token):
                return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error verifying token: {e}")
        return False
    finally:
        session.close()

def cleanup_expired_tokens():
    """Remove expired tokens from database"""
    from datetime import datetime
    
    session = Session()
    try:
        expired_tokens = session.query(Session_Cookie).filter(
            Session_Cookie.expiry <= datetime.utcnow()
        )
        count = expired_tokens.count()
        expired_tokens.delete()
        session.commit()
        print(f"Cleaned up {count} expired tokens")
    except Exception as e:
        session.rollback()
        print(f"Error cleaning up expired tokens: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    pass
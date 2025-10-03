from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(time_cost=2, memory_cost=20000, parallelism=1)

def encode(pwd):
    return ph.hash(pwd)
     

def check_pwd(pwd,hashed_pwd):
    try:        
        return ph.verify(hashed_pwd,pwd)
    except VerifyMismatchError:
        return False



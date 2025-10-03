import sys
import os
import urllib.parse
sys.path.insert(0, os.path.dirname(__file__))

from create_env import extract_oauth_creds_to_dotenv
from key_input import get_key

B = '\033[1m' #BOLD
R = '\033[0m' #RESET
Y = '\033[33m'#YELLOW

print(f'{Y}1) create an OAuth client {R}')
credentials_in_folder = None
while credentials_in_folder != 'y':
    print(f'\nHave you put the client_secret***.json somewhere in this folder? {B}(y/n){R}')
    credentials_in_folder = get_key()

print()
print(".env file is beeing created")
extract_oauth_creds_to_dotenv()
print('')

print(f'{Y}2) set up the DB{R}')

print('go to https://supabase.com/dashboard/org/')
print('Create new Project, Location == Central EU (Frankfurt) "eu-central-1"')
correct_pwd = 'n'
while correct_pwd != 'y':
    print(f'{B} Please enter the supabase password below.{R}')
    db_pwd = input()
    print(f'Is {B}{db_pwd}{R} the correct password? {B}(y/n){R}?')
    correct_pwd = get_key()

db_pwd = urllib.parse.quote(db_pwd)

print(f'\n Click the {B}Connect{R} button in the nav aber on the top ')
print(f'Copy the {B}Transaction Pooler{R} URL and paste it here' )
db_url_nopwd = input()

parts = db_url_nopwd.split('[YOUR-PASSWORD]')
parts.append(parts[1])
parts[1] = db_pwd
DB_URL = ''.join(parts)

with open('.env', 'a') as e:
    e.write(f'\nDB_URL={DB_URL}')
print(f'{Y} The DB URL was successfully merged and saved in the .env{R}')

print(f"{Y}\n How long should the session cookies be valid until a new login is needed?{B}\n default is 60 days{R}")
expiry = input()
try:
    expiry = int(expiry)

except ValueError as e:
    expiry = 60

with open('.env', 'a') as e:
    e.write(f'\nSESSION_LENGTH={expiry}')

print(f"\n {B} SESSION_LENGTH {R} set to {B}{expiry}{R}  in the .env")
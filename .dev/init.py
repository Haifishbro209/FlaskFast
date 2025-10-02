import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from create_env import extract_oauth_creds_to_dotenv

B = '\033[1m' #BOLD
R = '\033[0m' #RESET
Y = '\033[33m'#YELLOW

print(f'{Y}1) create an OAuth client and {R}')
print()
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
    correct_pwd = input()

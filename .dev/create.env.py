import glob
import os

files = glob.glob('**/client_secret*.json', recursive=True)
hidden_files = glob.glob('.*/**/client_secret*.json', recursive=True)
all_files = files + hidden_files



if len(all_files) ==0:
    print(f'No client secrets files found in {os.getcwd()} and all subdirectories')
    os.exit()

if len(all_files) > 1:
    for f in range(len(all_files)):
        print(f'{f + 1}. {all_files[f]}')
    print('Multiple files were found which one is the right one?')
    index = int(input())
    index -=1
    secrets = [index]
else:
    secrets = all_files[0]
    print(f'{all_files[0]} found!')

with open(secrets)
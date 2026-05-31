"""
create_env.py
-------------
Finds a client_secret*.json in the repository and extracts
GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET into the .env file.
"""

import glob
import json
import os


def extract_google_creds(env_path: str = "../.env") -> None:
    """Scan for client_secret*.json and append Google credentials to .env."""
    patterns = [
        "**/*client_secret*.json",
        ".*/**/*client_secret*.json",
    ]
    files: list[str] = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))
    files = list(set(files))

    if not files:
        print(f"No client_secret*.json found under {os.getcwd()}")
        raise FileNotFoundError("client_secret*.json not found")

    if len(files) > 1:
        print("Multiple client_secret files found:")
        for i, f in enumerate(files, 1):
            print(f"  {i}. {f}")
        idx = int(input("Which one should be used? ")) - 1
        chosen = files[idx]
    else:
        chosen = files[0]
        print(f"Found: {chosen}")

    with open(chosen) as fh:
        data = json.load(fh)["web"]

    _append_env(env_path, f'GOOGLE_CLIENT_ID={data["client_id"]}')
    _append_env(env_path, f'GOOGLE_CLIENT_SECRET={data["client_secret"]}')
    print("Google credentials written to .env")


def _append_env(path: str, line: str) -> None:
    with open(path, "a") as fh:
        fh.write(line + "\n")

#!/usr/bin/env python3
"""
init.py  –  FastFlask setup wizard
====================================
Run once from the project root:

    python .dev/init.py

What it does
------------
1. Asks which auth method you want (username, google, or both).
2. Copies the right templates and helper files into the project.
3. Patches app.py with the correct auth routes.
4. Creates / updates .env with:
   - DB_URL   (Supabase transaction pooler URL + URL-encoded password)
   - SECRET_KEY
   - ENCODING_SECRET
   - SESSION_LENGTH
   - GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET  (Google only)
   - GOOGLE_REDIRECT_URI                       (Google only)
5. Writes requirements.txt for the chosen auth method.
"""

import os
import re
import secrets
import shutil
import sys
import urllib.parse

# Make sure we can import sibling modules even when called from project root
sys.path.insert(0, os.path.dirname(__file__))

from key_input import get_key

# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------
B  = "\033[1m"       # bold
R  = "\033[0m"       # reset
G  = "\033[32m"      # green
Y  = "\033[33m"      # yellow
C  = "\033[36m"      # cyan
ER = "\033[31m"      # red

ROOT     = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEV      = os.path.dirname(__file__)
ENV_PATH = os.path.join(ROOT, ".env")


def _print(text: str) -> None:
    print(text)


def _section(title: str) -> None:
    _print(f"\n{Y}{B}── {title} {'─' * (50 - len(title))}{R}")


def _ok(msg: str) -> None:
    _print(f"{G}✓  {msg}{R}")


def _err(msg: str) -> None:
    _print(f"{ER}✗  {msg}{R}")


def _ask_yn(question: str) -> bool:
    _print(f"\n{question} {B}(y/n){R} ", end="", flush=True)
    while True:
        k = get_key().lower()
        if k in ("y", "n"):
            _print(k)
            return k == "y"


def _ask_line(prompt: str, hidden: bool = False) -> str:
    if hidden:
        import getpass
        return getpass.getpass(f"{prompt}: ")
    return input(f"{prompt}: ").strip()


# ---------------------------------------------------------------------------
# Step 1 – choose auth method
# ---------------------------------------------------------------------------

def choose_auth() -> str:
    """Returns 'username', 'google', or 'both'."""
    _section("Authentication method")
    _print(f"""
  {B}1{R}  Username + password
  {B}2{R}  Google OAuth
  {B}3{R}  Both

Choose {B}(1 / 2 / 3){R}: """, end="", flush=True)

    while True:
        k = get_key()
        if k in ("1", "2", "3"):
            _print(k)
            mapping = {"1": "username", "2": "google", "3": "both"}
            choice = mapping[k]
            _ok(f"Auth method: {B}{choice}{R}")
            return choice


# ---------------------------------------------------------------------------
# Step 2 – copy files
# ---------------------------------------------------------------------------

def copy_auth_files(method: str) -> None:
    _section("Copying auth files")

    src_dir = os.path.join(DEV, f"auth_{method}")

    # templates
    for fname in ("login.html", "register.html"):
        src  = os.path.join(src_dir, fname)
        dst  = os.path.join(ROOT, "templates", fname)
        shutil.copy2(src, dst)
        _ok(f"templates/{fname}")

    # google_auth.py goes to project root (imported by app.py)
    if method in ("google", "both"):
        src = os.path.join(DEV, "auth_google", "google_auth.py")
        dst = os.path.join(ROOT, "google_auth.py")
        shutil.copy2(src, dst)
        _ok("google_auth.py")


# ---------------------------------------------------------------------------
# Step 3 – patch app.py with auth routes
# ---------------------------------------------------------------------------

def patch_app(method: str) -> None:
    _section("Patching app.py")

    routes_file = os.path.join(DEV, f"auth_{method}", "auth_routes.py")
    with open(routes_file) as fh:
        routes_code = fh.read()

    # Strip the module-level docstring and comment block
    routes_code = re.sub(r'^""".*?"""\n', "", routes_code, flags=re.DOTALL)
    routes_code = re.sub(r"^# -{10,}.*?# -{10,}\n", "", routes_code,
                         flags=re.DOTALL | re.MULTILINE)
    routes_code = routes_code.strip()

    app_path = os.path.join(ROOT, "app.py")
    with open(app_path) as fh:
        app_code = fh.read()

    placeholder = "# FASTFLASK_AUTH_ROUTES_PLACEHOLDER"
    if placeholder not in app_code:
        _err("Placeholder not found in app.py – routes NOT inserted.")
        _print("      Manually paste the contents of "
               f".dev/auth_{method}/auth_routes.py into app.py")
        return

    new_code = app_code.replace(placeholder, routes_code)
    with open(app_path, "w") as fh:
        fh.write(new_code)
    _ok("Auth routes inserted into app.py")


# ---------------------------------------------------------------------------
# Step 4 – build .env
# ---------------------------------------------------------------------------

def build_env(method: str) -> None:
    _section("Environment variables  (.env)")

    lines: list[str] = []

    # --- DB ---
    _print(f"\n{C}Supabase setup{R}")
    _print("  Go to https://supabase.com/dashboard and open your project.")
    _print("  Click  Connect  →  Transaction Pooler  and copy the URL.\n")

    db_url_template = _ask_line("Paste the Supabase transaction pooler URL "
                                "(contains [YOUR-PASSWORD])")

    if "[YOUR-PASSWORD]" in db_url_template:
        db_pwd_raw = _ask_line("Supabase database password", hidden=True)
        db_pwd_enc = urllib.parse.quote(db_pwd_raw, safe="")
        db_url     = db_url_template.replace("[YOUR-PASSWORD]", db_pwd_enc)
    else:
        # user already substituted the password manually
        db_url = db_url_template

    lines.append(f"DB_URL={db_url}")
    _ok("DB_URL set")

    # --- secrets ---
    secret_key      = secrets.token_hex(32)
    encoding_secret = secrets.token_hex(32)
    lines.append(f"SECRET_KEY={secret_key}")
    lines.append(f"ENCODING_SECRET={encoding_secret}")
    _ok("SECRET_KEY generated")
    _ok("ENCODING_SECRET generated")

    # --- session length ---
    _print(f"\n{C}Session length{R}")
    session_raw = _ask_line("How many days should login sessions last? "
                             "[default: 7]")
    try:
        session_days = int(session_raw)
    except ValueError:
        session_days = 7
    lines.append(f"SESSION_LENGTH={session_days}")
    _ok(f"SESSION_LENGTH={session_days}")

    # --- Google credentials ---
    if method in ("google", "both"):
        _print(f"\n{C}Google OAuth credentials{R}")
        _print("  Make sure you have downloaded client_secret*.json from the")
        _print("  Google Cloud Console and placed it somewhere in this repo.\n")

        try:
            # run from project root so glob finds the file
            orig_dir = os.getcwd()
            os.chdir(ROOT)
            from create_env import extract_google_creds   # type: ignore

            # write to a temp buffer then add to our lines list
            tmp_env = os.path.join(ROOT, ".env.tmp_google")
            extract_google_creds(env_path=tmp_env)
            with open(tmp_env) as fh:
                lines.extend(fh.read().splitlines())
            os.remove(tmp_env)
        finally:
            os.chdir(orig_dir)

        redirect_uri = _ask_line(
            "Google redirect URI [default: http://localhost:8080/oauth2callback]"
        )
        if not redirect_uri:
            redirect_uri = "http://localhost:8080/oauth2callback"
        lines.append(f"GOOGLE_REDIRECT_URI={redirect_uri}")
        _ok(f"GOOGLE_REDIRECT_URI={redirect_uri}")

    # --- write ---
    _write_env(lines)


def _write_env(lines: list[str]) -> None:
    """Merge new lines into .env (overwrite existing keys, add new ones)."""
    existing: dict[str, str] = {}

    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as fh:
            for line in fh:
                line = line.rstrip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    existing[k.strip()] = v.strip()

    for line in lines:
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            existing[k.strip()] = v.strip()

    with open(ENV_PATH, "w") as fh:
        for k, v in existing.items():
            fh.write(f"{k}={v}\n")

    _ok(f".env written  ({len(existing)} keys)")


# ---------------------------------------------------------------------------
# Step 5 – requirements.txt
# ---------------------------------------------------------------------------

_BASE_REQUIREMENTS = """\
Flask==3.1.1
Flask-Limiter==3.12
python-dotenv==1.1.0
SQLAlchemy==2.0.41
psycopg2-binary==2.9.10
argon2-cffi==25.1.0
gunicorn==20.1.0
"""

_GOOGLE_REQUIREMENTS = """\
google-auth==2.41.1
google-auth-oauthlib==1.2.2
google-auth-httplib2==0.2.0
google-api-python-client==2.184.0
"""


def write_requirements(method: str) -> None:
    _section("requirements.txt")
    content = _BASE_REQUIREMENTS
    if method in ("google", "both"):
        content += _GOOGLE_REQUIREMENTS

    req_path = os.path.join(ROOT, "requirements.txt")
    with open(req_path, "w") as fh:
        fh.write(content)
    _ok("requirements.txt written")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _print(f"\n{B}{C}FastFlask  –  setup wizard{R}\n")
    _print("This script sets up authentication for your Flask project.")
    _print("Run it once from the project root directory.\n")

    if not _ask_yn("Continue?"):
        _print("Aborted.")
        sys.exit(0)

    method = choose_auth()
    copy_auth_files(method)
    patch_app(method)
    build_env(method)
    write_requirements(method)

    _section("Done")
    _print(f"""
{G}{B}FastFlask is ready!{R}

Next steps:
  1.  Create a virtual environment:
        python -m venv .venv && source .venv/bin/activate

  2.  Install dependencies:
        pip install -r requirements.txt

  3.  Run the app:
        python app.py

  4.  Before going to production:
        - Set  secure=True  on all  response.set_cookie()  calls in app.py
        - Set  debug=False  in app.py
        - Add your domain to GOOGLE_REDIRECT_URI (Google auth only)
""")


if __name__ == "__main__":
    main()

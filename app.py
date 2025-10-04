import os
from flask import *
from dotenv import load_dotenv

from src.database import *
import src.google_auth as google_auth
from src.random_string_gen import generate_token

load_dotenv()

SESSION_LENGTH = int(os.environ.get('SESSION_LENGTH') or 7)

app = Flask(__name__)

def get_current_user_id():
    token = request.cookies.get("token")
    token_to_user_id(token)


@app.route("/")
def landingpage():
    return render_template("landingpage.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/home")
def home():

    return render_template("home.html", profile_picture = profile_picture)

# APIs

@app.route("/api/register_with_google")
def register_api():
    authorization_url = google_auth.init_oauth_flow()
    return redirect(authorization_url)

@app.route("/api/log-in_with_google")
def login_api():
    authorization_url = google_auth.init_oauth_flow()
    return redirect(authorization_url)

@app.route("/oauth2callback")
def callback():
    code = request.args.get('code')
    if code:
        try:
            credentials = google_auth.handle_oauth_callback(code)
            user_info = google_auth.get_user_info(credentials)
            
            user_id = new_user(user_info)

            ip = request.remote_addr
            token = generate_token()
            expiry = datetime.utcnow() + timedelta(days= SESSION_LENGTH)
            user_agent = request.headers.get('User-Agent')


            response = make_response('Login successfull')
            response.set_cookie("token",token, expires= expiry )#, secure=True
            save_cookie(user_id,token,expiry,ip,user_agent)

            return response
        except Exception as e:
            return f"Error during authentication: {str(e)}", 400
    else:
        return "Authorization failed", 400



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=True) #set to false
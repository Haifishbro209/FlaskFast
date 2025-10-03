import os
from flask import *
from dotenv import load_dotenv
import src.google_auth as google_auth

load_dotenv()

app = Flask(__name__)

@app.route("/")
def landingpage():
    return render_template("landingpage.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

# APIs

@app.route("/api/register_with_google")
def register_api():
    authorization_url = google_auth.init_oauth_flow()
    return redirect(authorization_url)

@app.route("/api/log-in_with_google")
def login_api():
    authorization_url = google_auth.init_oauth_flow()
    return redirect(authorization_url)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=True) #set to false
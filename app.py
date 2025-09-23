import os
from flask import *
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/")
def landingpage():
    return render_template("landingpage.html")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=True) #set to false
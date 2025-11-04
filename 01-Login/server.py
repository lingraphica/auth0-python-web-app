"""Python Flask WebApp Auth0 integration example
"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)


# Controllers API
@app.route("/callback", methods=["GET", "POST"])
def callback():
    print("=" * 50)
    print("🔍 CALLBACK ROUTE HIT!")
    print("=" * 50)
    
    try:
        token = oauth.auth0.authorize_access_token()
        print("✅ Token received:", token)
        
        session.permanent = True
        session["user"] = token
        session["access_token"] = token.get("access_token")
        
        print("✅ Session user set:", session.get("user") is not None)
        
    except Exception as e:
        print("❌ ERROR in callback:", str(e))
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500
    
    return redirect("/")


@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
        access_token=session.get("access_token"),
    )


@app.route("/login")
def login():
    # ← ADD AUDIENCE PARAMETER HERE - This is critical!
    audience = env.get("AUTH0_AUDIENCE")
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True),
        audience=audience  # ← Add this!
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
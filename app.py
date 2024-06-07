from flask import Flask, jsonify, url_for, render_template, redirect, request, session, flash
from flask_login import login_required
from flask_session import Session
from flask_caching import Cache
from urllib.parse import urlencode, quote_plus
import datetime
import pytz
import sqlite3
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
from define_tables import *
 

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', '2b9a31c7d0f2c5e2a7c907a7c5e1d5e2')

#Configurations
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300,
    "SESSION_PERMANENT": False,
    "SESSION_TYPE": "filesystem",
    "AUTH0_CLIENT": os.getenv('AUTH0_CLIENT_ID'),
    "AUTHO0_CLIENT_SECRET": os.getenv('AUTH0_CLIENT_SECRET'),
    "AUTHO0_DOMAIN": os.getenv('AUTH0_DOMAIN')
}
app.config.from_mapping(config)

cache = Cache(app)
Session(app)
oauth = OAuth(app, cache=cache)
auth0 = oauth.register(
    'auth0',
    client_id=os.getenv('AUTH0_CLIENT_ID'),
    client_secret= os.getenv('AUTH0_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid profile email',
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

#-- DATABASE --
connection = sqlite3.connect("budget.db")
db = connection.cursor()


@app.route('/')
@cache.cached(timeout=50) 
def home():
    user = session.get('user')
    return render_template("layout.html", session=user)



@app.route('/login')
def login():
    render_template("login.html")
    return auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )
      
    
@app.route('/callback', methods=["GET", "POST"]) #because this is only user id if we want to add gmail then oaut = register('google')
def callback():
        token = auth0.authorize_access_token()
        if session["user"]:
            session["user"] = token
            nickname = session["user"]["userinfo"]["nickname"]
            sub = session["user"]["userinfo"]["sub"]
            print(f'{type(nickname)} and {type(sub)}')
            db.execute("INSERT INTO user (NickName, Auth0) VALUES (?, ?)", nickname, sub)
            return redirect("/")
        else: 
            return "No user allowed"

@app.route('/transaction', methods =["GET","POST"])
@login_required
def transaction():
    if request.method == "GET":
        return render_template("transaction.html")
    else:
        return redirect('/overview')


@app.route('/overview') #here they see there income, expenses, and a small bubble that mentions budget 


@app.route('/logout')
def logout():
    session.clear()
    logout_url = (
        "https://" + app.config["AUTH0_DOMAIN"]
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": app.config['AUTH0_CLIENT_ID'],
            },
            quote_via=quote_plus,
        )
    )
    print(f"Logout URL: {logout_url}")  # Debug print
    return redirect(logout_url)
        

if __name__ == "__main__":
    app.run(debug=True)

'''
-- typical response from user = token.json()
{ {'user': {'userinfo': {'sub': 'auth0|665dea8b7ab006f6e2700caa', 
'nickname': 'batoul.daou', 'name': 'batoul.daou@tuhh.de', 
'picture': 'https://s.gravatar.com/avatar/53ef17278efa7eb45b43d9555925da8f?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fba.png',
'updated_at': '2024-06-03T16:49:48.370Z', 
'email': 'batoul.daou@tuhh.de', 
'email_verified': True}}}>


'''
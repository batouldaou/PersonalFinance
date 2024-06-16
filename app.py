from flask import Flask, jsonify, url_for, render_template, redirect, request, session, flash, Response
from flask_login import login_required, LoginManager, UserMixin, login_user
from flask_session import Session
from flask_caching import Cache
from urllib.parse import urlencode, quote_plus
import sqlite3
import datetime 
import pytz
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
from create_tables import CreateTables
from forms import TransactionForm, BudgetForm
import pandas
import matplotlib.pyplot as plt
 

load_dotenv()
app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv('FLASK_SECRET_KEY')
login_manager = LoginManager()


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
login_manager.init_app(app)
login_manager.login_view = 'login'
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
connection = sqlite3.connect("budget.db", check_same_thread=False)
connection.row_factory = sqlite3.Row
db = connection.cursor()
create_table = CreateTables(db)
create_table.initialize_tables()


#Define the creation of the tables
class User(UserMixin):
    def __init__(self, id, auth0):
        self.id = id
        self.auth0 = auth0

@app.route('/')
def home():
    user = session.get('user')
    if user:
        print(f'session:{user}')
    else:
        print ('no user')
    return render_template("layout.html", session=user) #later change it to overview or something else with title


@app.route('/login')
def login():
    return auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )
    

@login_manager.user_loader
def load_user(user_id):
    user = db.execute("SELECT id, auth0 FROM user WHERE id = ?", (user_id,)).fetchone()
    if user:
        return User(id=user[0], auth0=user[1])
    return None
      
    
@app.route('/callback', methods=["GET", "POST"]) #because this is only user id if we want to add gmail then oaut = register('google')
def callback():
        try:
            token = auth0.authorize_access_token()
            session["user"] = token
            if "user" in session:
                nickname = session["user"]["userinfo"]["nickname"]
                sub = session["user"]["userinfo"]["sub"]
                print(f'{type(nickname)} and {type(sub)}')
                
                 # Fetch users from the database
                users = db.execute("SELECT id FROM user WHERE auth0 = ?", (sub,)).fetchone()            
                if not users:  # Check if the user is not in the database
                    db.execute("INSERT INTO user (auth0, nick_name) VALUES (?, ?)", (sub, nickname))
                    connection.commit()
                user_obj = User(id=users[0], auth0=sub)
                login_user(user_obj)
                print('redirecting to home')
                return redirect(url_for('home')) # Return a 200 OK status if user exists
            else: 
                return "No user allowed", 401  # Return a 401 Unauthorized status           
        except Exception as e:
        # Log the error and return an error response
            print(f"An error occurred: {e}")
            return "Internal Server Error", 500  # Return a 500 Internal Server Error status
    
            
@app.route('/category_manage', methods =['GET', 'POST'])
@login_required
def category_manage():
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0 =?", (auth0, )).fetchone()
    if request.method == 'POST':
        category_name = request.form.get("category_name") # Error handled with required attribute
        action = request.form.get("submit")
        category_id = request.form.get("category_id")
        if action == "add":        
            if category_name:
                try:
                    cursor = db.execute("INSERT INTO category (category_name, user_id) VALUES (?,?) ", (category_name, user_id[0]))
                    connection.commit()
                    new_id = cursor.lastrowid
                    new_category = {
                        'id': new_id,
                        "name": category_name                
                    }
                    return jsonify(new_category) 
                except Exception as e:
                    return  jsonify({"error": str(e)})  
        elif action == "delete":
            if category_id:
               try:
                    print(f"Attempting to delete category_id: {category_id} for user_id: {user_id[0]}")
                    db.execute("DELETE FROM category WHERE id = ? AND user_id = ?", (category_id, user_id[0]))
                    connection.commit()
                    return jsonify(success=True)
               except Exception as e:
                    print(f"Error deleting category: {e}")
                    return jsonify(success=False, error=str(e))
        elif action =="edit":
            if category_id and category_name:
                try:
                    print(f"Attempting to edit category_id: {category_id} to new name: {category_name} for user_id: {user_id[0]}")
                    db.execute("UPDATE category SET category_name = ? WHERE id = ? AND user_id = ?", (category_name, category_id, user_id[0]))
                    connection.commit()
                    return jsonify(id=category_id, name=category_name)
                except Exception as e:
                    print(f"Error editing category: {e}")
                    return jsonify(success=False, error=str(e))                
    categories_data = db.execute("SELECT id, category_name FROM category WHERE user_id = ?", (user_id[0],))                
    categories_list = [dict(row) for row in categories_data]
    return render_template('category_manage.html', categories_list=categories_list)

             

@app.route('/transactions', methods =["GET","POST"])
@login_required
def transactions():
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0=?", (auth0,)).fetchone()[0]
    category_name_query = db.execute("SELECT category_name FROM category WHERE user_id=?", (user_id,))
    category_name = [dict(row) for row in category_name_query]
    form = TransactionForm(category_name)
    
    if request.form.get("submit") == "delete":
        transaction_id = request.form.get("transaction_id")
        db.execute("DELETE FROM transactions WHERE id =? AND user_id = ?", (transaction_id, user_id))
        connection.commit()
        return jsonify(success=True)
        
    if request.method == "GET":
        trans_data = db.execute('''SELECT *
                                    FROM transactions 
                                    JOIN category 
                                    ON category.user_id = transactions.user_id 
                                        AND category.id = transactions.category_id 
                                    WHERE transactions.user_id = ?''', (user_id,)).fetchall()
        list_transactions = [dict(row) for row in trans_data]       
        return render_template('transactions.html', form=form, list_trans=list_transactions)
    else:                        
        amount = float(form.amount.data)
        type = form.type.data
        category = form.category.data
        category_id = db.execute("SELECT id FROM category WHERE category_name = ?", (category,)).fetchone()
        date = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime("%Y-%m-%d %H:%M:%S")
        cursor = db.execute('''
                    INSERT INTO transactions (user_id, amount,                                                    
                                            category_id, date, type)
                                    VALUES (?,?,?,?,?)
                    
                ''', (user_id, amount, category_id[0], date, type))
        connection.commit()
        new_id = cursor.lastrowid
        new_id = {
            'id':new_id,
            'amount': amount,
            'category_name': category,
            "type": type,
            "date": date      
        }
        return jsonify(new_id)


@app.route('/budget', methods= ['GET', 'POST']) #here they see there income, expenses, and a small bubble that mentions budget 
@login_required
def budget():
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0=?", (auth0,)).fetchone()[0]
    category_name_query = db.execute("SELECT category_name FROM category WHERE user_id=?", (user_id,))
    category_name = [dict(row) for row in category_name_query]
    form = BudgetForm(category_name)
    list_budget = db.execute('''
                                    SELECT budget.id, budget_percent, budget_amount, category_name
                                        FROM budget
                                        JOIN category 
                                        ON category.id = budget.category_id 
                                            AND budget.user_id = category.user_id
                                        WHERE budget.user_id = ?
                                    ''', (user_id,))
    list_budget = [dict(row) for row in list_budget]
    
    if request.method == 'GET':        
        return render_template('budget.html', form=form, list_budget=list_budget)
    else:
        action = request.form.get("submit")
        if action in ['add', 'edit'] :
            # Get income
            total_income = db.execute('''
                                        SELECT SUM(amount) 
                                            FROM transactions 
                                            WHERE type = ? 
                                                AND user_id = ?                           
                                    ''', ('Income', user_id)).fetchone()[0]
            if not total_income:
                flash("Please add income value first.")
                return jsonify({'error': "Please add income value first."})
            budget_percent = float(form.percentage.data)
            budget_amount = (budget_percent/100)*total_income        
            if action == "add":
                max_percent = 100
                total_percent = db.execute("SELECT SUM(budget_percent) FROM budget WHERE user_id=?", (user_id,)).fetchone()[0]
                if (total_percent+budget_percent) > max_percent:
                    flash("All the income is divided")
                    return jsonify({'error': "All the income is divided"})
                category_name = form.category.data
                category_id = db.execute("SELECT id FROM category WHERE category_name =?", (category_name, )).fetchone()
                cursor = db.execute('''
                                        INSERT INTO budget (user_id, budget_percent, budget_amount, category_id)
                                            VALUES (?,?,?,?)
                                    ''', (user_id, budget_percent, budget_amount, category_id[0]))
                connection.commit()
                new_id = cursor.lastrowid
                new_id = {
                    'budget_percent':budget_percent,
                    'budget_amount': budget_amount,
                    'category_name': category_name
                }
                return jsonify(new_id)
            else:
                budget_id = request.form.get("budget_id")
                db.execute('''
                            UPDATE budget
                            SET budget_percent = ?, budget_amount = ?
                            WHERE id = ? AND user_id = ?
                        ''', (budget_percent, budget_amount, budget_id, user_id))
                connection.commit()
                updated_entry = {
                    'id': budget_id,
                    'budget_percent': budget_percent,
                    'budget_amount': budget_amount
                }
                return jsonify(updated_entry)                    
        elif request.form.get("submit") == "delete":
            budget_id = request.form.get("budget_id")
            db.execute("DELETE FROM budget WHERE id = ? AND user_id = ?", (budget_id, user_id))
            connection.commit()
            return jsonify({'success': True})          
        
   


@app.route('/logout')
def logout():
    session.clear()
    logout_url = (
        "https://" + os.getenv("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": os.getenv('AUTH0_CLIENT_ID'),
            },
            quote_via=quote_plus,
        )
    )
    print(f"Logout URL: {logout_url}")  # Debug print
    return redirect(logout_url)
        

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
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
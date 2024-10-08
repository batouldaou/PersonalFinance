from flask import Flask, jsonify, url_for, render_template, redirect, request, session, flash, Response
from flask_login import login_required, LoginManager, UserMixin, login_user
from flask_session import Session
from flask_caching import Cache
from urllib.parse import urlencode, quote_plus
import sqlite3
from datetime import datetime 
import pytz
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv
from create_tables import CreateTables
from forms import TransactionForm, BudgetForm, CategoryForm
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from functions_needed import get_budget_data, get_transaction_data
from dateutil.relativedelta import relativedelta

 

load_dotenv()
app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv('FLASK_SECRET_KEY')
login_manager = LoginManager()
engine = create_engine('sqlite:///budget.db')

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
        auth0 = session['user']['userinfo']['sub']
        user_id = db.execute("SELECT id FROM user WHERE auth0 =?", (auth0, )).fetchone()[0]
        transactions_record = db.execute('''
                                         SELECT transactions.date, transactions.amount, transactions.type, category.category_name
                                                FROM transactions
                                                JOIN category
                                                ON transactions.category_id = category.id
                                                WHERE transactions.user_id = ?
                                                LIMIT 3
                                         ''',(user_id,)).fetchall()
        total_income = db.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type=?", (user_id, 'Income')).fetchone()[0]
        total_expense = db.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND type=?", (user_id, 'Expense')).fetchone()[0]
        total_balance = total_income - total_expense
        transactions = [dict(row) for row in transactions_record]
        return render_template("home.html", session=user, transactions=transactions, total_expenses=total_expense, total_balance=total_balance, total_income=total_income) 
    else:
        print ('no user')
        return render_template("home.html", session=user)
    


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


@app.route('/profile')
@login_required
def profile():
    user_info = session["user"]["userinfo"]
    auth0 = user_info['sub']
    nickname = user_info["nickname"]
    user_picture = user_info["picture"]
    email = user_info["email"]
    user = {'name':nickname, 'email': email, 'username': nickname, 'picture': user_picture}
    return render_template("profile.html", user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():   
    user_info = session["user"]["userinfo"]
    nickname = user_info["nickname"]
    user_picture = user_info["picture"]
    email = user_info["email"]
    user_data = {'name':nickname, 'email': email, 'username': nickname, 'picture': user_picture}
    if request.method == 'POST':
        user_info["nickname"] = request.form['name']
        user_info["email"] = request.form['email']
        user_info["nickname"] = request.form['username']
        flash('Profile updated successfully')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user_data)
    
    
    
@app.route('/category_manage', methods =['GET', 'POST'])
@login_required
def category_manage():
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0 =?", (auth0, )).fetchone()
    form = CategoryForm()
    if request.method == 'POST':
        category_name = form.category_name.data # Error handled with required attribute
        action = request.form.get("submit")
        category_id = request.form.get("category_id")
        type = form.type.data

        if action == "Add":        
            if category_name:
                try:
                    cursor = db.execute("INSERT INTO category (category_name, user_id, type) VALUES (?,?,?) ", (category_name, user_id[0], type))
                    connection.commit()
                    new_id = cursor.lastrowid
                    new_category = {
                        'id': new_id,
                        "name": category_name ,
                        "type": type              
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
                    return jsonify(success=False, error=str(e)) # What we need to do to understand why budget doesnt save
        elif action =="edit":
            if category_id and category_name:
                try:
                    print(f"Attempting to edit category_id: {category_id} to new name: {category_name} for user_id: {user_id[0]}")
                    db.execute("UPDATE category SET category_name = ?, type = ? WHERE id = ? AND user_id = ?", (category_name, type, category_id, user_id[0]))
                    connection.commit()
                    return jsonify(id=category_id, name=category_name, type=type)
                except Exception as e:
                    print(f"Error editing category: {e}")
                    return jsonify(success=False, error=str(e))                
    categories_data = db.execute("SELECT id, category_name, type FROM category WHERE user_id = ?", (user_id[0],))                
    categories_list = [dict(row) for row in categories_data]
    return render_template('category_manage.html', categories_list=categories_list, form=form)


@app.route('/get_categories', methods=['GET'])
@login_required
def get_categories():
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0=?", (auth0,)).fetchone()[0]
    selected_type = request.args.get('type')
    if selected_type:
        categories_query = db.execute("SELECT id, category_name FROM category WHERE user_id = ? AND type = ?", (user_id, selected_type)).fetchall()
        categories = [dict(row) for row in categories_query]
        return jsonify({'categories': categories})
    return jsonify({'categories': []})
                

@app.route('/transactions', methods =["GET","POST"])
@login_required
def transactions():  
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0=?", (auth0,)).fetchone()[0]
    category_name_query = db.execute("SELECT category_name FROM category WHERE user_id = ? ", (user_id,)).fetchall()
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
    type = 'Expense'
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0=?", (auth0,)).fetchone()[0]
    all_category_name_query = db.execute("SELECT category_name FROM category WHERE user_id=? AND type= ?", (user_id, type)).fetchall() # the complete category list
    categories_with_budget_query = db.execute("SELECT category_name FROM category, budget WHERE category.id = budget.category_id AND budget.user_id =?", (user_id,)).fetchall() # the categories with budget set
    
    all_category_names = {row['category_name'] for row in all_category_name_query}
    categories_with_budget = {row['category_name'] for row in categories_with_budget_query}
    categories_without_budget = [{'category_name': name} for name in all_category_names if name not in categories_with_budget]

    form = BudgetForm(categories_without_budget)    
    list_budget = db.execute('''
                                    SELECT budget.id, budget_percent, budget_amount, category_name
                                        FROM budget
                                        JOIN category 
                                        ON category.id = budget.category_id 
                                            AND budget.user_id = category.user_id
                                        WHERE budget.user_id = ? AND type=?
                                    ''', (user_id,type))
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
            
            if action == "add":
                budget_percent = float(form.percentage.data)
                budget_amount = (budget_percent/100)*total_income 
                  
                max_percent = 100
                total_percent = db.execute("SELECT SUM(budget_percent) FROM budget WHERE user_id=?", (user_id,)).fetchone()[0]
                total_percent = 0 if total_percent is None else total_percent
                if (total_percent+budget_percent) > max_percent:
                    flash("All the income is divided")
                    return jsonify({'error': "All the income is divided"})
                
                category_name = form.category.data
                category_id = db.execute("SELECT id FROM category WHERE category_name =?", (category_name, )).fetchone()
                
                # Check if budget for that category exists
                budget_category_exist = db.execute("SELECT id FROM budget WHERE category_id = ?", (category_id)).fetchall()
                if budget_category_exist:
                    flash("Budget exists for that category")
                    return jsonify({'error': "Budget exists for that category"})
                else:
                    cursor = db.execute('''
                                            INSERT INTO budget (user_id, budget_percent, budget_amount, category_id)
                                                VALUES (?,?,?,?)
                                        ''', (user_id, budget_percent, budget_amount, category_id[0]))
                    connection.commit()
                    new_budget = cursor.lastrowid
                    new_budget = {
                        'budget_percent':budget_percent,
                        'budget_amount': budget_amount,
                        'category_name': category_name
                    }
                    categories_with_budget.add(category_name)
                    categories_without_budget = [{'category_name': name} for name in all_category_names if name not in categories_with_budget]

                    return jsonify(new_budget=new_budget, categories_without_budget=categories_without_budget)
                    
            else:
                budget_percent = float(request.form.get("budget_percent"))
                budget_amount = (budget_percent/100)*total_income    
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
            category_name_query = db.execute("SELECT category.category_name FROM category, budget WHERE budget.id = ? AND category.id = budget.category_id", (budget_id,)).fetchone()
            category_name = category_name_query['category_name'] if category_name_query else None
            db.execute("DELETE FROM budget WHERE id =? AND user_id = ?", (budget_id, user_id))
            connection.commit()
            if category_name:
                categories_with_budget.discard(category_name)
                categories_without_budget = [{'category_name': name} for name in all_category_names if name not in categories_with_budget]
                return jsonify(success=True, categories_without_budget=categories_without_budget)   
            return jsonify(success=True)
    

@app.route('/api/budget/<int:user_id>')
def api_budget(user_id):
    df_budget = get_budget_data(user_id, engine)
    return jsonify(df_budget.to_dict(orient='records'))


@app.route('/api/transactions/<int:user_id>')
def api_transactions(user_id):
    df_merged = get_transaction_data(user_id,engine)
    return jsonify(df_merged.to_dict(orient='records'))


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/overview')
def overview():
    '''
        View overview data per month
    '''
    auth0 = session['user']['userinfo']['sub']
    user_id = db.execute("SELECT id FROM user WHERE auth0=?", (auth0,)).fetchone()[0]
    first_transaction_record = db.execute("SELECT date FROM transactions WHERE user_id = ? ORDER BY date ASC ", (user_id,)).fetchone()[0]
    first_transaction_datetime = datetime.strptime(first_transaction_record, '%Y-%m-%d %H:%M:%S')
    first_transaction_month = first_transaction_datetime.strftime('%Y-%m-%d')
    current_datetime = datetime.now()
    current_month = current_datetime.strftime('%Y-%m-%d')

    month_difference = -first_transaction_datetime.month + current_datetime.month 
        # Get the overview records from transactions 
    overview_records = db.execute('''
                                    SELECT category.type, category.category_name,
                                            SUM(transactions.amount) AS amount
                                        FROM transactions, category
                                        WHERE category.id = transactions.category_id
                                            AND transactions.user_id = category.user_id
                                            AND transactions.user_id = ?
                                        GROUP BY category.category_name                                      
                                    ''',(user_id,)).fetchall()
    if month_difference >=1:
        current_month = (current_datetime + relativedelta(months=1)).replace(day=1).strftime('%Y-%m-%d')
        # Check if it works then delete from transactions
        for record in overview_records:
            db.execute('''
                INSERT INTO monthly_overview (user_id, type, category_name, amount, month)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, type, category_name, month) DO UPDATE SET amount = excluded.amount
            ''', (user_id, record['type'], record['category_name'], record['amount'], current_month))
            connection.commit()
            
        db.execute('''
            DELETE FROM transactions
            WHERE user_id = ?
            AND date >= ?
            AND date < ?
        ''', (user_id, first_transaction_month, current_month))
    
    income_records = db.execute('''
        SELECT month, SUM(amount) as total_amount
        FROM monthly_overview
        WHERE user_id = ? AND type = ?
        GROUP BY month
        ORDER BY month
    ''', (user_id,'Income')).fetchall()
    income_records = [dict(row) for row in income_records]

    expense_records = db.execute('''
        SELECT month, SUM(amount) as total_amount
        FROM monthly_overview
        WHERE user_id = ? AND type = ?
        GROUP BY month
        ORDER BY month
    ''', (user_id,'Expense')).fetchall()
    expense_records = [dict(row) for row in expense_records]

    income_categories = db.execute('''
        SELECT category_name, SUM(amount) as amount
        FROM monthly_overview
        WHERE user_id = ? AND type = ?
        GROUP BY category_name
    ''', (user_id,'Income')).fetchall()
    income_categories = [dict(row) for row in income_categories]
    
    expense_categories = db.execute('''
        SELECT category_name, SUM(amount) as amount
        FROM monthly_overview
        WHERE user_id = ? AND type = ?
        GROUP BY category_name
    ''', (user_id,'Expense')).fetchall()
    expense_categories = [dict(row) for row in expense_categories]

    return render_template("fake_overview.html", 
                           income_records=income_records, 
                           expense_records=expense_records,
                           income_categories=income_categories,
                           expense_categories=expense_categories)
        
    

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


#Define the creation of the tables
def create_users(db):
    db.execute( ''' CREATE TABLE IF NOT EXISTS user  (
            auth0 TEXT PRIMARY KEY UNIQUE,
            nick_name TEXT NOT NULL,
            current_cash NUMERIC NOT NULL DEFAULT 0)
           ''')



def create_transaction(db):
    db.execute('''
                CREATE TABLE IF NOT EXISTS transaction (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    amount REAL,
                    category_id INTEGER,
                    date DATETIME,
                    type TEXT,
                    FOREIGN KEY (user_id) REFERENCES user(auth0),
                    FOREIGN KEY (category_id) REFERENCES category(id)
                )
           ''')


def create_category(db):
    db.execute(" CREATE TABLE IF NOT EXISTS category (id INTEGER PRIMARY KEY AUTOINCREMENT, category_name TEXT NOT NULL)")


def create_budget(db):
    db.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES user(auth0),
                FOREIGN KEY (category_id) REFERENCES category(id)
                
            )
           ''')


def create_goals(db):
    db.execute('''
                CREATE TABLE IF NOT EXISTS goal  (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    goal_name TEXT,
                    goal_amount REAL,
                    set_contribution REAL,
                    FOREIGN KEY (user_id) REFERENCES user(auth0)
                )
               ''')
    
    
def create_overview(db):
    db.execute('''CREATE TABLE IF NOT EXITS overview(
                    user_id TEXT NOT NULL,
                    transaction_id INTEGER,
                    budget_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES user(auth0),
                    FOREIGN KEY (budget_id) REFERENCES budget(id),
                    FOREIGN KEY (transaction_id) REFERENCES transaction(id)
                    )
               ''')
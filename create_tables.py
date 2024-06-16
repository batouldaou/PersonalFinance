       
        
class CreateTables():
    '''
        No physical meaning - created to make life easier
    '''
    def __init__(self, db, *args) -> None:
        self.db = db
        if args:
            self.tables = list(args)
        else:
            self.tables = None


    def initialize_tables(self):
        self.create_users()
        self.create_category()
        self.create_transactions()
        self.create_budget()      
        self.create_goals()
        self.create_overview()
        
    
        
    def create_users(self):
        self.db.execute( ''' 
                        CREATE TABLE IF NOT EXISTS user  (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    auth0 TEXT  UNIQUE,
                                    nick_name TEXT NOT NULL,
                                    current_cash NUMERIC NOT NULL DEFAULT 0
                                    )
                        ''')


    def create_category(self):
        self.db.execute('''
                        CREATE TABLE IF NOT EXISTS category (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                        category_name TEXT NOT NULL UNIQUE,
                                        user_id INTEGER NOT NULL,
                                        type TEXT,
                                        FOREIGN KEY (user_id) REFERENCES user(id))
                        ''')
       
    def create_transactions(self):
        self.db.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        amount REAL,
                        category_id INTEGER,
                        date TEXT,
                        type TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user(id),
                        FOREIGN KEY (category_id) REFERENCES category(id)
                        )
                        ''')      
    

    def create_budget(self):
        self.db.execute('''
                CREATE TABLE IF NOT EXISTS budget (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    category_id INTEGER,
                    budget_percent REAL,
                    budget_amount REAL,
                    FOREIGN KEY (user_id) REFERENCES user(id),
                    FOREIGN KEY (category_id) REFERENCES category(id)             
                    )
                    ''')


    def create_goals(self):
        self.db.execute('''
                    CREATE TABLE IF NOT EXISTS goal  (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        goal_name TEXT,
                        goal_amount REAL,
                        set_contribution REAL,
                        FOREIGN KEY (user_id) REFERENCES user(id)
                        )
                        ''')
        
        
    def create_overview(self):
        self.db.execute('''
                    CREATE TABLE IF NOT EXISTS overview(
                        user_id INTEGER NOT NULL,
                        transactions_id INTEGER,
                        budget_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES user(id),
                        FOREIGN KEY (budget_id) REFERENCES budget(id),
                        FOREIGN KEY (transactions_id) REFERENCES transactions(id)
                        )
                        ''')
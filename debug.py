from dotenv import load_dotenv
import os
from create_tables import CreateTables
import sqlite3
'''
load_dotenv()
auth0_domain = os.getenv('AUTH0_DOMAIN')
if auth0_domain is None:
    print("AUTH0_DOMAIN not set in environment variables")
else:
    print(f"AUTH0_DOMAIN: {auth0_domain}")
'''

connection = sqlite3.connect("budget.db")
db = connection.cursor()
create_table = CreateTables(db)
create_table.initialize_tables()
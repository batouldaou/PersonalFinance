from dotenv import load_dotenv
import os
from create_tables import CreateTables
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
'''
load_dotenv()
auth0_domain = os.getenv('AUTH0_DOMAIN')
if auth0_domain is None:
    print("AUTH0_DOMAIN not set in environment variables")
else:
    print(f"AUTH0_DOMAIN: {auth0_domain}")
'''

engine = create_engine('sqlite:///budget.db')
param ={'user_id': '1'}
df_budget = pd.read_sql('''SELECT * 
                    FROM budget 
                    JOIN category 
                    ON category.id = budget.category_id 
                    WHERE budget.user_id = ?
                 ''', engine, params=[param])
# inner join to drop the common things out abd it works
from flask import render_template
from sqlalchemy import create_engine
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


engine = create_engine('sqlite:///budget.db')
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


engine = create_engine('sqlite:///budget.db')
user_id = 1

def budget_pie_chart(user_id):
    type = 'Expense'
    df_budget = pd.read_sql('''SELECT budget.id AS budget_id, budget.user_id,  budget_percent, category_name
                        FROM budget 
                        JOIN category 
                        ON category.id = budget.category_id 
                        WHERE budget.user_id = ? AND category.type = ?
                    ''', engine, params=(user_id, type))

    df_budget = df_budget.set_index('category_name') # So we get category name and there respective budget_percent

    def absolute_value(val):
        a = int(val/100.*df_budget['budget_percent'].sum())
        return f'{a}%'

    # Plot the pie chart with actual values
    df_budget.plot.pie(y='budget_percent', figsize=(5, 5), autopct=absolute_value)
    plt.ylabel('') # hides y label
    plt.show()
    
    
def budget_track_bar(user_id):
    df_track = pd.read_sql(''' 
                            SELECT SUM(budget.budget_amount) AS budget_amount, category.category_name AS category_name
                            FROM budget
                            JOIN category
                            ON budget.category_id = category.id
                            WHERE budget.user_id = ?
                            GROUP BY category.category_name
                            
                           ''', engine, params=(user_id,))
    
    df_transac = pd.read_sql('''
                                SELECT SUM(transactions.amount) AS trans, category.category_name AS category_name
                                FROM transactions 
                                JOIN category
                                ON category.id = transactions.category_id
                                WHERE transactions.user_id = ? 
                                GROUP BY category.id
                                                                                      
                             ''', engine, params=(user_id,))
    df_merged = pd.merge(df_transac, df_track, on="category_name", how ="left")
    df_merged = df_merged.dropna()
    
    bar_width = 0.2
    categories = df_merged['category_name']
    budget = df_merged['budget_amount'].astype(int)
    transactions = df_merged['trans'].astype(int)

    # Setting positions for the bars on the x-axis
    r1 = range(len(categories))
    r2 = [x + bar_width for x in r1]
    fig, ax = plt.subplots()

    # Plot budget amounts
    ax.bar(r1, budget, color='b', width=bar_width, edgecolor='grey', label='Budget')

    # Plot transaction amounts with some offset to avoid overlap
    ax.bar(r2, transactions, color='g', width=bar_width, edgecolor='grey', label='Transactions')

    # Adding labels and title
    ax.set_xlabel('Category Names', fontweight='bold')
    ax.set_ylabel('Amount', fontweight='bold')
    ax.set_title('Budget and Transactions by Category')

    # Adding xticks
    ax.set_xticks([r + bar_width / 2 for r in range(len(categories))])
    ax.set_xticklabels(categories, rotation=45)

    # Adding legend
    ax.legend()

    plt.tight_layout()
    plt.show()
    
budget_track_bar(user_id)
budget_pie_chart(user_id)
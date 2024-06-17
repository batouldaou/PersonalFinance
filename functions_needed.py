import pandas as pd


def get_budget_data(user_id,engine):
    type = 'Expense'
    df_budget = pd.read_sql('''SELECT budget.id AS budget_id, budget.user_id,  budget_percent, category_name
                        FROM budget 
                        JOIN category 
                        ON category.id = budget.category_id 
                        WHERE budget.user_id = ? AND category.type = ?
                    ''', engine, params=(user_id, type))
    return df_budget



def get_transaction_data(user_id, engine):
    type = 'Expense'
    df_track = pd.read_sql(''' 
                            SELECT SUM(budget.budget_amount) AS budget_amount, category.category_name AS category_name
                            FROM budget
                            JOIN category
                            ON budget.category_id = category.id
                            WHERE budget.user_id = ? AND category.type = ?
                            GROUP BY category.category_name
                            
                           ''', engine, params=(user_id, type))
    
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
    return df_merged
'''
    Defines transaction forms 
'''
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import SubmitField, SelectField, DecimalField
from wtforms.validators import InputRequired, Length


class TransactionForm(FlaskForm):
    amount = DecimalField('Amount')
    category = SelectField('Category', [InputRequired()], choices=[])
    type = SelectField('Type', [InputRequired()], choices=[])
    submit = SubmitField('Add Transaction')
    
    
    def __init__(self, categories=None, *args):
        super(TransactionForm, self).__init__(*args)        
        self.type.choices = ['Income', 'Expense']
        if categories:
            self.category.choices = [category["category_name"] for category in categories]


class BudgetForm(FlaskForm):
    percentage = DecimalField('Percentage', [InputRequired()])
    category = SelectField('Category', [InputRequired()], choices = [])
    submit = SubmitField('Add Budget')
    
    def __init__(self, categories=None, *args):
        super(BudgetForm, self).__init__(*args)        
        if categories:
            self.category.choices = [category["category_name"] for category in categories]

    
    
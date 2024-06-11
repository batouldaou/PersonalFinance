'''
    Defines transaction forms 
'''
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import SubmitField, SelectField, DecimalField
from wtforms.validators import InputRequired, Length


class TransactionForms(FlaskForm):
    amount = DecimalField('Amount')
    #cateogry = SelectField('Category', [InputRequired()], choices=[])
    type = SelectField('Type', [InputRequired()], choices=[])
    submit = SubmitField('Add Transaction')
    
    
    def __init__(self, *args):
        super(TransactionForms, self).__init__(*args)
        #fself.category.choices = [category for category in args]
        self.type.choices = ['Income', 'Expense']
    
    
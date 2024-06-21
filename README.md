# Personal Finance Manager Web Application
#### Video Demo:  <URL HERE>
#### Description:


## Overview

A personal finance manager web application created with Flask on Python. The database is managed using SQLite3. The inspiration for this project comes from my boyfriend, who uses a personalized Excel sheet to track his spending across different categories. I aimed to create a smoother and more user-friendly solution for him.

## Features

### User Authentication

- **Sign-In**: Users are prompted to sign in. Authentication is handled through AUTH-0, ensuring secure sign-in.

### Categories

- **Customizable Categories**: Users can create, add, edit, and delete categories. Categories are added with two types: income and expense which helps to track the different categories of income (e.g., Jobs, Stocks, Side Hustles) and expenses for the user.

### Transactions

- **Add Transactions**: Users can add transactions by specifying the amount and the related category. The user can then delete the transaction, or edit the transaction category, type, or amount as they deem fit. 
- **Transaction Types**: Users select the type of transaction (income or expense), which updates the category list accordingly.


### Budget Management

- **Set Budgets**: Users can navigate to the budget page to set a budget for each expense category. User is allowed to set one budget per category more than that would induce an error. 
- **Budget Calculation**: Budgets are defined as a percentage of the total income, and the application calculates and displays the budget amounts. If the total percentage of the budget has reached 100, an error message would appear that "All the income is divided" and the user can no longer add more as that would mean the user has reached the full amount of their income. 
- **Edit Budgets**: Budgets can be modified, updated, or deleted as needed.

### Analysis

- **Visual Analysis**: The analysis page visually represents budget distribution across different categories with the help of a pie chart. The values are seen as percentages on the pie chart.
- **Budget Tracking**: Displays the budget amount per category alongside the current total spending. This helps user track the budget that they have set and the current total spending for that category for that particular time.

### Overview

- **Monthly Overview**: Renders a summary of the total income, the total expenses per month over time, and the total income and expenses per category for the current month.
- **Dashboard**: Displays the current month's total income, expenses, and balance, along with recent transactions.

## Notes

- **Initial Data Display**: The overview page may initially be empty due to insufficient data. To showcase how the data would look with more entries, a `fake_overview.html` is provided.

## Future Works:
- **Time-Series**: Time-series for the transactions.
- **Cloud DataBase**" To make this application suitable for more users.

## Conclusion

This personal finance manager aims to provide a user-friendly interface for tracking income, expenses, and budgets, offering valuable insights through visualizations and summaries. It simplifies the process of managing personal finances compared to traditional methods like Excel sheets.

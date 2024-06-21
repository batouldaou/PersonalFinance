# Personal Finance Tracker
#### Video Demo:  <URL HERE>
#### Description:
# Personal Finance Manager Web Application

## Overview

A personal finance manager web application created with Flask on Python. The database is managed using SQLite3. The inspiration for this project comes from my boyfriend, who uses a personalized Excel sheet to track his spending across different categories. I aimed to create a smoother and more user-friendly solution for him.

## Features

### User Authentication

- **Sign-In**: Users are prompted to sign in. Authentication is handled through AUTH-0, ensuring secure sign-in.

### Categories

- **Customizable Categories**: Users can create and edit categories to track income (e.g., Jobs, Stocks, Side Hustles) and expenses.
- **Dynamic Category List**: The category list dynamically changes based on the type of transaction (income or expense) selected.

### Transactions

- **Add Transactions**: Users can add transactions by specifying the amount and the related category.
- **Transaction Types**: Users select the type of transaction (income or expense), which updates the category list accordingly.

### Budget Management

- **Set Budgets**: Users can navigate to the budget page to set a budget for each expense category.
- **Budget Calculation**: Budgets are defined as a percentage of the total income, and the application calculates and displays the budget amounts.
- **Edit Budgets**: Budgets can be modified, updated, or deleted as needed.

### Analysis

- **Visual Analysis**: The analysis page visually represents budget distribution across different categories.
- **Bar Chart**: Displays the budget amount per category alongside the current total spending.
- **Budget Tracking**: Helps users keep track of their budget and spending per category.

### Overview

- **Monthly Overview**: Renders a summary of total income, total expenses per month over time, and total income and expenses per category for the current month.
- **Dashboard**: Displays the current month's total income, expenses, and balance, along with recent transactions.

## Notes

- **Initial Data Display**: The overview page may initially be empty due to insufficient data. To showcase how the data would look with more entries, a `fake_overview.html` is provided.

## Conclusion

This personal finance manager aims to provide a user-friendly interface for tracking income, expenses, and budgets, offering valuable insights through visualizations and summaries. It simplifies the process of managing personal finances compared to traditional methods like Excel sheets.

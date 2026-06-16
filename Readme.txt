# ExpenseTracker - Personal Finance Dashboard

A full-stack personal finance dashboard with automatic transaction categorization, real-time analytics, and persistent data storage.

---

## Overview

ExpenseTracker is a complete financial management application that helps users track their spending, categorize transactions automatically, and visualize their financial health. Built with modern web technologies, it features a professional banking-style interface, CSV import/export capabilities, and intelligent auto-categorization.

---

## Features

### Core Features

- **Smart Auto-Categorization**: Automatically categorizes transactions into 9 categories (Income, Food & Dining, Transport, Shopping, Bills & Utilities, Entertainment, Healthcare, Travel, Other)
- **Interactive Dashboard**: Real-time visualizations including doughnut charts for spending by category and line charts for income vs expense trends
- **Transaction Management**: Complete CRUD operations with instant search and filtering
- **CSV Import/Export**: Bulk upload bank statements and export reports
- **Data Persistence**: Full-stack integration with SQLite database for reliable data storage
- **Financial Analytics**: Instant calculations of total balance, income, expenses, and savings rate

### Dashboard Features

- **Total Balance**: Real-time account balance
- **Total Income**: Track all income sources
- **Total Expenses**: Monitor spending habits
- **Savings Rate**: Percentage of income saved
- **Spending by Category**: Doughnut chart visualization
- **Income vs Expenses Trend**: Line chart for monthly comparison
- **Search Transactions**: Find transactions by description or category
- **Filter Transactions**: View All, Income only, or Expenses only

### Auto-Categorization Rules

| Category | Keywords |
|----------|----------|
| Income | salary, paycheck, deposit, refund, bonus, freelance |
| Food & Dining | starbucks, restaurant, cafe, pizza, groceries, lunch |
| Transport | uber, lyft, taxi, gas, fuel, parking, bus, train |
| Shopping | amazon, walmart, target, best buy, ebay, store, mall |
| Bills & Utilities | electric, water, internet, netflix, spotify, phone, rent |
| Entertainment | cinema, movie, theater, concert, hulu, disney, gaming |
| Healthcare | pharmacy, doctor, hospital, clinic, dental, medical |
| Travel | flight, hotel, airbnb, booking, vacation, trip |

---

## Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5 | Structure and markup |
| CSS3 | Professional banking-style design |
| JavaScript (Vanilla) | Application logic and interactivity |
| Chart.js | Data visualization (doughnut and line charts) |
| Font Awesome | Icons and visual elements |
| Google Fonts (Inter) | Typography |

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Programming language |
| FastAPI | REST API framework |
| SQLite | Database (file-based, no server required) |
| Uvicorn | ASGI server |
| Python-Multipart | CSV file upload handling |

### Development Tools
- Git for version control
- VS Code as the primary IDE
- PowerShell for command line operations

---

## Project Structure


How to Run FastAPI in Terminal - Step by Step
Here's the exact terminal commands to run your FastAPI backend:

Step 1: Install required packages on terminal -main.py
input:
pip install fastapi uvicorn 

Step 2: Using Uvicorn on terminal in main.py
input:
uvicorn main:app --reload --port 8000

OUTPUT:
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://120.0.0.1:0000


note: run this on the backend terminal to connect to the SQLite DB 

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
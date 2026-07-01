# ExpenseTracker

ExpenseTracker is a full-stack personal finance dashboard designed to help users monitor spending, track income, and gain insights into their financial habits. The application provides automated transaction categorization, interactive analytics, and secure data persistence through a modern web-based interface.

## Key Features

* Automated transaction categorization across multiple spending categories
* Interactive financial dashboard with real-time analytics
* Income, expense, balance, and savings tracking
* Transaction management with search and filtering
* CSV import and export functionality
* Persistent data storage using SQLite
* Visual reporting with Chart.js

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### Backend

* Python
* FastAPI
* SQLite
* Uvicorn

### Tools

* Git
* GitHub
* VS Code

## Running the Application

### Install Dependencies

```bash
pip install fastapi uvicorn
```

### Start the Backend Server

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

```text
http://localhost:8000
```

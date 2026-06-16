from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sqlite3
import csv
import io
import os
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI(
    title="ExpenseTracker API",
    description="Personal Finance Dashboard with SQLite & Auto-Categorization",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# DATABASE SETUP
# ============================================

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'expenses.db')

def get_db_connection():
    """Create and return a database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            auto_tagged BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ SQLite database initialized successfully!")
    print(f"📁 Database location: {DB_PATH}")

# Initialize database on startup
init_db()

# ============================================
# AUTO-CATEGORIZATION ENGINE
# ============================================

CATEGORY_RULES = {
    "Income": ["salary", "paycheck", "deposit", "payment received", "refund", "reimbursement", "freelance", "bonus", "income"],
    "Food & Dining": ["uber eats", "doordash", "grubhub", "starbucks", "coffee", "restaurant", "cafe", "pizza", "mcdonald", "chipotle", "wendy", "kfc", "burger", "sushi", "dining", "lunch", "dinner", "groceries", "grocery"],
    "Transport": ["uber", "lyft", "taxi", "gas", "fuel", "parking", "toll", "bus", "train", "subway", "metro", "shell", "bp"],
    "Shopping": ["amazon", "walmart", "target", "best buy", "ebay", "etsy", "mall", "store", "shop", "nordstrom", "zara", "h&m", "costco"],
    "Bills & Utilities": ["electric", "water", "gas bill", "internet", "netflix", "spotify", "phone bill", "utility", "rent", "mortgage", "wifi", "cable", "subscription"],
    "Entertainment": ["cinema", "movie", "theater", "concert", "hulu", "disney+", "game", "gaming", "steam", "playstation", "xbox"],
    "Healthcare": ["pharmacy", "doctor", "hospital", "clinic", "dental", "vision", "medical", "health", "prescription", "dentist"],
    "Travel": ["flight", "hotel", "airbnb", "booking", "vacation", "trip", "airline", "rental car", "travel"]
}

def auto_categorize(description: str) -> str:
    """Auto-categorize transaction based on description keywords"""
    desc_lower = description.lower()
    
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
    
    return "Other"

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "ExpenseTracker API with SQLite & Auto-Categorization 🚀",
        "version": "2.0.0",
        "endpoints": {
            "GET /transactions": "View all transactions",
            "POST /transactions": "Add single transaction",
            "POST /upload-csv": "Upload bank CSV file",
            "PUT /transactions/{id}": "Update transaction",
            "POST /update-category/{id}": "Update transaction category",
            "DELETE /transactions/{id}": "Delete transaction",
            "GET /stats": "Get statistics"
        },
        "docs": "/docs"
    }

@app.get("/transactions")
async def get_transactions():
    """Get all transactions from SQLite database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, description, category, date, auto_tagged FROM transactions ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    transactions = [
        {
            "id": r["id"],
            "amount": r["amount"],
            "description": r["description"],
            "category": r["category"],
            "date": r["date"],
            "auto_tagged": bool(r["auto_tagged"])
        }
        for r in rows
    ]
    
    return {"transactions": transactions, "count": len(transactions)}

@app.post("/transactions")
async def add_transaction(
    amount: float = Form(...),
    description: str = Form(...),
    category: str = Form(None)
):
    """Add a new transaction with optional auto-categorization"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Auto-categorize if no category provided or "auto"
    if not category or category == "auto":
        detected_category = auto_categorize(description)
        auto_tagged = True
    else:
        detected_category = category
        auto_tagged = False
    
    date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute(
        "INSERT INTO transactions (amount, description, category, date, auto_tagged) VALUES (?, ?, ?, ?, ?)",
        (amount, description, detected_category, date, 1 if auto_tagged else 0)
    )
    
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": "Transaction saved to SQLite",
        "id": transaction_id,
        "auto_categorized": auto_tagged,
        "category": detected_category
    }

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file and import transactions with auto-categorization"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Read CSV content
    contents = await file.read()
    
    try:
        csv_text = contents.decode('utf-8')
    except UnicodeDecodeError:
        csv_text = contents.decode('latin-1')
    
    csv_reader = csv.DictReader(io.StringIO(csv_text))
    imported_count = 0
    errors = []
    
    # Detect column names
    fieldnames = csv_reader.fieldnames or []
    
    # Common column name mappings
    possible_amount_cols = ['amount', 'Amount', 'AMOUNT', 'Transaction Amount', 'Debit', 'Credit', 'Sum', 'Price']
    possible_desc_cols = ['description', 'Description', 'DESCRIPTION', 'Transaction Description', 'Narration', 'Memo', 'Merchant']
    possible_date_cols = ['date', 'Date', 'DATE', 'Transaction Date', 'Date']
    
    # Detect actual column names
    amount_col = next((col for col in possible_amount_cols if col in fieldnames), None)
    desc_col = next((col for col in possible_desc_cols if col in fieldnames), None)
    
    if not amount_col or not desc_col:
        conn.close()
        return JSONResponse(
            status_code=400,
            content={
                "error": "Could not detect required columns",
                "found_columns": fieldnames,
                "required": ["amount column", "description column"]
            }
        )
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            # Parse amount
            amount_str = row.get(amount_col, "0").replace('$', '').replace(',', '').strip()
            amount = abs(float(amount_str))
            
            # Skip zero amounts
            if amount == 0:
                continue
            
            # Get description
            description = row.get(desc_col, "").strip()
            if not description:
                continue
            
            # Auto-categorize
            category = auto_categorize(description)
            
            # Get date or use today
            date_str = datetime.now().strftime("%Y-%m-%d")
            if possible_date_cols:
                for col in possible_date_cols:
                    if col in row and row[col]:
                        try:
                            # Try to parse date
                            date_str = row[col]
                            # Simple date parsing - you may need more robust parsing
                            break
                        except:
                            pass
            
            # Insert into database
            cursor.execute(
                "INSERT INTO transactions (amount, description, category, date, auto_tagged) VALUES (?, ?, ?, ?, ?)",
                (amount, description, category, date_str, 1)
            )
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "imported_count": imported_count,
        "errors": errors,
        "total_transactions": imported_count
    }

@app.put("/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: int,
    amount: float = Form(...),
    description: str = Form(...),
    category: str = Form(...)
):
    """Update a transaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE transactions SET amount = ?, description = ?, category = ?, auto_tagged = 0 WHERE id = ?",
        (amount, description, category, transaction_id)
    )
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Transaction updated successfully"}

@app.post("/update-category/{transaction_id}")
async def update_category(transaction_id: int, category: str = Form(...)):
    """Update transaction category (user override)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE transactions SET category = ?, auto_tagged = 0 WHERE id = ?",
        (category, transaction_id)
    )
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Category updated"}

@app.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """Delete a transaction"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    conn.commit()
    conn.close()
    
    return {"message": "Transaction deleted successfully"}

@app.get("/stats")
async def get_stats():
    """Get summary statistics from SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total income
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE category = 'Income'")
    total_income = cursor.fetchone()[0]
    
    # Total expenses
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE category != 'Income'")
    total_expenses = cursor.fetchone()[0]
    
    # Total transactions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_transactions = cursor.fetchone()[0]
    
    # Balance
    balance = total_income - total_expenses
    
    conn.close()
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "total_transactions": total_transactions,
        "savings_rate": (balance / total_income * 100) if total_income > 0 else 0
    }

@app.get("/transactions/search")
async def search_transactions(q: str):
    """Search transactions by description or category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, amount, description, category, date, auto_tagged FROM transactions WHERE description LIKE ? OR category LIKE ? ORDER BY date DESC",
        (f"%{q}%", f"%{q}%")
    )
    rows = cursor.fetchall()
    conn.close()
    
    transactions = [
        {
            "id": r["id"],
            "amount": r["amount"],
            "description": r["description"],
            "category": r["category"],
            "date": r["date"],
            "auto_tagged": bool(r["auto_tagged"])
        }
        for r in rows
    ]
    
    return {"transactions": transactions, "count": len(transactions)}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ExpenseTracker Backend...")
    print("📁 Database location: instance/expenses.db")
    print("📍 API running at: http://localhost:8000")
    print("📊 API docs at: http://localhost:8000/docs")
    print("📊 Auto-categorization: ENABLED")
    print("📁 CSV Upload: ENABLED")
    uvicorn.run(app, host="0.0.0.0", port=8000)
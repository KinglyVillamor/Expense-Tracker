from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import csv
import io
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory storage
transactions_db = []
next_id = 1

# STONE 5: Auto-categorization rules
CATEGORY_RULES = {
    "Food & Dining": ["uber eats", "doordash", "grubhub", "starbucks", "coffee", "restaurant", "cafe", "pizza", "mcdonald", "chipotle", "wendy", "kfc", "burger", "sushi", "dining"],
    "Transport": ["uber", "lyft", "taxi", "gas", "fuel", "parking", "toll", "bus", "train", "subway", "metro"],
    "Shopping": ["amazon", "walmart", "target", "best buy", "ebay", "etsy", "mall", "store", "shop", "nordstrom", "zara", "h&m"],
    "Bills & Utilities": ["electric", "water", "gas bill", "internet", "netflix", "spotify", "phone bill", "utility", "rent", "mortgage", "wifi", "cable"],
    "Entertainment": ["cinema", "movie", "theater", "concert", "spotify", "netflix", "hulu", "disney+", "game", "gaming"],
    "Income": ["salary", "paycheck", "deposit", "transfer", "refund", "reimbursement", "freelance", "payment received"],
    "Healthcare": ["pharmacy", "doctor", "hospital", "clinic", "dental", "vision", "medical", "health"],
    "Travel": ["flight", "hotel", "airbnb", "booking", "vacation", "trip", "airline", "rental car"]
}

def auto_categorize(description: str) -> str:
    """
    STONE 5: Automatically guess category based on description keywords
    """
    desc_lower = description.lower()
    
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category
    
    return "Other"  # Default category if no rules match

@app.post("/transactions")
async def create_transaction(
    amount: float = Form(...),
    description: str = Form(...),
    category: str = Form(None)  # Make category optional for auto-detection
):
    global next_id
    
    # STONE 5: Auto-categorize if no category provided or if it's "auto"
    if not category or category == "auto":
        detected_category = auto_categorize(description)
    else:
        detected_category = category
    
    new_transaction = {
        "id": next_id,
        "amount": amount,
        "description": description,
        "category": detected_category,
        "auto_tagged": not category or category == "auto"  # Track if auto-tagged
    }
    transactions_db.append(new_transaction)
    next_id += 1
    
    return {
        "status": "success",
        "message": "Transaction stored",
        "transaction": new_transaction,
        "auto_categorized": not category or category == "auto"
    }

# STONE 4: CSV Upload endpoint
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file from your bank and import transactions
    Expected CSV columns: Date, Description, Amount (or similar)
    """
    global next_id
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Read CSV content
    contents = await file.read()
    csv_text = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_text))
    
    imported_count = 0
    errors = []
    
    # Common column name mappings (handles different bank formats)
    possible_amount_cols = ['amount', 'Amount', 'AMOUNT', 'Transaction Amount', 'Debit', 'Credit', 'Sum']
    possible_desc_cols = ['description', 'Description', 'DESCRIPTION', 'Transaction Description', 'Narration', 'Memo']
    possible_date_cols = ['date', 'Date', 'DATE', 'Transaction Date']
    
    # Detect actual column names
    fieldnames = csv_reader.fieldnames or []
    amount_col = next((col for col in possible_amount_cols if col in fieldnames), None)
    desc_col = next((col for col in possible_desc_cols if col in fieldnames), None)
    
    if not amount_col or not desc_col:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Could not detect required columns",
                "found_columns": fieldnames,
                "required": ["amount/Amount column", "description/Description column"]
            }
        )
    
    for row_num, row in enumerate(csv_reader, start=2):  # start=2 because row 1 is header
        try:
            # Parse amount (handle negative values for debits)
            amount_str = row.get(amount_col, "0").replace('$', '').replace(',', '').strip()
            amount = float(amount_str)
            
            # Skip zero or empty amounts
            if amount == 0:
                continue
                
            # Get description
            description = row.get(desc_col, "").strip()
            if not description:
                continue
            
            # Auto-categorize based on description
            category = auto_categorize(description)
            
            # Add transaction
            new_transaction = {
                "id": next_id,
                "amount": abs(amount),  # Store absolute value
                "description": description,
                "category": category,
                "auto_tagged": True
            }
            transactions_db.append(new_transaction)
            next_id += 1
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "status": "success",
        "imported_count": imported_count,
        "errors": errors,
        "total_transactions": len(transactions_db)
    }

@app.get("/transactions")
async def get_transactions():
    return {
        "count": len(transactions_db),
        "transactions": transactions_db
    }

@app.post("/update-category/{transaction_id}")
async def update_category(transaction_id: int, category: str = Form(...)):
    """
    STONE 5: Allow user to override auto-categorized transactions
    """
    for tx in transactions_db:
        if tx["id"] == transaction_id:
            tx["category"] = category
            tx["auto_tagged"] = False
            return {"status": "success", "transaction": tx}
    
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int):
    """
    Delete a transaction by ID
    """
    global transactions_db
    for i, tx in enumerate(transactions_db):
        if tx["id"] == transaction_id:
            deleted = transactions_db.pop(i)
            return {"status": "success", "deleted": deleted}
    
    raise HTTPException(status_code=404, detail="Transaction not found")

@app.get("/")
async def root():
    return {
        "message": "Stone Ledger Backend - Now with CSV Upload & Auto-categorization! 🚀",
        "endpoints": {
            "POST /transactions": "Add single transaction",
            "POST /upload-csv": "Upload bank CSV file",
            "GET /transactions": "View all transactions",
            "POST /update-category/{id}": "Update transaction category",
            "DELETE /transactions/{id}": "Delete transaction"
        }
    }
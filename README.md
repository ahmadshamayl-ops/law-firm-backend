# AI-Powered Cash Posting Agent - Proof of Concept

A Python-based PoC for automated cash posting that intelligently matches bank payments to open invoices using AI-driven matching algorithms.

## Overview

This PoC demonstrates an automated cash posting system that:
- Loads data from multiple sources (Bank Statements, Remittance Advices, ERP Invoices)
- Matches payments to invoices using intelligent algorithms
- Generates posting entries and exception reports
- Provides REST API endpoints for integration

## Features

- **User Authentication**:
  - User signup and login functionality
  - JWT token-based authentication
  - Protected routes and secure API access
  - Session management with localStorage

- **Interactive Web Frontend**:
  - User-friendly HTML/CSS/JavaScript interface
  - One-click payment processing
  - Real-time metrics and progress tracking
  - Tabbed view for matched postings and exceptions
  - CSV download functionality

- **Intelligent Matching Engine**:
  - Primary: Matches using Invoice_Reference from remittance data
  - Fallback: Fuzzy matching based on payer name and amount similarity
  - Multiple match types: Exact, Reference, Fuzzy, Contextual

- **API Endpoints**:
  - `POST /api/v1/postings/process` - Process payments and match to invoices
  - `GET /api/v1/postings/results` - Get matched posting results
  - `GET /api/v1/postings/exceptions` - Get unmatched payments requiring review

- **Output Formats**:
  - JSON responses via API
  - CSV files for matched postings

## Project Structure

```
lawfirm/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_loader.py      # CSV data loading
│   │   ├── matching_engine.py  # Matching algorithms
│   │   └── posting_generator.py # Output file generation
│   └── routers/
│       ├── __init__.py
│       └── postings.py         # API routes
├── static/
│   └── index.html              # Web frontend interface
├── output/                     # Generated output files
├── requirements.txt
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager
- PostgreSQL installed and running
- pgAdmin 4 (optional, for database management)

### Database Setup

1. **Create PostgreSQL Database**:
   - Open pgAdmin 4
   - Create a new database named `law_firm`
   - See `DATABASE_SETUP.md` for detailed instructions

2. **Configure Database Connection**:
   - Create a `.env` file in the project root
   - Add your database connection string:
     ```env
     DATABASE_URL=postgresql://postgres:your_password@localhost:5432/law_firm
     ```
   - Replace `your_password` with your PostgreSQL password

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd lawfirm
   ```

2. **Create a virtual environment (recommended)**:
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database tables**:
   ```bash
   python app/init_db.py
   ```
   (Or tables will be created automatically on first server start)

5. **Ensure data files are in the project root** (for testing):
   - `1. ERP _ Open Invoices (ERP_Invoice_Data.csv).csv`
   - `2. Bank Statement Data (Bank_Statement.csv) - Sheet1.csv`
   - `3. remittance data - Sheet1.csv`

## Running the Application

### Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The application will be available at:
- **Web Frontend**: http://localhost:8000 (Interactive UI)
- **API Base URL**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Using the Web Frontend

1. **Sign Up/Login**:
   - Open your browser and navigate to http://localhost:8000
   - If you don't have an account, click "Sign up here" to create one
   - Enter your username and password to login

2. **Upload Files**:
   - Upload the three required CSV files (Bank Statement, Remittance, ERP Invoices)
   - Wait for all files to be uploaded (button will enable automatically)

3. **Process Payments**:
   - Click the **"🚀 Process Payments"** button
   - View the results:
     - **Metrics**: See total payments, matched count, exceptions, and match rate
     - **Matched Postings Tab**: View all successfully matched payments
     - **Exceptions Tab**: View payments that require manual review

4. **Download Results**:
   - Click **"📥 Download CSV"** to save the matched postings file

5. **Logout**:
   - Click the **"Logout"** button in the top right corner when done

## Usage Examples

### 1. Process Payments (POST request)

```bash
curl -X POST "http://localhost:8000/api/v1/postings/process" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Or with custom file paths:
```bash
curl -X POST "http://localhost:8000/api/v1/postings/process" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_statement_path": "path/to/bank_statement.csv",
    "remittance_path": "path/to/remittance.csv",
    "erp_invoice_path": "path/to/invoices.csv"
  }'
```

### 2. Get Matched Results (GET request)

```bash
curl "http://localhost:8000/api/v1/postings/results"
```

### 3. Get Exceptions (GET request)

```bash
curl "http://localhost:8000/api/v1/postings/exceptions"
```

### Using Python requests:

```python
import requests

# Process payments
response = requests.post("http://localhost:8000/api/v1/postings/process", json={})
result = response.json()

print(f"Matched: {result['matched_count']}/{result['total_payments']}")
print(f"Match Rate: {result['match_rate']}%")
print(f"Output file: {result['output_file_path']}")
```

## Matching Logic

### Primary Method: Invoice Reference Matching
1. Matches bank transaction to remittance advice by payer name and amount
2. Uses `Invoice_Reference` from remittance to find corresponding invoice
3. Calculates confidence based on name and amount similarity

### Fallback Method: Fuzzy Matching
1. Compares payer name similarity (normalized, handles business suffixes)
2. Compares amount similarity (percentage difference)
3. Requires minimum combined score threshold (70%)
4. Considers currency matching

### Match Types
- **Exact**: Invoice reference matches and amounts are very close (>95% similarity)
- **Reference**: Invoice reference matches but amounts differ
- **Fuzzy (name)**: High name similarity (>80%) and good amount match
- **Fuzzy (amount)**: High amount similarity (>85%)
- **Contextual**: Lower confidence match based on combined factors

## Output Files

Matched postings are saved to `output/Matched_Postings_YYYYMMDD_HHMMSS.csv` with columns:
- Payment_Ref
- Payer_Name
- Matched_Invoice
- Match_Type
- Confidence
- Posting_Status
- Bank_Amount
- Invoice_Amount
- Amount_Difference

## Success Metrics

The PoC targets:
- **≥85% auto-match accuracy** on sample data
- Automated posting for high-confidence matches
- Clear exception reporting for manual review

## Limitations (PoC Scope)

- Static data processing (no real-time integrations)
- No database persistence (results are file-based)
- No user authentication/authorization
- No OCR/NLP for document extraction (assumes structured CSV input)
- Simplified matching algorithms (production would use ML models)

## Future Enhancements

- Database integration for persistence
- OCR/NLP for unstructured document processing
- Machine learning models for improved matching
- User dashboard for review and approval
- Integration with ERP systems (SAP, Oracle, etc.)
- Email/SFTP auto-fetching capabilities
- Continuous learning from user corrections

## License

Proof of Concept - Internal Use Only


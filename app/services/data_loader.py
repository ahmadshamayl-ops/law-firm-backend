"""Service for loading and parsing CSV data files"""

import csv
import io
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Union

from app.models.schemas import BankTransaction, Invoice, Remittance


def parse_amount(amount_str: str) -> Decimal:
    """Parse amount string with commas to Decimal"""
    if isinstance(amount_str, (int, float)):
        return Decimal(str(amount_str))
    # Remove commas and convert to Decimal
    cleaned = str(amount_str).replace(",", "").strip()
    return Decimal(cleaned)


def parse_date(date_str: str) -> datetime.date:
    """Parse date string to date object"""
    if isinstance(date_str, datetime):
        return date_str.date()
    # Try common date formats
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")


def load_erp_invoices(file_source: Union[str, io.TextIOWrapper]) -> List[Invoice]:
    """Load ERP invoice data from CSV file (path or file object)"""
    invoices = []
    
    # Handle both file path and file object
    if isinstance(file_source, str):
        file_path = Path(file_source)
        if not file_path.exists():
            raise FileNotFoundError(f"Invoice file not found: {file_path}")
        file_obj = open(file_path, "r", encoding="utf-8")
        should_close = True
    else:
        file_obj = file_source
        should_close = False
    
    try:
        # Reset file pointer if it's a file object
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        
        reader = csv.DictReader(file_obj)
        for row in reader:
            try:
                invoice = Invoice(
                    invoice_id=row["Invoice_ID"].strip(),
                    client_name=row["Client_Name"].strip(),
                    matter_id=row["Matter_ID"].strip(),
                    invoice_date=parse_date(row["Invoice_Date"]),
                    invoice_amount=parse_amount(row["Invoice_Amount (USD)"]),
                    currency=row["Currency"].strip(),
                    due_date=parse_date(row["Due_Date"]),
                    status=row["Status"].strip()
                )
                invoices.append(invoice)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid invoice row: {e}")
                continue
    finally:
        if should_close:
            file_obj.close()
    
    return invoices


def load_bank_statements(file_source: Union[str, io.TextIOWrapper]) -> List[BankTransaction]:
    """Load bank statement data from CSV file (path or file object)"""
    transactions = []
    
    # Handle both file path and file object
    if isinstance(file_source, str):
        file_path = Path(file_source)
        if not file_path.exists():
            raise FileNotFoundError(f"Bank statement file not found: {file_path}")
        file_obj = open(file_path, "r", encoding="utf-8")
        should_close = True
    else:
        file_obj = file_source
        should_close = False
    
    try:
        # Reset file pointer if it's a file object
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        
        reader = csv.DictReader(file_obj)
        for row in reader:
            try:
                transaction = BankTransaction(
                    value_date=parse_date(row["Value_Date"]),
                    reference_no=row["Reference_No"].strip(),
                    description=row["Description"].strip(),
                    payer_name=row["Payer_Name"].strip(),
                    amount=parse_amount(row["Amount"]),
                    currency=row["Currency"].strip()
                )
                transactions.append(transaction)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid bank transaction row: {e}")
                continue
    finally:
        if should_close:
            file_obj.close()
    
    return transactions


def load_remittances(file_source: Union[str, io.TextIOWrapper]) -> List[Remittance]:
    """Load remittance advice data from CSV file (path or file object)"""
    remittances = []
    
    # Handle both file path and file object
    if isinstance(file_source, str):
        file_path = Path(file_source)
        if not file_path.exists():
            raise FileNotFoundError(f"Remittance file not found: {file_path}")
        file_obj = open(file_path, "r", encoding="utf-8")
        should_close = True
    else:
        file_obj = file_source
        should_close = False
    
    try:
        # Reset file pointer if it's a file object
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        
        reader = csv.DictReader(file_obj)
        for row in reader:
            try:
                remittance = Remittance(
                    remittance_id=row["Remittance_ID"].strip(),
                    payer_name=row["Payer_Name"].strip(),
                    invoice_reference=row["Invoice_Reference"].strip(),
                    payment_amount=parse_amount(row["Payment_Amount"]),
                    notes=row["Notes"].strip()
                )
                remittances.append(remittance)
            except (KeyError, ValueError) as e:
                print(f"Warning: Skipping invalid remittance row: {e}")
                continue
    finally:
        if should_close:
            file_obj.close()
    
    return remittances


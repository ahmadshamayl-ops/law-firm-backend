"""API routes for cash posting operations"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List
import io

from app.models.schemas import (
    MatchingResponse,
    MatchedPosting,
    BankTransaction,
    Invoice,
    Remittance
)
from app.services.data_loader import (
    load_bank_statements,
    load_erp_invoices,
    load_remittances
)
from app.services.matching_engine import match_payment_to_invoice
from app.services.posting_generator import save_matched_postings_csv
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/v1/postings", tags=["postings"])


@router.post("/process", response_model=MatchingResponse)
async def process_payments(
    bank_statement_file: UploadFile = File(..., description="Bank Statement CSV file"),
    remittance_file: UploadFile = File(..., description="Remittance Advice CSV file"),
    erp_invoice_file: UploadFile = File(..., description="ERP Invoice Data CSV file"),
    current_user: dict = Depends(get_current_user)
):
    """
    Process payments and match them to invoices.
    
    Requires three CSV file uploads:
    - bank_statement_file: Bank statement with payment transactions
    - remittance_file: Remittance advice with invoice references
    - erp_invoice_file: ERP invoice data with open invoices
    """
    try:
        # Validate file types
        if not bank_statement_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Bank statement file must be a CSV file")
        if not remittance_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Remittance file must be a CSV file")
        if not erp_invoice_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="ERP invoice file must be a CSV file")
        
        # Read file contents and create file-like objects
        bank_statement_content = await bank_statement_file.read()
        remittance_content = await remittance_file.read()
        erp_invoice_content = await erp_invoice_file.read()
        
        # Create StringIO objects from file contents
        bank_statement_io = io.StringIO(bank_statement_content.decode('utf-8'))
        remittance_io = io.StringIO(remittance_content.decode('utf-8'))
        erp_invoice_io = io.StringIO(erp_invoice_content.decode('utf-8'))
        
        # Load data from uploaded files
        invoices = load_erp_invoices(erp_invoice_io)
        bank_transactions = load_bank_statements(bank_statement_io)
        remittances = load_remittances(remittance_io)
        
        # Match payments to invoices
        matched_postings: List[MatchedPosting] = []
        unmatched_payments: List[dict] = []
        
        for transaction in bank_transactions:
            matched = match_payment_to_invoice(transaction, remittances, invoices)
            
            if matched:
                matched_postings.append(matched)
            else:
                unmatched_payments.append({
                    "payment_ref": transaction.reference_no,
                    "payer_name": transaction.payer_name,
                    "amount": str(transaction.amount),
                    "currency": transaction.currency,
                    "date": transaction.value_date.isoformat()
                })
        
        # Save results to CSV
        output_file_path = None
        if matched_postings:
            output_file_path = save_matched_postings_csv(matched_postings)
        
        # Calculate metrics
        total_payments = len(bank_transactions)
        matched_count = len(matched_postings)
        unmatched_count = len(unmatched_payments)
        match_rate = (matched_count / total_payments * 100) if total_payments > 0 else 0.0
        
        return MatchingResponse(
            total_payments=total_payments,
            matched_count=matched_count,
            unmatched_count=unmatched_count,
            match_rate=round(match_rate, 2),
            matched_postings=matched_postings,
            unmatched_payments=unmatched_payments,
            output_file_path=output_file_path
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing payments: {str(e)}")


@router.get("/results", response_model=List[MatchedPosting])
async def get_matched_results():
    """
    Get the latest matched posting results.
    Note: This endpoint is deprecated. Results are returned from /process endpoint.
    """
    raise HTTPException(
        status_code=400, 
        detail="This endpoint requires file uploads. Please use /process endpoint with file uploads."
    )


@router.get("/exceptions")
async def get_exceptions():
    """
    Get unmatched payments that require manual review.
    Note: This endpoint is deprecated. Exceptions are returned from /process endpoint.
    """
    raise HTTPException(
        status_code=400, 
        detail="This endpoint requires file uploads. Please use /process endpoint with file uploads."
    )


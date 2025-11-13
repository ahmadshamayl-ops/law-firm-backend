"""Pydantic models for data validation and serialization"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class Invoice(BaseModel):
    """ERP Invoice data model"""
    invoice_id: str
    client_name: str
    matter_id: str
    invoice_date: date
    invoice_amount: Decimal
    currency: str
    due_date: date
    status: str


class BankTransaction(BaseModel):
    """Bank statement transaction data model"""
    value_date: date
    reference_no: str
    description: str
    payer_name: str
    amount: Decimal
    currency: str


class Remittance(BaseModel):
    """Remittance advice data model"""
    remittance_id: str
    payer_name: str
    invoice_reference: str
    payment_amount: Decimal
    notes: str


class MatchedPosting(BaseModel):
    """Matched posting result model"""
    payment_ref: str
    payer_name: str
    matched_invoice: str
    match_type: str
    confidence: str
    posting_status: str
    bank_amount: Optional[Decimal] = None
    invoice_amount: Optional[Decimal] = None
    amount_difference: Optional[Decimal] = None


class MatchingRequest(BaseModel):
    """Request model for processing payments"""
    bank_statement_path: Optional[str] = None
    remittance_path: Optional[str] = None
    erp_invoice_path: Optional[str] = None


class MatchingResponse(BaseModel):
    """Response model for matching results"""
    total_payments: int
    matched_count: int
    unmatched_count: int
    match_rate: float
    matched_postings: list[MatchedPosting]
    unmatched_payments: list[dict]
    output_file_path: Optional[str] = None



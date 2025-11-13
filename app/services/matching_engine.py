"""Matching engine for intelligent payment-to-invoice matching"""

from decimal import Decimal
from typing import Optional, Tuple
from difflib import SequenceMatcher

from app.models.schemas import BankTransaction, Invoice, MatchedPosting, Remittance


def calculate_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names using SequenceMatcher"""
    # Normalize names: lowercase, remove common suffixes/prefixes
    def normalize(name: str) -> str:
        name = name.lower().strip()
        # Remove common business suffixes
        for suffix in [" ltd", " ltd.", " limited", " inc", " inc.", " corp", " corp.", 
                      " llc", " pte", " pte.", " co", " co.", " group", " holdings"]:
            if name.endswith(suffix):
                name = name[:-len(suffix)].strip()
        return name
    
    norm1 = normalize(name1)
    norm2 = normalize(name2)
    
    # Use SequenceMatcher for similarity
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    
    # Boost similarity if one name contains the other
    if norm1 in norm2 or norm2 in norm1:
        similarity = min(1.0, similarity + 0.2)
    
    return similarity


def calculate_amount_similarity(amount1: Decimal, amount2: Decimal) -> float:
    """Calculate similarity between two amounts"""
    if amount1 == amount2:
        return 1.0
    
    # Calculate percentage difference
    if amount2 == 0:
        return 0.0
    
    diff = abs(amount1 - amount2)
    percentage_diff = float(diff / amount2)
    
    # Convert to similarity score (0-1)
    # 0% diff = 1.0, 5% diff = 0.9, 10% diff = 0.8, etc.
    similarity = max(0.0, 1.0 - (percentage_diff * 2))
    return similarity


def match_by_invoice_reference(
    transaction: BankTransaction,
    remittances: list[Remittance],
    invoices: list[Invoice]
) -> Optional[Tuple[Invoice, Remittance, str, float]]:
    """Match payment using Invoice_Reference from remittance data (primary method)"""
    # Find remittance that matches this transaction
    matching_remittance = None
    
    # Try to match remittance by payer name and amount
    for remittance in remittances:
        name_sim = calculate_name_similarity(transaction.payer_name, remittance.payer_name)
        amount_sim = calculate_amount_similarity(transaction.amount, remittance.payment_amount)
        
        # If both name and amount are similar enough, consider it a match
        if name_sim > 0.6 and amount_sim > 0.8:
            matching_remittance = remittance
            break
    
    if not matching_remittance:
        return None
    
    # Find invoice by Invoice_Reference
    invoice_ref = matching_remittance.invoice_reference
    matching_invoice = None
    
    for invoice in invoices:
        if invoice.invoice_id == invoice_ref:
            matching_invoice = invoice
            break
    
    if not matching_invoice:
        return None
    
    # Determine match type and confidence
    name_sim = calculate_name_similarity(transaction.payer_name, matching_invoice.client_name)
    amount_sim = calculate_amount_similarity(transaction.amount, matching_invoice.invoice_amount)
    
    # Exact match if invoice reference matches and amounts are very close
    if amount_sim > 0.95:
        match_type = "Exact"
        confidence = min(99, 85 + int(amount_sim * 10) + int(name_sim * 5))
    else:
        match_type = "Reference"
        confidence = min(98, 80 + int(amount_sim * 10) + int(name_sim * 5))
    
    return matching_invoice, matching_remittance, match_type, confidence / 100.0


def fuzzy_match(
    transaction: BankTransaction,
    invoices: list[Invoice],
    exclude_invoice_ids: set[str] = None
) -> Optional[Tuple[Invoice, str, float]]:
    """Fuzzy match payment to invoice using name and amount similarity (fallback method)"""
    if exclude_invoice_ids is None:
        exclude_invoice_ids = set()
    
    best_match = None
    best_score = 0.0
    best_match_type = None
    
    for invoice in invoices:
        if invoice.invoice_id in exclude_invoice_ids:
            continue
        
        # Skip if currency doesn't match
        if transaction.currency != invoice.currency:
            continue
        
        # Calculate similarity scores
        name_sim = calculate_name_similarity(transaction.payer_name, invoice.client_name)
        amount_sim = calculate_amount_similarity(transaction.amount, invoice.invoice_amount)
        
        # Combined score (weighted: 40% name, 60% amount)
        combined_score = (name_sim * 0.4) + (amount_sim * 0.6)
        
        if combined_score > best_score and combined_score > 0.7:  # Minimum threshold
            best_score = combined_score
            best_match = invoice
            
            # Determine match type
            if name_sim > 0.8 and amount_sim > 0.9:
                best_match_type = "Fuzzy (name)"
            elif amount_sim > 0.85:
                best_match_type = "Fuzzy (amount)"
            else:
                best_match_type = "Contextual"
    
    if best_match:
        confidence = min(98, int(best_score * 100))
        return best_match, best_match_type, confidence / 100.0
    
    return None


def match_payment_to_invoice(
    transaction: BankTransaction,
    remittances: list[Remittance],
    invoices: list[Invoice]
) -> Optional[MatchedPosting]:
    """Main matching function: tries Invoice_Reference first, then fuzzy matching"""
    
    # Step 1: Try matching by Invoice_Reference (primary method)
    result = match_by_invoice_reference(transaction, remittances, invoices)
    
    if result:
        invoice, remittance, match_type, confidence = result
        amount_diff = transaction.amount - invoice.invoice_amount
        
        return MatchedPosting(
            payment_ref=transaction.reference_no,
            payer_name=transaction.payer_name,
            matched_invoice=invoice.invoice_id,
            match_type=match_type,
            confidence=f"{int(confidence * 100)}%",
            posting_status="Auto-posted",
            bank_amount=transaction.amount,
            invoice_amount=invoice.invoice_amount,
            amount_difference=amount_diff
        )
    
    # Step 2: Fallback to fuzzy matching
    result = fuzzy_match(transaction, invoices)
    
    if result:
        invoice, match_type, confidence = result
        amount_diff = transaction.amount - invoice.invoice_amount
        
        return MatchedPosting(
            payment_ref=transaction.reference_no,
            payer_name=transaction.payer_name,
            matched_invoice=invoice.invoice_id,
            match_type=match_type,
            confidence=f"{int(confidence * 100)}%",
            posting_status="Auto-posted",
            bank_amount=transaction.amount,
            invoice_amount=invoice.invoice_amount,
            amount_difference=amount_diff
        )
    
    # No match found
    return None



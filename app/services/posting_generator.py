"""Service for generating posting output files"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List

from app.models.schemas import MatchedPosting


def save_matched_postings_csv(
    matched_postings: List[MatchedPosting],
    output_dir: str = "output"
) -> str:
    """Save matched postings to CSV file"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Matched_Postings_{timestamp}.csv"
    filepath = output_path / filename
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Payment_Ref",
                "Payer_Name",
                "Matched_Invoice",
                "Match_Type",
                "Confidence",
                "Posting_Status",
                "Bank_Amount",
                "Invoice_Amount",
                "Amount_Difference"
            ]
        )
        writer.writeheader()
        
        for posting in matched_postings:
            writer.writerow({
                "Payment_Ref": posting.payment_ref,
                "Payer_Name": posting.payer_name,
                "Matched_Invoice": posting.matched_invoice,
                "Match_Type": posting.match_type,
                "Confidence": posting.confidence,
                "Posting_Status": posting.posting_status,
                "Bank_Amount": str(posting.bank_amount) if posting.bank_amount else "",
                "Invoice_Amount": str(posting.invoice_amount) if posting.invoice_amount else "",
                "Amount_Difference": str(posting.amount_difference) if posting.amount_difference else ""
            })
    
    return str(filepath)


def generate_posting_entries(matched_postings: List[MatchedPosting]) -> List[dict]:
    """Generate accounting posting entries (Debit: Bank, Credit: AR)"""
    entries = []
    
    for posting in matched_postings:
        entry = {
            "date": datetime.now().date().isoformat(),
            "debit_account": "Bank Account",
            "credit_account": "Accounts Receivable",
            "amount": float(posting.bank_amount) if posting.bank_amount else 0.0,
            "reference": posting.payment_ref,
            "invoice": posting.matched_invoice,
            "description": f"Payment from {posting.payer_name} for {posting.matched_invoice}"
        }
        entries.append(entry)
    
    return entries



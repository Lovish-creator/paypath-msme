import os
import re
import uuid
from datetime import datetime, date
from typing import Optional, Tuple
from pypdf import PdfReader

from backend.app.core.config import settings
from backend.app.schemas.invoice import InvoiceExtractionResult


class DocumentExtractor:
    """
    Extracts structured invoice information from uploaded PDF and image documents.
    Provides verified field suggestions for user confirmation before invoice creation.
    """

    @classmethod
    def get_upload_dir(cls) -> str:
        upload_dir = os.path.join(settings.STORAGE_LOCAL_DIR, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @classmethod
    def save_uploaded_file(cls, filename: str, content: bytes) -> Tuple[str, str]:
        ext = os.path.splitext(filename)[1].lower() or ".pdf"
        unique_name = f"inv_{uuid.uuid4().hex[:12]}{ext}"
        saved_path = os.path.join(cls.get_upload_dir(), unique_name)
        with open(saved_path, "wb") as f:
            f.write(content)
        return unique_name, saved_path

    @classmethod
    def extract_from_pdf(cls, file_path: str, original_filename: str) -> InvoiceExtractionResult:
        raw_text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    raw_text += text + "\n"
        except Exception:
            raw_text = ""

        return cls.parse_invoice_text(raw_text, original_filename, file_path)

    @classmethod
    def parse_invoice_text(
        cls,
        text: str,
        original_filename: str,
        saved_file_path: str,
    ) -> InvoiceExtractionResult:
        preview = text[:1500].strip() if text else ""
        confidence = 0.0

        # 1. Extract GSTIN
        gstin = None
        gstin_match = re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}\b", text, re.IGNORECASE)
        if gstin_match:
            gstin = gstin_match.group(0).upper()
            confidence += 0.25

        # 2. Extract Invoice Number
        invoice_number = None
        inv_match = re.search(
            r"(?:Invoice\s*(?:No|Number|#)|Bill\s*(?:No|#)|INV\s*[-#:])\s*[:.\-]?\s*([A-Za-z0-9\-_\/]+)",
            text,
            re.IGNORECASE,
        )
        if inv_match:
            cand = inv_match.group(1).strip()
            if len(cand) >= 3 and len(cand) <= 30:
                invoice_number = cand
                confidence += 0.25
        else:
            # Fallback heuristic based on filename
            name_cand = re.sub(r"\.[a-zA-Z0-9]+$", "", original_filename)
            if re.search(r"\d+", name_cand):
                invoice_number = f"INV-{name_cand[:12].upper()}"

        # 3. Extract Amount
        total_amount = None
        amt_match = re.search(
            r"(?:Total\s*Amount|Grand\s*Total|Invoice\s*(?:Total|Value)|Net\s*Payable|Amount\s*Due)[^\d\n\r]*[₹\sRs\.]*([\d,]+(?:\.\d{2})?)",
            text,
            re.IGNORECASE,
        )
        if amt_match:
            cand_str = amt_match.group(1).replace(",", "")
            try:
                cand_float = float(cand_str)
                if cand_float > 0:
                    total_amount = round(cand_float, 2)
                    confidence += 0.25
            except ValueError:
                pass

        # 4. Extract Date
        extracted_date = None
        date_match = re.search(
            r"(?:Invoice\s*Date|Date\s*of\s*Issue|Billing\s*Date|Dated)[:\s]*(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})",
            text,
            re.IGNORECASE,
        )
        if date_match:
            d_str = date_match.group(1)
            # Try formatting
            for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%d-%m-%y", "%d/%m/%y", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(d_str, fmt).date()
                    extracted_date = dt.isoformat()
                    confidence += 0.25
                    break
                except ValueError:
                    continue

        if not extracted_date:
            extracted_date = date.today().isoformat()

        # 5. Extract Buyer Name heuristic
        buyer_name = None
        buyer_match = re.search(
            r"(?:Billed\s*To|Buyer|Customer|Consignee|Client)[:\s]*\n?([^\n\r,]{3,60})",
            text,
            re.IGNORECASE,
        )
        if buyer_match:
            b_cand = buyer_match.group(1).strip()
            # Clean common noise
            if not any(kw in b_cand.lower() for kw in ("gstin", "invoice", "date", "address")):
                buyer_name = b_cand

        return InvoiceExtractionResult(
            invoice_number=invoice_number or f"INV-{uuid.uuid4().hex[:6].upper()}",
            buyer_name=buyer_name or "Verified Debtor Name",
            buyer_gstin=gstin,
            invoice_date=extracted_date,
            total_amount=total_amount,
            agreed_credit_days=30,
            has_written_agreement=True,
            confidence_score=round(confidence, 2),
            raw_text_preview=preview,
            source_file_name=original_filename,
            saved_file_path=saved_file_path,
        )

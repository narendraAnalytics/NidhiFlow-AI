EXTRACTION_PROMPT_TEMPLATE = """You are extracting structured borrower information from an OCR'd Indian loan document, for a lending platform where a human underwriter makes the final decision. Accuracy matters more than completeness.

Document type as declared at upload: {document_type}

OCR markdown content:
---
{markdown}
---

Rules — follow all of them:
1. Only extract a value if it is explicitly present in the text above. Never infer, calculate, guess, or autocomplete a value from partial information, context, or general knowledge.
2. If a field is not present, illegible, or you are not reasonably sure, leave it null. A null field is always better than a wrong one.
3. Preserve the original formatting of dates and numbers exactly as printed — do not reformat, normalize, or correct them.
4. `id_number` is the PAN number for a PAN Card, the Aadhaar number for an Aadhaar card, or the relevant identifying number for other document types — leave it null if not applicable to this document type.
5. `detected_document_type` is your own independent best guess at what kind of document this text actually is (e.g. "PAN Card", "Salary Slip"), regardless of the declared type above — this is used to flag a mismatch if the declared type looks wrong, so answer honestly even if it disagrees with the declared type.
6. `monthly_income` must be an amount explicitly stated in the document (e.g. printed on a salary slip) — never derive it from unrelated figures.
7. Set `confidence` (0.0-1.0) to reflect how certain you are that the fields above are correct given the text quality — lower it for blurry OCR, cut-off text, or anything you had to read carefully to make out.
8. Use `notes` to flag anything a human reviewer should double-check (partially obscured text, inconsistent formatting, multiple candidate values for the same field, etc.) — leave it null if there is nothing notable.
"""


def build_extraction_prompt(document_type: str, markdown: str) -> str:
    return EXTRACTION_PROMPT_TEMPLATE.format(document_type=document_type, markdown=markdown)

EXTRACTION_PROMPT_TEMPLATE = """You are extracting structured borrower information from an OCR'd Indian loan document.

Document type as declared at upload: {document_type}

OCR markdown content:
---
{markdown}
---

Extract the fields that are actually present and relevant to a "{document_type}" document. Leave a field null if it is not present in the text — never guess or fabricate a value. `id_number` should be the PAN number for a PAN Card, or the Aadhaar number for an Aadhaar card, or the relevant identifying number for other document types (leave null if not applicable). `detected_document_type` should be your own best guess at what kind of document this text actually is, independent of the declared type above, so a mismatch can be flagged if the declared type looks wrong.
"""


def build_extraction_prompt(document_type: str, markdown: str) -> str:
    return EXTRACTION_PROMPT_TEMPLATE.format(document_type=document_type, markdown=markdown)

import json
import re
from langchain_community.chat_models import ChatOCIGenAI


PROMPT_TEMPLATE = """You are an expert invoice analyst. Analyze the following invoice text carefully.

Return ONLY a valid JSON object with this exact structure (no extra text, no markdown):
{{
  "vendor": "vendor name or Unknown",
  "invoice_number": "invoice number or Unknown",
  "date": "invoice date or Unknown",
  "currency": "currency symbol or $",
  "line_items": [
    {{"description": "item name", "quantity": 1, "unit_price": 0.00, "total": 0.00}}
  ],
  "subtotal": 0.00,
  "tax": 0.00,
  "total_amount": 0.00,
  "anomalies": ["list any issues found: duplicate items, math errors, missing fields, suspicious amounts"],
  "summary": "2-sentence plain English summary of this invoice"
}}

Invoice Text:
{extracted_text}"""


def analyze_invoice(extracted_text: str, compartment_id: str, config_path: str = "~/.oci/config") -> dict:

    llm = ChatOCIGenAI(
        model_id="cohere.command-a-03-2025",
        compartment_id=compartment_id,
        model_kwargs={"temperature": 0, "max_tokens": 1500},
        auth_profile="DEFAULT",
    )

    prompt = PROMPT_TEMPLATE.format(extracted_text=extracted_text[:4000])
    response = llm.invoke(prompt)
    raw_text = response.content

    return parse_json_response(raw_text)


def parse_json_response(raw_text: str) -> dict:
    """Safely parse JSON from model response."""
    clean = re.sub(r"```json|```", "", raw_text).strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "vendor": "Unknown",
            "invoice_number": "Unknown",
            "date": "Unknown",
            "currency": "$",
            "line_items": [],
            "subtotal": 0,
            "tax": 0,
            "total_amount": 0,
            "anomalies": ["Could not parse structured data from invoice."],
            "summary": raw_text[:500],
        }
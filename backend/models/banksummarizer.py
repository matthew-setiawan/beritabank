import os
import sys
import json
from typing import Any, Dict, List, Union
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Ensure project root (backend) is on sys.path so we can import utils
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from utils.gemini_utils import call_gemini

# Load env (for MongoDB connection)
load_dotenv()


def summarize_bank_info(bank_name: str, country: str = "Indonesia") -> Dict[str, Any]:
    """
    Use GPT to research and return structured information about a bank's deposit product.

    Args:
        bank_name: Bank name (e.g., "Bank BCA")
        country: Optional country context to guide GPT

    Returns:
        dict with keys:
          - name (str)
          - logo_url (str)
          - rating (float)
          - deposit_name (str)
          - minimum_deposit (int)
          - interest_rate (float)
          - tenure_options (list[int])
          - early_withdrawal (str)
          - fees (float or int)
          - insurance (str)
          - application_method (list[str])
        or an error dict { success: False, error: ... }
    """
    prompt = f"""
You are a financial research assistant. Deeply research the bank below and output JSON ONLY, no extra text.
If a field is unknown, infer the most reasonable value from public information, otherwise put null.
Ensure the output is STRICT valid JSON.

Bank: {bank_name}
Country context: {country}

Return a JSON shape similar to the one below as example, but data based on what you deep researched:
{{
  "name": "{bank_name}",
  "logo_url": "https://...",
  "website_url": "https://...",
  "rating": 4.7,
  "deposit_name": "Deposito ...",
  "minimum_deposit": 10000000,
  "interest_rate": 3.5,
  "tenure_options": [1, 3, 6, 12],
  "early_withdrawal": "Not allowed",
  "fees": 0,
  "insurance": "Covered by LPS",
  "application_method": ["Online", "Branch"],
  "desc": "Short analysis: overall health, recent positive/negative news, developments, awards.",
  "desc_id": "Analisis singkat: kesehatan keseluruhan, berita positif/negatif terkini, perkembangan, penghargaan.",
  "bank_type": "bpr"
}}

Rules:
- rating is a float from 1.0-5.0 based on reputation and consumer sentiment.
- interest_rate use the highest you can find on this so based on their highest terms.
- minimum_deposit is integer in local currency (IDR for Indonesia).
- tenure_options are integers in months.
- fees is a number (0 if none apparent).
- Use realistic, current-seeming numbers. If uncertain, give conservative, reasonable estimates.
- Output JSON ONLY. No commentary.
- desc is a concise paragraph in English summarizing: (1) overall health, (2) recent positive/negative news, (3) recent developments, (4) notable awards.
- desc_id is the Indonesian translation of the desc field, maintaining the same structure and content.
- bank_type must be one of: "bpr" (regional/BPR) or "umum" (bank umum).
- website_url is the official homepage of the bank (HTTPS preferred, no trackers or query params if possible).
"""

    result_text = call_gemini(
        prompt,
        model="gemini-1.5-pro",
        temperature=0.0,
        google_search_retrieval=True,
    )

    # Handle API errors returned as strings starting with "Error:"
    if isinstance(result_text, str) and result_text.startswith("Error:"):
        return {"success": False, "error": result_text}

    # Try to parse JSON; if fails, attempt to extract JSON substring
    parsed: Dict[str, Any]
    try:
        parsed = json.loads(result_text)
    except json.JSONDecodeError:
        # Attempt to find the first and last curly braces segment
        try:
            start = result_text.find("{")
            end = result_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                parsed = json.loads(result_text[start : end + 1])
            else:
                return {"success": False, "error": "Failed to parse JSON from GPT response"}
        except Exception as e:
            return {"success": False, "error": f"Failed to parse JSON: {str(e)}"}

    # Coerce and validate fields with sensible defaults
    def to_float(v: Any, default: float = 0.0) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    def to_int(v: Any, default: int = 0) -> int:
        try:
            f = float(v)
            return int(f)
        except (TypeError, ValueError):
            return default

    def to_int_list(v: Any) -> List[int]:
        if isinstance(v, list):
            out: List[int] = []
            for item in v:
                try:
                    out.append(int(float(item)))
                except Exception:
                    continue
            return out
        return []

    def to_str(v: Any) -> str:
        return "" if v is None else str(v)

    def to_str_list(v: Any) -> List[str]:
        if isinstance(v, list):
            return [to_str(x) for x in v if to_str(x)]
        return []

    normalized: Dict[str, Union[str, float, int, List[int], List[str]]] = {
        "name": to_str(parsed.get("name") or bank_name),
        "logo_url": to_str(parsed.get("logo_url")),
        "website_url": to_str(parsed.get("website_url")),
        "rating": to_float(parsed.get("rating"), 0.0),
        "deposit_name": to_str(parsed.get("deposit_name")),
        "minimum_deposit": to_int(parsed.get("minimum_deposit"), 0),
        "interest_rate": to_float(parsed.get("interest_rate"), 0.0),
        "tenure_options": to_int_list(parsed.get("tenure_options")),
        "early_withdrawal": to_str(parsed.get("early_withdrawal")),
        "fees": to_float(parsed.get("fees"), 0.0),
        "insurance": to_str(parsed.get("insurance")),
        "application_method": to_str_list(parsed.get("application_method")),
        "desc": to_str(parsed.get("desc")),
        "desc_id": to_str(parsed.get("desc_id")),
        "bank_type": (to_str(parsed.get("bank_type")).lower() if to_str(parsed.get("bank_type")) in ["bpr", "umum", "BPR", "UMUM"] else ("bpr" if "bpr" in bank_name.lower() else "umum")),
    }

    # Try to fetch a logo image using our image retriever if not provided or if caller prefers fresh fetch
    try:
        try:
            # Relative import when used as a package
            from .imageretriever import get_first_image_url  # type: ignore
        except ImportError:
            try:
                # Absolute import when running from project root
                from models.imageretriever import get_first_image_url  # type: ignore
            except ImportError:
                # Add current directory to path when executed directly
                if CURRENT_DIR not in sys.path:
                    sys.path.append(CURRENT_DIR)
                from imageretriever import get_first_image_url  # type: ignore

        query = f"{bank_name} logo"
        img = get_first_image_url(query)
        if img:
            normalized["logo_url"] = img
    except Exception:
        # Keep existing logo_url from model output if retrieval fails
        pass

    return {"success": True, "data": normalized}


def save_bankinfo_to_database(bank_name: str, country: str = "Indonesia") -> Dict[str, Any]:
    """
    Summarize bank information and upsert into MongoDB collection beritabank.bank_information.

    If a bank with the same name exists, update its information instead of inserting a new document.
    """
    try:
        # Summarize via Gemini
        summary = summarize_bank_info(bank_name, country=country)
        if not summary.get("success"):
            return {"success": False, "error": summary.get("error", "Failed to summarize bank info")}

        data: Dict[str, Any] = summary["data"]
        # Ensure bank name is present
        name = data.get("name") or bank_name

        # Prepare Mongo connection
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        if not connection_string:
            return {
                'success': False,
                'error': 'MONGODB_CONNECTION_STRING not found in environment variables'
            }

        client = MongoClient(connection_string)
        db = client['beritabank']
        collection = db['bank_information']

        # Build document
        document = {
            "name": name,
            "logo_url": data.get("logo_url"),
            "website_url": data.get("website_url"),
            "rating": data.get("rating"),
            "deposit_name": data.get("deposit_name"),
            "minimum_deposit": data.get("minimum_deposit"),
            "interest_rate": data.get("interest_rate"),
            "tenure_options": data.get("tenure_options", []),
            "early_withdrawal": data.get("early_withdrawal"),
            "fees": data.get("fees"),
            "insurance": data.get("insurance"),
            "application_method": data.get("application_method", []),
            "desc": data.get("desc"),
            "desc_id": data.get("desc_id"),
            "bank_type": data.get("bank_type"),
            "updated_at": datetime.now().isoformat(),
        }

        # Upsert by bank name
        result = collection.update_one(
            {"name": name},
            {
                "$set": document,
                "$setOnInsert": {"created_at": datetime.now().isoformat()},
            },
            upsert=True,
        )

        operation = "updated" if result.matched_count > 0 else "inserted"

        # Fetch the final document to get _id
        saved = collection.find_one({"name": name})
        saved_id = str(saved["_id"]) if saved else None

        return {
            "success": True,
            "message": f"Bank information {operation} successfully",
            "name": name,
            "database_id": saved_id,
            "operation": operation,
            "data": document,
        }

    except Exception as e:
        return {"success": False, "error": f"Database operation failed: {str(e)}"}


if __name__ == "__main__":
    # Simple manual test
    result = save_bankinfo_to_database("Bank Mayapada", country="Indonesia")
    print(json.dumps(result, indent=2, ensure_ascii=False))
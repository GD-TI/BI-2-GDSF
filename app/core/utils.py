from __future__ import annotations

import base64
import json
import re
import urllib.parse
from datetime import datetime


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_valid_date(date_value: str | None) -> str:
    if not date_value:
        return today()
    try:
        datetime.strptime(date_value, "%Y-%m-%d")
        return date_value
    except ValueError:
        return today()


def format_br_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def format_currency_us_to_br(value: str) -> str:
    raw = value.replace("R$", "").strip().replace(",", "")
    number = float(raw)
    return f"R$ {number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def decode_ranking_payload(encoded: str) -> dict:
    decoded_base64 = base64.b64decode(encoded).decode("utf-8")
    decoded_url = urllib.parse.unquote(decoded_base64)
    return json.loads(decoded_url)


def extract_date_from_filename(filename: str) -> str | None:
    match = re.match(r"^chatguru_log_(\d{4}-\d{2}-\d{2})\.json$", filename)
    return match.group(1) if match else None

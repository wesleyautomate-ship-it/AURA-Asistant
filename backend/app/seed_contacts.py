from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import pathlib
import re
import sys
from urllib.parse import urlparse
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from sqlalchemy import func
from sqlalchemy.orm import Session

# Ensure the backend package is importable when executed as a script.
BACKEND_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.all_models import import_all_models
from app.core.database import get_db_context
from app.domain.listings.enhanced_real_estate_models import EnhancedClient

import_all_models()

logger = logging.getLogger(__name__)

GOOGLE_SHEET_ID = "1twgArJl54BLDeaDyC6WWEmbrPn-b1F0c0SXgSnprvuI"
GOOGLE_SHEET_GID = "1290096536"
DEFAULT_SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export"
    f"?format=csv&gid={GOOGLE_SHEET_GID}"
)

FIELD_ALIASES: Dict[str, Tuple[str, ...]] = {
    "name": (
        "name",
        "full name",
        "contact name",
        "client",
        "client name",
        "display name",
        "file as",
    ),
    "email": ("email", "e-mail", "mail"),
    "phone": (
        "phone",
        "phone number",
        "mobile",
        "mobile number",
        "whatsapp",
        "whatsapp #",
        "contact number",
    ),
    "location": (
        "area",
        "location",
        "preferred area",
        "preferred location",
        "neighbourhood",
        "neighborhood",
    ),
    "budget": (
        "budget",
        "budget (aed)",
        "budget range",
        "price range",
    ),
    "budget_min": (
        "budget min",
        "min budget",
        "minimum budget",
        "min price",
    ),
    "budget_max": (
        "budget max",
        "max budget",
        "maximum budget",
        "max price",
    ),
    "warmth": (
        "warmth",
        "temperature",
        "status",
        "client status",
        "lead status",
        "stage",
    ),
    "pipeline": (
        "pipeline",
        "pipeline stage",
        "funnel stage",
        "deal stage",
        "crm stage",
    ),
    "client_type": (
        "client type",
        "persona",
        "lead type",
        "buyer/seller",
        "type",
    ),
    "notes": ("notes", "context", "comment", "comments", "remarks"),
    "referral_source": (
        "source",
        "lead source",
        "referral",
        "origin",
        "source channel",
    ),
}

STATUS_MAPPING = {
    "active": "active",
    "hot": "active",
    "ready": "active",
    "engaged": "active",
    "warm": "warm",
    "nurture": "warm",
    "lukewarm": "warm",
    "new": "new",
    "prospect": "new",
    "incoming": "new",
    "cold": "cold",
    "idle": "cold",
    "quiet": "cold",
    "dormant": "dormant",
    "lost": "dormant",
    "inactive": "dormant",
    "dead": "dormant",
    "on hold": "dormant",
}

CLIENT_TYPE_MAPPING = {
    "buyer": "buyer",
    "buy": "buyer",
    "tenant": "tenant",
    "rent": "tenant",
    "seller": "seller",
    "sell": "seller",
    "landlord": "landlord",
    "investor": "investor",
}

BUDGET_SUFFIXES = {
    "k": Decimal("1000"),
    "m": Decimal("1000000"),
    "b": Decimal("1000000000"),
}


@dataclass
class ImportSummary:
    total_rows: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "total": self.total_rows,
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "errors": list(self.errors),
        }

    def log_report(self) -> None:
        logger.info(
            "Contacts import complete: total=%s created=%s updated=%s skipped=%s errors=%s",
            self.total_rows,
            self.created,
            self.updated,
            self.skipped,
            len(self.errors),
        )


@dataclass
class NormalizedContact:
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_location: Optional[str] = None
    budget_min: Optional[Decimal] = None
    budget_max: Optional[Decimal] = None
    client_status: Optional[str] = None
    client_type: Optional[str] = None
    referral_source: Optional[str] = None
    notes: Optional[str] = None
    pipeline_stage: Optional[str] = None
    raw: Dict[str, str] = field(default_factory=dict)


def fetch_sheet_csv(sheet_url: str, timeout: int = 20) -> str:
    parsed = urlparse(sheet_url)
    if parsed.scheme == "file":
        path = pathlib.Path(parsed.path)
        if not path.exists():
            raise RuntimeError(f"Local file not found: {path}")
        return path.read_text(encoding="utf-8")

    candidate_path = pathlib.Path(sheet_url)
    if candidate_path.exists():
        return candidate_path.read_text(encoding="utf-8")

    response = requests.get(sheet_url, timeout=timeout)
    if response.status_code == 401:
        raise RuntimeError(
            "Google Sheet returned 401 Unauthorized. Share the sheet with 'Anyone with the link' "
            "or provide credentials before retrying."
        )
    if response.status_code >= 400:
        raise RuntimeError(
            f"Failed to fetch Google Sheet (status {response.status_code})"
        )
    response.encoding = response.encoding or "utf-8"
    return response.text


def parse_contacts_from_csv(csv_text: str) -> Iterable[Dict[str, str]]:
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        # Preserve exact column names for diagnostics
        yield {k: (v or "").strip() for k, v in row.items()}


def normalize_contact(row: Dict[str, str]) -> Optional[NormalizedContact]:
    lookup_items = [
        (key.strip().lower(), value)
        for key, value in row.items()
    ]
    lookup = dict(lookup_items)

    def extract(*aliases: str) -> Optional[str]:
        for alias in aliases:
            alias_norm = alias.strip().lower()
            for key, value in lookup_items:
                if alias_norm == key:
                    candidate = value
                elif key.startswith(alias_norm):
                    next_index = len(alias_norm)
                    if next_index < len(key) and key[next_index].isalpha():
                        continue
                    candidate = value
                else:
                    continue

                if "label" in key and alias_norm in {"phone", "mobile", "phone number"}:
                    continue
                if "label" in key and alias_norm in {"email", "e-mail", "mail"}:
                    continue

                if candidate:
                    cleaned = " ".join(candidate.split())
                    if cleaned:
                        return cleaned
        return None

    name = extract(*FIELD_ALIASES["name"])
    if not name:
        first = extract("first name", "given name")
        last = extract("last name", "surname", "family name")
        if first or last:
            parts = [part for part in [first, last] if part]
            name = " ".join(parts)

    if not name:
        return None

    email = _normalize_email(extract(*FIELD_ALIASES["email"]))
    phone = _normalize_phone(extract(*FIELD_ALIASES["phone"]))
    if not email and not phone:
        return None

    preferred_location = extract(*FIELD_ALIASES["location"])
    notes = extract(*FIELD_ALIASES["notes"])
    referral_source = extract(*FIELD_ALIASES["referral_source"])

    budget_min, budget_max = _extract_budgets(lookup)

    status_raw = extract(*FIELD_ALIASES["warmth"])
    status = _normalize_status(status_raw)
    pipeline_stage = extract(*FIELD_ALIASES["pipeline"])

    client_type_raw = extract(*FIELD_ALIASES["client_type"])
    client_type = _normalize_client_type(client_type_raw)

    return NormalizedContact(
        name=_normalize_name(name),
        email=email,
        phone=phone,
        preferred_location=preferred_location,
        budget_min=budget_min,
        budget_max=budget_max,
        client_status=status,
        client_type=client_type,
        referral_source=referral_source,
        notes=notes,
        pipeline_stage=pipeline_stage.title() if pipeline_stage else None,
        raw=row,
    )


def _normalize_name(value: str) -> str:
    compact = " ".join(part for part in value.split() if part)
    if compact.isupper():
        return compact.title()
    return compact


def _normalize_email(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    email = value.strip().lower()
    if not re.match(r"^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$", email):
        return None
    return email


def _normalize_phone(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    stripped = re.sub(r"[^\d+]", "", value)
    if not stripped:
        return None
    if stripped.startswith("+"):
        digits = "+" + re.sub(r"\D", "", stripped)
    else:
        digits_only = re.sub(r"\D", "", stripped)
        if digits_only.startswith("00"):
            digits_only = digits_only[2:]
        if digits_only.startswith("0"):
            digits_only = digits_only[1:]
        digits = "+" + digits_only if digits_only else None
    if not digits or len(digits) < 6:
        return None
    return digits


def _extract_budgets(lookup: Dict[str, str]) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    min_candidate = _parse_budget_string(
        _first_value(lookup, FIELD_ALIASES["budget_min"])
    )
    max_candidate = _parse_budget_string(
        _first_value(lookup, FIELD_ALIASES["budget_max"])
    )
    if min_candidate or max_candidate:
        return min_candidate, max_candidate

    budget_raw = _first_value(lookup, FIELD_ALIASES["budget"])
    if not budget_raw:
        return None, None

    parts = re.split(r"\s*(?:-|to|–)\s*", budget_raw.lower())
    amounts = [
        _parse_budget_string(part)
        for part in parts
        if part
    ]
    amounts = [amt for amt in amounts if amt is not None]
    if not amounts:
        single = _parse_budget_string(budget_raw)
        return single, single
    if len(amounts) == 1:
        return amounts[0], amounts[0]
    return min(amounts), max(amounts)


def _first_value(lookup: Dict[str, str], aliases: Tuple[str, ...]) -> Optional[str]:
    for alias in aliases:
        value = lookup.get(alias)
        if value:
            return value
    return None


def _parse_budget_string(raw: Optional[str]) -> Optional[Decimal]:
    if not raw:
        return None
    text = raw.strip().lower()
    text = text.replace("aed", "").replace(",", "").replace(" ", "")
    match = re.match(r"([0-9]*\.?[0-9]+)([kmb]?)", text)
    if not match:
        return None
    number, suffix = match.groups()
    try:
        value = Decimal(number)
    except InvalidOperation:
        return None
    multiplier = BUDGET_SUFFIXES.get(suffix, Decimal(1))
    return (value * multiplier).quantize(Decimal("1")) if multiplier != 1 else value


def _normalize_status(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    key = value.strip().lower()
    key = re.sub(r"[^a-z ]", "", key)
    return STATUS_MAPPING.get(key)


def _normalize_client_type(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    key = value.strip().lower()
    key = re.sub(r"[^a-z]", "", key)
    return CLIENT_TYPE_MAPPING.get(key)


def import_contacts_from_google_sheet(
    db: Session,
    sheet_url: str = DEFAULT_SHEET_URL,
) -> ImportSummary:
    summary = ImportSummary()
    csv_text = fetch_sheet_csv(sheet_url)
    for row in parse_contacts_from_csv(csv_text):
        summary.total_rows += 1
        try:
            normalized = normalize_contact(row)
            if not normalized:
                summary.skipped += 1
                continue
            result = _upsert_contact(db, normalized)
            if result == "created":
                summary.created += 1
            elif result == "updated":
                summary.updated += 1
            else:
                summary.skipped += 1
        except Exception as exc:  # noqa: BLE001
            message = f"Row {summary.total_rows} failed: {exc}"
            logger.exception(message)
            summary.errors.append(message)
            summary.skipped += 1
    summary.log_report()
    return summary


def _upsert_contact(db: Session, contact: NormalizedContact) -> str:
    existing = None
    if contact.email:
        existing = (
            db.query(EnhancedClient)
            .filter(func.lower(EnhancedClient.email) == contact.email)
            .first()
        )
    if not existing and contact.phone:
        existing = (
            db.query(EnhancedClient)
            .filter(EnhancedClient.phone == contact.phone)
            .first()
        )

    if existing:
        return _update_contact(existing, contact)

    entry = EnhancedClient(
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        preferred_location=contact.preferred_location,
        budget_min=contact.budget_min,
        budget_max=contact.budget_max,
        client_status=contact.client_status or "warm",
        client_type=contact.client_type or "buyer",
        referral_source=contact.referral_source,
        requirements=contact.notes,
        preferences=_build_preferences(contact, {}),
        last_activity_at=datetime.utcnow(),
    )
    db.add(entry)
    return "created"


def _update_contact(existing: EnhancedClient, contact: NormalizedContact) -> str:
    changed = False

    if contact.name and contact.name != existing.name:
        existing.name = contact.name
        changed = True

    def update_if_new(attr: str, value: Optional[str]) -> None:
        nonlocal changed
        if value and getattr(existing, attr) != value:
            setattr(existing, attr, value)
            changed = True

    update_if_new("email", contact.email)
    update_if_new("phone", contact.phone)
    update_if_new("preferred_location", contact.preferred_location)
    update_if_new("client_status", contact.client_status)
    update_if_new("client_type", contact.client_type)
    update_if_new("referral_source", contact.referral_source)

    if contact.notes and contact.notes != getattr(existing, "requirements", None):
        existing.requirements = contact.notes
        changed = True

    for attr, value in (("budget_min", contact.budget_min), ("budget_max", contact.budget_max)):
        if value is not None:
            current = getattr(existing, attr)
            if current is None or current != value:
                setattr(existing, attr, value)
                changed = True

    preferences = _as_dict(existing.preferences)
    merged_prefs = _build_preferences(contact, preferences)
    if merged_prefs != preferences:
        existing.preferences = merged_prefs
        changed = True

    if changed:
        existing.updated_at = datetime.utcnow()
        return "updated"
    return "unchanged"


def _build_preferences(contact: NormalizedContact, base: Dict[str, object]) -> Dict[str, object]:
    prefs = dict(base or {})
    if contact.pipeline_stage:
        prefs["pipeline_stage"] = contact.pipeline_stage
    if contact.client_status:
        prefs.setdefault("status_label", contact.client_status.title())
    if contact.raw:
        prefs.setdefault("import_source", "google_sheet")
    return prefs


def _as_dict(value: object) -> Dict[str, object]:
    if not value:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {}
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed contacts from Google Sheet.")
    parser.add_argument(
        "--sheet-url",
        default=DEFAULT_SHEET_URL,
        help="CSV export URL for the Google Sheet.",
    )
    args = parser.parse_args()

    with get_db_context() as db:
        summary = import_contacts_from_google_sheet(db, sheet_url=args.sheet_url)
        if summary.errors:
            print("Completed with errors:")
            for error in summary.errors:
                print(f" - {error}")
        print(
            f"Contacts created={summary.created}, updated={summary.updated}, skipped={summary.skipped}, total={summary.total_rows}"
        )


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

# Ensure application packages resolve even when executed as a script.
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.all_models import import_all_models
from app.core.database import get_db_context
from app.domain.listings.enhanced_real_estate_models import (
    EnhancedClient,
    EnhancedProperty,
    MarketData,
    NeighborhoodProfile,
    Transaction,
)

import_all_models()

logger = logging.getLogger(__name__)

DEFAULT_DATA_DIR = ROOT_DIR.parent / "data"


@dataclass
class UpsertStats:
    created: int = 0
    updated: int = 0
    skipped: int = 0

    def record(self, status: str) -> None:
        if status == "created":
            self.created += 1
        elif status == "updated":
            self.updated += 1
        else:
            self.skipped += 1

    def summary(self) -> str:
        return f"created={self.created} updated={self.updated} skipped={self.skipped}"


def load_csv(path: Path) -> Iterable[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield {k.strip(): (v or "").strip() for k, v in row.items()}


def parse_list_field(raw: str) -> List[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
        if isinstance(value, list):
            return [str(item).strip() for item in value if item]
    except (json.JSONDecodeError, TypeError, ValueError):
        pass
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_decimal(raw: str) -> Optional[Decimal]:
    if not raw:
        return None
    cleaned = raw.replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_float(raw: str) -> Optional[float]:
    value = parse_decimal(raw)
    return float(value) if value is not None else None


def parse_int(raw: str) -> Optional[int]:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def parse_date(raw: str) -> Optional[date]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def parse_budget_range(raw: str) -> Tuple[Optional[Decimal], Optional[Decimal]]:
    if not raw:
        return (None, None)
    text = raw.lower().replace("aed", "").replace(" ", "")

    # Patterns like "2m-3m", "500k-1m", "5m+", "under1m"
    tokens = []
    current = ""
    for ch in text:
        if ch.isdigit() or ch in {".", "k", "m"}:
            current += ch
        elif current:
            tokens.append(current)
            current = ""
    if current:
        tokens.append(current)

    values = [_convert_budget_token(token) for token in tokens]
    values = [val for val in values if val is not None]

    if not values:
        return (None, None)

    if "+" in text and values:
        return (min(values), None)

    if "under" in text and values:
        return (None, max(values))

    if len(values) == 1:
        return (values[0], values[0])
    return (min(values), max(values))


def _convert_budget_token(token: str) -> Optional[Decimal]:
    multiplier = Decimal(1)
    if token.endswith("k"):
        multiplier = Decimal(1_000)
        token = token[:-1]
    elif token.endswith("m"):
        multiplier = Decimal(1_000_000)
        token = token[:-1]

    try:
        return Decimal(token) * multiplier
    except InvalidOperation:
        return None


def normalize_phone(raw: str) -> Optional[str]:
    if not raw:
        return None
    digits = "".join(ch for ch in raw if ch.isdigit() or ch == "+")
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    if not digits.startswith("+") and digits:
        digits = "+" + digits
    return digits or None


def upsert_clients(session: Session, data_dir: Path) -> Dict[str, int]:
    path = data_dir / "clients.csv"
    stats = UpsertStats()
    mapping: Dict[str, int] = {}
    if not path.exists():
        logger.info("clients.csv not found, skipping client seed")
        return mapping

    logger.info("Seeding clients from %s", path)
    for row in load_csv(path):
        name_parts = [row.get("first_name", "").strip(), row.get("last_name", "").strip()]
        name = " ".join([part for part in name_parts if part]) or f"Client {row.get('id')}"
        email = row.get("email") or None
        phone = normalize_phone(row.get("phone"))

        query = session.query(EnhancedClient)
        if email:
            existing = query.filter(func.lower(EnhancedClient.email) == email.lower()).first()
        elif phone:
            existing = query.filter(EnhancedClient.phone == phone).first()
        else:
            existing = query.filter(func.lower(EnhancedClient.name) == name.lower()).first()

        budget_min, budget_max = parse_budget_range(row.get("budget_range", ""))
        preferred_areas = parse_list_field(row.get("preferred_areas", ""))
        preferences = parse_list_field(row.get("property_preferences", ""))

        client_status = (row.get("status") or "active").lower()
        client_type = (row.get("client_type") or "buyer").lower()

        if existing:
            updated = False
            if existing.name != name:
                existing.name = name
                updated = True
            if email and existing.email != email:
                existing.email = email
                updated = True
            if phone and existing.phone != phone:
                existing.phone = phone
                updated = True
            if budget_min is not None:
                existing.budget_min = budget_min
                updated = True
            if budget_max is not None:
                existing.budget_max = budget_max
                updated = True
            if preferred_areas:
                existing.preferred_location = ", ".join(preferred_areas)
                updated = True
            if preferences:
                existing.preferences = preferences
                updated = True
            existing.client_status = client_status
            existing.client_type = client_type
            stats.record("updated" if updated else "skipped")
            mapping[row.get("id") or name] = existing.id
        else:
            new_client = EnhancedClient(
                name=name,
                email=email,
                phone=phone,
                budget_min=budget_min,
                budget_max=budget_max,
                preferred_location=", ".join(preferred_areas) if preferred_areas else None,
                preferences=preferences,
                client_type=client_type,
                client_status=client_status,
                referral_source=row.get("source"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(new_client)
            session.flush()
            stats.record("created")
            mapping[row.get("id") or name] = new_client.id

    logger.info("Clients seeded: %s", stats.summary())
    return mapping


def upsert_contractors(session: Session, data_dir: Path) -> Dict[str, int]:
    path = data_dir / "vendors.csv"
    stats = UpsertStats()
    mapping: Dict[str, int] = {}
    if not path.exists():
        logger.info("vendors.csv not found, skipping contractor seed")
        return mapping

    logger.info("Seeding contractors from %s", path)
    for row in load_csv(path):
        name = row.get("vendor_name") or row.get("contact_person") or f"Vendor {row.get('id')}"
        email = row.get("email") or None
        phone = normalize_phone(row.get("phone"))

        query = session.query(EnhancedClient)
        existing = None
        if email:
            existing = query.filter(func.lower(EnhancedClient.email) == email.lower()).first()
        if not existing and phone:
            existing = query.filter(EnhancedClient.phone == phone).first()
        if not existing:
            existing = query.filter(func.lower(EnhancedClient.name) == name.lower()).first()

        preferences = {
            "vendor_type": row.get("vendor_type"),
            "license_number": row.get("license_number"),
            "specializations": parse_list_field(row.get("specializations", "")),
            "rating": row.get("rating"),
            "average_rating": row.get("average_rating"),
            "total_projects": row.get("total_projects"),
            "status": row.get("status"),
        }

        if existing:
            existing.preferences = preferences
            existing.client_type = "vendor"
            existing.client_status = (row.get("status") or "active").lower()
            stats.record("updated")
            mapping[row.get("id") or name] = existing.id
        else:
            contractor = EnhancedClient(
                name=name,
                email=email,
                phone=phone,
                client_type="vendor",
                client_status=(row.get("status") or "active").lower(),
                preferred_location=row.get("address"),
                preferences=preferences,
                relationship_start_date=parse_date(row.get("contract_start_date", "")),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(contractor)
            session.flush()
            stats.record("created")
            mapping[row.get("id") or name] = contractor.id

    logger.info("Contractors seeded: %s", stats.summary())
    return mapping


def upsert_properties(session: Session, data_dir: Path) -> Dict[str, int]:
    path = data_dir / "properties.csv"
    stats = UpsertStats()
    mapping: Dict[str, int] = {}
    if not path.exists():
        logger.info("properties.csv not found, skipping property seed")
        return mapping

    logger.info("Seeding properties from %s", path)
    for row in load_csv(path):
        address = row.get("address") or f"Unknown address #{row.get('id')}"
        area = row.get("area") or row.get("location") or "Dubai"
        property_type = row.get("property_type") or "Property"

        title = f"{property_type} · {area}"
        query = session.query(EnhancedProperty).filter(
            func.lower(EnhancedProperty.description) == address.lower()
        )
        existing = query.first()

        price = parse_decimal(row.get("price_aed", ""))
        sqft = parse_decimal(row.get("square_feet", ""))
        bedrooms = parse_int(row.get("bedrooms"))
        bathrooms = parse_int(row.get("bathrooms"))
        completion = parse_date(row.get("completion_date", ""))
        amenities = [item.strip() for item in (row.get("amenities") or "").split(",") if item.strip()]

        payload = {
            "title": title,
            "description": address,
            "property_type": property_type,
            "price": price,
            "price_aed": price,
            "location": area,
            "area_sqft": sqft,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "developer_name": row.get("developer"),
            "listing_status": (row.get("status") or "available").lower(),
            "features": amenities,
            "view_type": row.get("view"),
            "completion_date": completion,
        }

        if existing:
            for key, value in payload.items():
                if value is not None:
                    setattr(existing, key, value)
            stats.record("updated")
            mapping[row.get("id") or address] = existing.id
        else:
            property_obj = EnhancedProperty(
                **payload,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(property_obj)
            session.flush()
            stats.record("created")
            mapping[row.get("id") or address] = property_obj.id

    logger.info("Properties seeded: %s", stats.summary())
    return mapping


def upsert_market_data(session: Session, data_dir: Path) -> None:
    csv_path = data_dir / "market_data.csv"
    json_path = data_dir / "market_trends.json"
    stats = UpsertStats()

    logger.info("Seeding market data")

    if csv_path.exists():
        for row in load_csv(csv_path):
            area = row.get("neighborhood") or row.get("area") or "Dubai"
            property_type = row.get("category") or "mixed"
            key = (
                session.query(MarketData)
                .filter(
                    func.lower(MarketData.area) == area.lower(),
                    func.lower(MarketData.property_type) == property_type.lower(),
                )
                .first()
            )

            payload = {
                "avg_price": parse_decimal(row.get("avg_price_per_sqft")),
                "price_per_sqft": parse_decimal(row.get("avg_price_per_sqft")),
                "market_trend": row.get("demand_level") or row.get("supply_level"),
                "market_context": {
                    "price_change_3m": row.get("price_change_3m"),
                    "price_change_6m": row.get("price_change_6m"),
                    "price_change_1y": row.get("price_change_1y"),
                    "transaction_volume": row.get("transaction_volume"),
                    "days_on_market": row.get("days_on_market"),
                    "supply_level": row.get("supply_level"),
                    "demand_level": row.get("demand_level"),
                    "source": row.get("source"),
                },
                "data_date": parse_date(row.get("report_date", "")) or date.today(),
            }

            if key:
                for column, value in payload.items():
                    setattr(key, column, value)
                stats.record("updated")
            else:
                session.add(
                    MarketData(
                        area=area,
                        property_type=property_type,
                        **payload,
                    )
                )
                stats.record("created")

    if json_path.exists():
        try:
            records = json.loads(json_path.read_text(encoding="utf-8"))
            trends = records if isinstance(records, list) else records.get("trends", [])
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load %s: %s", json_path, exc)
            trends = []

        for item in trends:
            area = item.get("area") or item.get("neighborhood")
            if not area:
                continue
            property_type = item.get("property_type") or "mixed"
            existing = (
                session.query(MarketData)
                .filter(
                    func.lower(MarketData.area) == area.lower(),
                    func.lower(MarketData.property_type) == property_type.lower(),
                )
                .first()
            )
            payload = {
                "avg_price": parse_decimal(str(item.get("avg_price_aed", ""))),
                "price_per_sqft": parse_decimal(str(item.get("price_per_sqft", ""))),
                "market_trend": item.get("trend"),
                "market_context": item,
                "data_date": parse_date(str(item.get("as_of"))) or date.today(),
            }
            if existing:
                for column, value in payload.items():
                    setattr(existing, column, value)
                stats.record("updated")
            else:
                session.add(
                    MarketData(
                        area=area,
                        property_type=property_type,
                        **payload,
                    )
                )
                stats.record("created")

    logger.info("Market data seeded: %s", stats.summary())


def upsert_neighborhoods(session: Session, data_dir: Path) -> None:
    path = data_dir / "neighborhoods.json"
    stats = UpsertStats()
    if not path.exists():
        logger.info("neighborhoods.json not found, skipping neighborhood seed")
        return

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        records = payload if isinstance(payload, list) else payload.get("value", [])
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to parse %s: %s", path, exc)
        records = []

    for entry in records:
        name = entry.get("name")
        if not name:
            continue
        existing = session.query(NeighborhoodProfile).filter(
            func.lower(NeighborhoodProfile.area_name) == name.lower()
        ).first()
        payload = {
            "amenities": entry.get("amenities") or [],
            "demographics": {
                "top_developers": entry.get("top_developers"),
                "transportation": entry.get("transportation"),
                "description": entry.get("description"),
            },
            "average_rental_yield": parse_decimal(str(entry.get("average_price_per_sqft", ""))),
            "shopping_score": entry.get("shopping_centers"),
            "family_friendly_score": entry.get("parks"),
        }
        if existing:
            for column, value in payload.items():
                setattr(existing, column, value)
            stats.record("updated")
        else:
            session.add(
                NeighborhoodProfile(
                    area_name=name,
                    amenities=payload["amenities"],
                    demographics=payload["demographics"],
                    average_rental_yield=payload["average_rental_yield"],
                    shopping_score=payload["shopping_score"],
                    family_friendly_score=payload["family_friendly_score"],
                )
            )
            stats.record("created")

    logger.info("Neighborhoods seeded: %s", stats.summary())


def upsert_transactions(
    session: Session,
    data_dir: Path,
    property_map: Dict[str, int],
    client_map: Dict[str, int],
) -> None:
    path = data_dir / "transactions.csv"
    if not path.exists():
        logger.info("transactions.csv not found, skipping transactions seed")
        return

    stats = UpsertStats()
    name_cache: Dict[str, int] = {}

    logger.info("Seeding transactions from %s", path)
    for row in load_csv(path):
        external_property_id = row.get("property_id")
        property_id = property_map.get(external_property_id)
        if not property_id:
            logger.debug("Skipping transaction %s — property %s not seeded", row.get("id"), external_property_id)
            stats.record("skipped")
            continue

        transaction_date = parse_date(row.get("transaction_date", "")) or date.today()

        amount = parse_decimal(row.get("amount_aed", ""))
        commission_rate = parse_decimal(row.get("commission_rate", ""))
        commission_amount = parse_decimal(row.get("commission_amount", ""))

        buyer_id = resolve_client(session, row.get("buyer_name"), client_map, name_cache)
        seller_id = resolve_client(session, row.get("seller_name"), client_map, name_cache)

        existing = (
            session.query(Transaction)
            .filter(
                Transaction.property_id == property_id,
                Transaction.transaction_date == transaction_date,
            )
            .first()
        )

        payload = {
            "property_id": property_id,
            "buyer_id": buyer_id,
            "seller_id": seller_id,
            "transaction_type": (row.get("transaction_type") or "sale").lower(),
            "transaction_status": (row.get("status") or "pending").lower(),
            "offer_price": amount,
            "final_price": amount,
            "commission_rate": commission_rate,
            "commission_amount": commission_amount,
            "transaction_date": transaction_date,
            "payment_terms": {"method": row.get("payment_method")},
            "notes": row.get("notes"),
        }

        if existing:
            for column, value in payload.items():
                setattr(existing, column, value)
            stats.record("updated")
        else:
            session.add(Transaction(**payload))
            stats.record("created")

    logger.info("Transactions seeded: %s", stats.summary())


def resolve_client(
    session: Session,
    name: Optional[str],
    client_map: Dict[str, int],
    cache: Dict[str, int],
) -> Optional[int]:
    if not name:
        return None
    key = name.strip()
    if key in cache:
        return cache[key]

    existing = (
        session.query(EnhancedClient)
        .filter(func.lower(EnhancedClient.name) == key.lower())
        .first()
    )
    if existing:
        cache[key] = existing.id
        return existing.id

    # Create lightweight record if missing to preserve linkage.
    fallback = EnhancedClient(
        name=key,
        client_type="buyer",
        client_status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    session.add(fallback)
    session.flush()
    cache[key] = fallback.id
    return fallback.id


def run(data_dir: Path) -> None:
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory {data_dir} does not exist")

    with get_db_context() as session:
        client_map = upsert_clients(session, data_dir)
        contractor_map = upsert_contractors(session, data_dir)
        client_map.update(contractor_map)
        property_map = upsert_properties(session, data_dir)
        upsert_market_data(session, data_dir)
        upsert_neighborhoods(session, data_dir)
        upsert_transactions(session, data_dir, property_map, client_map)
        logger.info("Seeding completed successfully")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed structured domain data from /data directory.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Directory containing CSV/JSON data (defaults to repository /data).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    run(args.data_dir)


if __name__ == "__main__":
    main()


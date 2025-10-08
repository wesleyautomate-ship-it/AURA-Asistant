#!/usr/bin/env python3
"""Minimal smoke checks for Aura services.

Usage:
  python scripts/smoke_tests.py [base_api_url]

If no URL is provided the script defaults to http://localhost:8000.
The backend should be running with DISABLE_AUTH=true so the dev
endpoints used here are reachable without authentication.
"""
from __future__ import annotations

import json
import sys
from typing import Iterable, Tuple

import requests

DEFAULT_BASE = "http://localhost:8000"

Endpoint = Tuple[str, int]


def iter_endpoints(base_url: str) -> Iterable[Endpoint]:
    base = base_url.rstrip("/")
    yield f"{base}/health", 200
    yield f"{base}/api/v1/properties/dev", 200
    yield f"{base}/api/requests/dev", 200
    yield f"{base}/api/v1/tasks/dev", 200


def main() -> int:
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    failures = []

    for url, expected_status in iter_endpoints(base_url):
        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as exc:  # pragma: no cover - runtime validation only
            failures.append((url, f"network error: {exc}"))
            continue

        if response.status_code != expected_status:
            snippet = response.text
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
            failures.append((url, f"expected {expected_status}, got {response.status_code}: {snippet}"))
            continue

        # Pretty-print a short confirmation for visibility
        try:
            payload = response.json()
            preview = json.dumps(payload, indent=2)[:160]
        except ValueError:
            preview = response.text[:160]
        print(f"[OK] {url}\n{preview}\n")

    if failures:
        print("\nSmoke test failures:")
        for url, detail in failures:
            print(f"  - {url}: {detail}")
        return 1

    print("All smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

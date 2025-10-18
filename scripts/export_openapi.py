import json
import sys
from pathlib import Path


def main(out_path: str) -> None:
    # Ensure project root on sys.path
    root = Path(__file__).resolve().parents[1]
    backend_dir = root / "backend"
    for p in (root, backend_dir):
        sp = str(p)
        if sp not in sys.path:
            sys.path.insert(0, sp)

    from backend.app.main import app  # type: ignore

    schema = app.openapi()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    print(f"Wrote OpenAPI schema to {out}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent / "openapi.json")
    main(out)

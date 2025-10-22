"""
Utility script to inspect Alembic revision graph and print an ordered chain.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from alembic.config import Config
from alembic.script import Script, ScriptDirectory


def _load_script_directory() -> ScriptDirectory:
    repo_root = Path(__file__).resolve().parents[1]
    config_path = repo_root / "alembic.ini"
    if not config_path.exists():
        raise SystemExit(f"Could not locate Alembic config at {config_path}")
    config = Config(str(config_path))
    return ScriptDirectory.from_config(config)


def _collect_revisions(directory: ScriptDirectory) -> Dict[str, Script]:
    return {rev.revision: rev for rev in directory.walk_revisions()}


def _format_chain(chain: Sequence[str]) -> str:
    return " -> ".join(chain)


def _get_children_map(revisions: Dict[str, Script]) -> Dict[str, List[str]]:
    children: Dict[str, List[str]] = {}
    for rev in revisions.values():
        down = rev.down_revision
        if not down:
            continue
        downs: Iterable[str]
        if isinstance(down, (tuple, list, set)):
            downs = down
        else:
            downs = (down,)
        for parent in downs:
            children.setdefault(parent, []).append(rev.revision)
    return children


def _ordered_chain(
    start: str, children_map: Dict[str, List[str]]
) -> List[str]:
    chain: List[str] = []
    current = start
    visited: set[str] = set()
    while current:
        if current in visited:
            chain.append(f"[cycle detected at {current}]")
            break
        visited.add(current)
        chain.append(current)
        next_children = children_map.get(current, [])
        if not next_children:
            break
        if len(next_children) > 1:
            print(f"Branch detected at {current}: {next_children}")
        current = next_children[0]
    return chain


def main() -> None:
    directory = _load_script_directory()
    revisions = _collect_revisions(directory)
    if not revisions:
        print("No Alembic revisions found.")
        return

    children_map = _get_children_map(revisions)

    roots = [rev.revision for rev in revisions.values() if not rev.down_revision]
    print(f"Detected {len(revisions)} revision(s).")

    if not roots:
        print("No base revision detected.")
    else:
        for root in roots:
            chain = _ordered_chain(root, children_map)
            print(f"\nChain starting at {root}:")
            print(_format_chain(chain))
            for rev_id in chain:
                rev = revisions.get(rev_id)
                if rev is None:
                    continue
                print(f"  {rev.revision} ({Path(rev.path).name})")

    missing: Dict[str, List[str]] = {}
    for rev in revisions.values():
        down = rev.down_revision
        if not down:
            continue
        downs: Iterable[str]
        if isinstance(down, (tuple, list, set)):
            downs = down
        else:
            downs = (down,)
        for item in downs:
            if item is None or item in revisions:
                continue
            missing.setdefault(rev.revision, []).append(item)

    if missing:
        print("\nMissing down_revision targets detected:")
        for rev_id, targets in missing.items():
            print(f"  {rev_id} references {targets}")
    else:
        print("\nAll down_revision targets resolved.")

    visited_nodes = set()
    for root in roots:
        visited_nodes.update(_ordered_chain(root, children_map))
    orphans = [rev for rev in revisions if rev not in visited_nodes]
    if orphans:
        print("\nRevisions not reachable from any base:")
        for rev_id in orphans:
            rev = revisions[rev_id]
            print(f"  {rev.revision} ({Path(rev.path).name})")
    else:
        print("\nAll revisions reachable from base revision(s).")


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""Validate and deterministically regenerate a docs/contracts registry."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
PLAN_REF_RE = re.compile(r"^[A-Z][A-Z0-9]*-[A-Z0-9][A-Z0-9._-]*$")
SECTIONS_WITH_REFS = ("provides", "artifacts", "state_owned", "invariants")
SECTIONS_WITH_DECLARATIONS = ("provides", "artifacts", "state_owned")
TOP_LEVEL_KEYS = {
    "schema_version", "id", "summary", "owner_paths", "provides", "artifacts",
    "state_owned", "invariants", "depends_on", "module_docs", "extensions",
}
ENTRY_KEYS = {
    "provides": {"name", "kind", "summary", "plan_refs", "declarations"},
    "artifacts": {"name", "summary", "plan_refs", "declarations"},
    "state_owned": {"name", "summary", "plan_refs", "declarations"},
    "invariants": {"statement", "plan_refs"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--contracts-dir", default="docs/contracts")
    parser.add_argument("--write-index", action="store_true")
    return parser.parse_args()


def load_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {path}: {exc}")
    return None


def expect_list_of_strings(value: object, where: str, errors: list[str], *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"{where} must be a list of non-empty strings")
        return []
    if nonempty and not value:
        errors.append(f"{where} must not be empty")
    if len(value) != len(set(value)):
        errors.append(f"{where} contains duplicate values")
    return list(value)


def expect_string(value: object, where: str, errors: list[str], *, nonempty: bool = False) -> str | None:
    if not isinstance(value, str) or (nonempty and not value):
        qualifier = "non-empty " if nonempty else ""
        errors.append(f"{where} must be a {qualifier}string")
        return None
    return value


def reject_unknown_keys(value: dict, allowed: set[str], where: str, errors: list[str]) -> None:
    for key in sorted(set(value) - allowed):
        errors.append(f"{where} has unsupported property: {key}")


def check_local_paths(root: Path, paths: list[str], where: str, errors: list[str]) -> None:
    for raw in paths:
        if "://" in raw:
            errors.append(f"{where} must use repository-local paths, not URI: {raw}")
            continue
        if Path(raw).is_absolute():
            errors.append(f"{where} must use a relative repository path: {raw}")
            continue
        candidate = (root / raw).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            errors.append(f"{where} path escapes repository root: {raw}")
            continue
        if not candidate.exists():
            errors.append(f"{where} path does not exist: {raw}")


def validate_contract(root: Path, path: Path, data: object, errors: list[str]) -> dict | None:
    rel = path.relative_to(root)
    if not isinstance(data, dict):
        errors.append(f"{rel}: top level must be an object")
        return None
    reject_unknown_keys(data, TOP_LEVEL_KEYS, str(rel), errors)
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        errors.append(f"{rel}: schema_version must equal 1")

    sid = data.get("id")
    if not isinstance(sid, str) or not ID_RE.fullmatch(sid):
        errors.append(f"{rel}: id must match {ID_RE.pattern}")
        return None

    if "summary" in data:
        expect_string(data["summary"], f"{rel}: summary", errors)
    if "extensions" in data and not isinstance(data["extensions"], dict):
        errors.append(f"{rel}: extensions must be an object")

    owner_paths = expect_list_of_strings(data.get("owner_paths"), f"{rel}: owner_paths", errors, nonempty=True)
    check_local_paths(root, owner_paths, f"{rel}: owner_paths", errors)
    module_docs = expect_list_of_strings(data.get("module_docs", []), f"{rel}: module_docs", errors)
    check_local_paths(root, module_docs, f"{rel}: module_docs", errors)
    depends_on = expect_list_of_strings(data.get("depends_on", []), f"{rel}: depends_on", errors)
    if sid in depends_on:
        errors.append(f"{rel}: subsystem may not depend on itself")

    plan_refs: set[str] = set()
    for section in SECTIONS_WITH_REFS:
        entries = data.get(section, [])
        if not isinstance(entries, list):
            errors.append(f"{rel}: {section} must be an array")
            continue
        for index, entry in enumerate(entries):
            location = f"{rel}: {section}[{index}]"
            if not isinstance(entry, dict):
                errors.append(f"{location} must be an object")
                continue
            reject_unknown_keys(entry, ENTRY_KEYS[section], location, errors)
            if section == "provides":
                expect_string(entry.get("name"), f"{location}.name", errors, nonempty=True)
                expect_string(entry.get("kind"), f"{location}.kind", errors, nonempty=True)
            elif section in ("artifacts", "state_owned"):
                expect_string(entry.get("name"), f"{location}.name", errors, nonempty=True)
            else:
                expect_string(entry.get("statement"), f"{location}.statement", errors, nonempty=True)
            if "summary" in entry:
                expect_string(entry["summary"], f"{location}.summary", errors)
            refs = expect_list_of_strings(entry.get("plan_refs", []), f"{location}.plan_refs", errors)
            for ref in refs:
                if not PLAN_REF_RE.fullmatch(ref):
                    errors.append(f"{location}.plan_refs has invalid stable ID: {ref}")
                plan_refs.add(ref)
            if section in SECTIONS_WITH_DECLARATIONS:
                declarations = expect_list_of_strings(entry.get("declarations", []), f"{location}.declarations", errors)
                check_local_paths(root, declarations, f"{location}.declarations", errors)

    return {
        "id": sid,
        "owner_paths": sorted(owner_paths),
        "contract": str(path.relative_to(path.parent)),
        "plan_refs": sorted(plan_refs),
        "depends_on": depends_on,
    }


def build_index(records: list[dict]) -> dict:
    ref_index: dict[str, list[str]] = defaultdict(list)
    subsystems = []
    for record in sorted(records, key=lambda item: item["id"]):
        subsystems.append({
            "id": record["id"],
            "owner_paths": record["owner_paths"],
            "contract": record["contract"],
        })
        for ref in record["plan_refs"]:
            ref_index[ref].append(record["id"])
    return {
        "schema_version": 1,
        "generated": True,
        "subsystems": subsystems,
        "plan_refs": {key: sorted(set(value)) for key, value in sorted(ref_index.items())},
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    contracts_dir = (root / args.contracts_dir).resolve()
    errors: list[str] = []

    try:
        contracts_dir.relative_to(root)
    except ValueError:
        print(f"ERROR: contract directory must be inside repository root: {contracts_dir}", file=sys.stderr)
        return 2
    if not contracts_dir.exists() or not contracts_dir.is_dir():
        print(f"ERROR: contract directory does not exist: {contracts_dir}", file=sys.stderr)
        return 2

    contract_files = sorted(path for path in contracts_dir.glob("*.json") if path.name != "index.json")
    records: list[dict] = []
    seen_ids: dict[str, Path] = {}
    for path in contract_files:
        data = load_json(path, errors)
        if data is None:
            continue
        record = validate_contract(root, path, data, errors)
        if record is None:
            continue
        sid = record["id"]
        if sid in seen_ids:
            errors.append(f"duplicate subsystem id {sid!r}: {seen_ids[sid].relative_to(root)} and {path.relative_to(root)}")
        else:
            seen_ids[sid] = path
        records.append(record)

    known_ids = {record["id"] for record in records}
    ref_owners: dict[str, set[str]] = defaultdict(set)
    for record in records:
        for ref in record["plan_refs"]:
            ref_owners[ref].add(record["id"])
        for dependency in record["depends_on"]:
            if dependency not in known_ids:
                errors.append(f"{record['contract']}: unresolved subsystem dependency: {dependency}")
    for ref, owners in sorted(ref_owners.items()):
        if len(owners) > 1:
            errors.append(f"stable plan ref {ref} is mapped to multiple subsystems: {', '.join(sorted(owners))}")

    expected_index = build_index(records)
    index_path = contracts_dir / "index.json"
    if args.write_index and not errors:
        index_path.write_text(canonical_json(expected_index), encoding="utf-8")
    current_index = load_json(index_path, errors)
    if current_index is not None and current_index != expected_index:
        errors.append(f"{index_path.relative_to(root)} is stale or non-canonical; run with --write-index")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"contract registry validation failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"contract registry OK: {len(records)} subsystem(s), {len(expected_index['plan_refs'])} indexed plan ref(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

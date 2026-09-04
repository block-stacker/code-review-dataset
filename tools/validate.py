"""Validate finding records against the schema and against the snippets they cite.

The JSON Schema constrains a record in isolation. It cannot express the
relationships that actually keep the dataset trustworthy: that a record points
at a snippet which exists, that the two agree on language and identifier, and
that the lines a reviewer is told to look at are lines the file really has.
Those checks live here.

Exit status is 0 when every record is consistent and 1 otherwise, so the
script can be used directly as a CI gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import jsonschema

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Problem:
    """One reason a record was rejected, tied to the record that caused it."""

    record: str
    message: str

    def __str__(self) -> str:
        return f"{self.record}: {self.message}"


def iter_finding_paths(findings_dir: Path) -> Iterator[Path]:
    """Yield every finding record, ordered so output is stable across machines."""
    yield from sorted(findings_dir.rglob("*.json"))


def load_json(path: Path) -> Any:
    """Read one JSON document, raising ValueError with the path on malformed input."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def check_schema(record: Any, schema: dict[str, Any], name: str) -> list[Problem]:
    """Collect every schema violation, rather than stopping at the first."""
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    problems = []
    for error in sorted(validator.iter_errors(record), key=lambda e: list(e.path)):
        location = ".".join(str(part) for part in error.path) or "(root)"
        problems.append(Problem(name, f"{location}: {error.message}"))
    return problems


def check_cross_references(
    path: Path, record: dict[str, Any], repo_root: Path
) -> list[Problem]:
    """Check the claims a record makes about the world outside itself.

    Only runs on records that already satisfy the schema, so the fields it
    reads are known to be present and of the right type.
    """
    name = path.name
    problems: list[Problem] = []

    if record["id"] != path.stem:
        problems.append(
            Problem(name, f"id {record['id']!r} does not match filename stem {path.stem!r}")
        )

    directory = path.parent.name
    if record["language"] != directory:
        problems.append(
            Problem(name, f"language {record['language']!r} but filed under {directory!r}")
        )

    snippet = repo_root / record["snippet"]
    if not snippet.is_file():
        problems.append(Problem(name, f"snippet not found: {record['snippet']}"))
        # Every remaining check reads the snippet, so there is nothing more to say.
        return problems

    if not snippet.name.startswith(record["id"]):
        problems.append(
            Problem(name, f"snippet {snippet.name!r} is not prefixed with id {record['id']!r}")
        )

    line_count = len(snippet.read_text(encoding="utf-8").splitlines())
    for line in record["defect_lines"]:
        if line > line_count:
            problems.append(
                Problem(name, f"defect_lines cites line {line}, but the snippet has {line_count}")
            )

    return problems


def check_unique_ids(records: dict[str, dict[str, Any]]) -> list[Problem]:
    """Report ids claimed by more than one record.

    Filenames already make collisions impossible within a directory, so this
    only catches the same id reused across languages.
    """
    seen: dict[str, str] = {}
    problems: list[Problem] = []
    for name, record in sorted(records.items()):
        identifier = record.get("id")
        if not isinstance(identifier, str):
            continue
        if identifier in seen:
            problems.append(Problem(name, f"id {identifier!r} already used by {seen[identifier]}"))
        else:
            seen[identifier] = name
    return problems


def validate_all(repo_root: Path = REPO_ROOT) -> list[Problem]:
    """Validate the whole dataset and return every problem found."""
    schema = load_json(repo_root / "schema" / "finding.schema.json")
    findings_dir = repo_root / "findings"

    problems: list[Problem] = []
    valid_records: dict[str, dict[str, Any]] = {}

    paths = list(iter_finding_paths(findings_dir))
    if not paths:
        return [Problem("findings/", "no finding records found")]

    for path in paths:
        try:
            record = load_json(path)
        except ValueError as exc:
            problems.append(Problem(path.name, str(exc)))
            continue

        schema_problems = check_schema(record, schema, path.name)
        problems.extend(schema_problems)
        if schema_problems:
            # Cross-reference checks assume well-formed fields.
            continue

        problems.extend(check_cross_references(path, record, repo_root))
        valid_records[path.name] = record

    problems.extend(check_unique_ids(valid_records))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to validate (default: the repository containing this script).",
    )
    args = parser.parse_args(argv)

    problems = validate_all(args.repo_root)
    for problem in problems:
        print(problem, file=sys.stderr)

    count = len(list(iter_finding_paths(args.repo_root / "findings")))
    if problems:
        print(f"\n{len(problems)} problem(s) across {count} record(s)", file=sys.stderr)
        return 1

    print(f"{count} record(s) valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

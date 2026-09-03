# code-review-dataset

A small, hand-annotated dataset of real defects in Python and TypeScript.

Each entry pairs a short, self-contained code snippet with a structured review
finding: where the defect is, the mechanism that makes it wrong, the concrete
input that triggers it, and a fix with its rationale.

## Why this exists

Most "buggy code" collections are exercises: the defect is obvious, the snippet
is artificial, and the answer is a single line. That is not what code review
looks like.

The constraint this dataset holds itself to is that **every snippet is accepted
by the toolchain**. The Python files import and run. The TypeScript files
compile under `strict: true`. Nothing here is caught by a compiler, a type
checker, or a default linter configuration — each defect requires a reader who
understands the runtime semantics of the language.

That makes the dataset useful for two things:

- **Evaluating reviewers**, human or model, on defects that survive automated tooling.
- **Calibrating severity**, since each finding carries an explicit trigger rather than a vague warning.

## Layout

```
snippets/{python,typescript}/   Code under review. Each file compiles and runs.
findings/{python,typescript}/   One JSON record per snippet.
schema/finding.schema.json      The record format, as JSON Schema.
tools/                          Validation, statistics, and catalog generation.
docs/CATALOG.md                 Generated, human-readable index of all findings.
ANNOTATION_GUIDE.md             Severity and category definitions.
```

Snippet and finding are linked by a shared id: `snippets/python/py-001_*.py`
is described by `findings/python/py-001.json`.

## A record

Every finding answers the same questions in the same order:

| Field | Question it answers |
| --- | --- |
| `title` | What is the defect, in one line? |
| `defect_lines` | Which lines would you point at in review? |
| `explanation` | What is the mechanism? Why does the language behave this way? |
| `trigger` | What concrete input or interleaving produces the wrong result? |
| `observed` / `expected` | What happens, versus what the code plainly intends? |
| `fix` | What is the corrected code? |
| `fix_rationale` | Why that fix, and what it does not address. |
| `distractors` | What looks wrong here but is actually fine? |

The `trigger` field is the one that does the work. A finding without a concrete
failing input is a code-style opinion, not a defect report, and does not belong
in this dataset.

## Usage

```bash
python3 -m pip install jsonschema   # the only dependency
make check                          # validate every record, then run the tests
make catalog                        # regenerate docs/CATALOG.md
make stats                          # composition by language, category, severity
```

## Scope and limits

- 12 findings: 6 Python, 6 TypeScript. Small on purpose — every entry is reviewed rather than generated in bulk.
- Single annotator, so there is no inter-annotator agreement to report yet. Severity reflects one person's calibration against `ANNOTATION_GUIDE.md`.
- Snippets are reduced from patterns common in production code, not copied from any specific codebase.

## License

MIT. See [LICENSE](LICENSE).

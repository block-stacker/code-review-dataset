# code-review-dataset

[![check](https://github.com/block-stacker/code-review-dataset/actions/workflows/check.yml/badge.svg)](https://github.com/block-stacker/code-review-dataset/actions/workflows/check.yml)

A small, hand-annotated dataset of real defects in Python and TypeScript.

Each entry pairs a short, self-contained code snippet with a structured review
finding: where the defect is, the mechanism that makes it wrong, the concrete
input that triggers it, and a fix with its rationale.

**[Browse all 12 findings →](docs/CATALOG.md)**

## Why this exists

Most collections of buggy code are exercises. The defect is obvious, the
snippet is artificial, and the answer is one line long. That is not what code
review looks like.

The constraint this dataset holds itself to is that **every snippet is accepted
by the toolchain**. The Python files import and run to completion. The
TypeScript files compile under `strict`, with `noUncheckedIndexedAccess` and
`exactOptionalPropertyTypes` on as well. Nothing here is caught by a compiler,
a type checker, or a default linter configuration. Each defect requires a
reader who understands the runtime semantics of the language.

CI enforces that constraint on every push rather than leaving it as a claim.

Three of the TypeScript entries are made possible by type-system rules that
exist deliberately — `Promise<void>` being assignable to `void`, `any` being
assignable to anything, a shorter function being assignable to a longer
signature. The annotations name the rule and say why it exists, because
"TypeScript should have caught this" is the wrong lesson to take from them.

## Layout

```
snippets/{python,typescript}/   Code under review. Each file compiles and runs.
findings/{python,typescript}/   One JSON record per snippet.
schema/finding.schema.json      The record format, as JSON Schema.
tools/                          Validation, statistics, and catalog generation.
tests/                          Tests for those tools.
docs/CATALOG.md                 Generated, human-readable index of all findings.
ANNOTATION_GUIDE.md             Severity and category definitions.
CONTRIBUTING.md                 How to add a finding.
```

Snippet and finding are linked by a shared id: `snippets/python/py-001_*.py` is
described by `findings/python/py-001.json`. The validator enforces that link.

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

Two of those carry most of the weight.

`trigger` is what separates a defect report from a code-style opinion. A
finding whose author cannot name a failing input has not finished the analysis,
and does not belong here.

`fix_rationale` is required to say what the fix leaves unaddressed. Most fixes
leave something: an unvalidated boundary, a caller that still needs updating, a
race narrowed rather than closed. A fix presented as total when it is partial
is worse than the original defect, because it ends the conversation.

## Usage

```bash
python3 -m pip install jsonschema   # the only Python dependency
npm ci                              # only needed for the TypeScript typecheck

./check.sh                          # everything CI runs
./check.sh stats                    # composition by language, category, severity
./check.sh catalog                  # regenerate docs/CATALOG.md
```

`docs/CATALOG.md` is generated and committed, so `./check.sh catalog-check`
fails the build if it drifts from the records.

## Scope and limits

Stated plainly, because a dataset that hides its biases is not much use as a
dataset.

- **12 findings, 6 per language.** Small on purpose. Every entry was written and verified individually rather than generated in bulk.
- **Severity is skewed.** Every entry is `high` or `critical`; there is nothing at `medium` or `low`. That reflects what was interesting to write up, not the distribution of defects in real code, and it means the dataset is not a fair sample for calibrating a severity model.
- **Three categories are empty.** `resource-management`, `security`, and `performance` have no entries yet. `./check.sh stats` prints this, so the gap stays visible instead of being rediscovered later.
- **Single annotator.** There is no inter-annotator agreement to report. Severity reflects one person's calibration against [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md), and the close calls are recorded there so a second annotator could reproduce rather than re-argue them.
- **Snippets are reduced from patterns common in production code.** They are not copied from any specific codebase.
- **Every recorded `observed` value was produced by running the code**, not predicted. One consequence: `py-004` was annotated on a UTC+09:00 host, and its output is timezone-dependent by nature. That is the point of the finding.

## License

MIT. See [LICENSE](LICENSE).

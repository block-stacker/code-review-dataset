# Contributing

## Adding a finding

1. **Write the snippet first, and run it.** Put it in `snippets/<language>/` named `<id>_<short_slug>.<ext>`. It must run to completion (Python) or compile under `strict` (TypeScript). If the toolchain complains, the entry does not qualify — see the bar in [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md).

2. **Record what it actually printed.** `observed` is a transcript, not a prediction. Run the snippet, copy the output. Findings have been wrong at this step before, which is why `./check.sh snippets` exists.

3. **Write the finding** as `findings/<language>/<id>.json`. Copy an existing record for the field order. `explanation` should let a reader predict the *next* instance of the defect, not just recognize this one.

4. **Write and verify the fix.** Compile it and run it before writing it down. A fix that has never been executed is a guess.

5. **Fill in `distractors`.** This is the field that separates review from pattern-matching, and the one that catches an annotator who found the defect by recognizing its shape rather than by reading the code. If nothing nearby looks suspicious, the snippet is probably too small to be interesting.

6. **Regenerate and check:**

   ```bash
   ./check.sh catalog
   ./check.sh
   ```

## What gets rejected

- No concrete trigger. "This could be a problem under load" is a worry, not a finding.
- A defect the compiler, type checker, or a default linter already reports.
- Style preferences: naming, formatting, structure.
- A `fix_rationale` that claims the fix is complete without saying what it leaves open.
- A snippet whose defect only exists because the snippet is artificial. If the surrounding code would never be written that way, the finding teaches nothing.

## Severity

Defined in [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md). It describes blast radius
and detectability, never fix difficulty. When a defect is both wrong and quiet,
escalate one level; a silent wrong answer propagates in a way a thrown exception
does not.

If a call is close, add a line to the calibration notes at the end of that
guide explaining which way it went and why. That file is the reason severity
means the same thing in entry 1 and entry 40.

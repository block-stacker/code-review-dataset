# Annotation guide

The rules a record has to follow to enter this dataset. They exist so that
severity means the same thing in entry 1 and entry 40, and so that a second
annotator could reproduce the labels without asking what was intended.

## What qualifies as a finding

A snippet earns an entry only if all four hold:

1. **The toolchain accepts it.** Python imports and runs; TypeScript compiles under `strict: true`. If `tsc` or a default linter already reports it, it belongs in a linter's test suite, not here.
2. **There is a concrete trigger.** A specific input, state, or thread interleaving that produces a wrong result. "This could be a problem under load" is not a trigger.
3. **The intent is legible.** The surrounding code must make clear what the author meant, so that "wrong" is a claim about the code and not about taste.
4. **It is not a style preference.** Naming, formatting, and structure are out of scope regardless of how strongly anyone feels.

## Severity

Severity describes **blast radius and detectability**, not how hard the fix is.
A one-character fix can be critical; a large refactor can be low.

| Severity | Meaning | Test |
| --- | --- | --- |
| `critical` | Silent data loss or corruption, or a security boundary failure. | Would you page someone at night? |
| `high` | Wrong output on realistic input, or a crash on a common path. Usually visible eventually. | Does normal usage hit this? |
| `medium` | Wrong or degraded behavior on an edge case, or a failure that is loud and easy to trace. | Does it need unusual input, or is it obvious when it happens? |
| `low` | A latent hazard that is correct today but breaks under a plausible, unremarkable change. | Is the bug in the future rather than the present? |

The distinction that decides most cases is **silence**. A defect that throws is
easier to live with than one that returns a plausible wrong answer, because the
second one propagates. When a defect is both wrong and quiet, escalate one level.

## Categories

One per finding. Where two apply, choose the one that describes the *cause*, not
the symptom.

| Category | Use for |
| --- | --- |
| `correctness` | Wrong result from a correct-looking expression. The default. |
| `concurrency` | Requires a specific interleaving, ordering, or scheduling to fail. |
| `error-handling` | Failures that are swallowed, mislabeled, or reported as success. |
| `resource-management` | Handles, connections, locks, or memory not released. |
| `type-safety` | A claim about a type that the runtime does not enforce. |
| `api-contract` | Misuse of a documented interface whose signature still typechecks. |
| `security` | Crosses a trust boundary: injection, authz, secrets, unsafe deserialization. |
| `performance` | Complexity or allocation behavior that degrades non-obviously with size. |

## Writing the fields

**`explanation` — the mechanism, not the verdict.**
State why the language behaves this way. "Default arguments are evaluated once,
at function definition time, and the resulting object is stored on the function"
is an explanation. "Mutable defaults are bad practice" is not. A reader who did
not know the rule should be able to predict the next instance of it after
reading this field.

**`trigger` — an input, not a worry.**
Concrete values, or a numbered interleaving for concurrency findings. If you
cannot name the input, you have not finished the analysis.

**`observed` / `expected` — both stated in terms of that trigger.**
Not general descriptions. If the trigger is `add_tag("a")` twice, `observed` is
`["a", "a"]`, not "the list grows".

**`fix_rationale` — including what the fix does not do.**
Most fixes leave something unaddressed: an unvalidated boundary, a caller that
still needs updating, a race narrowed but not eliminated. Say so. A fix
presented as total when it is partial is worse than the original defect,
because it ends the conversation.

**`distractors` — the discipline field.**
Nearby code that looks suspicious but is correct as written. Filling this in is
what separates review from pattern-matching, and it is the field that catches an
annotator who found the defect by recognizing its shape rather than by reading.

## Severity calibration notes

Recorded when a judgment call was close, so the same call is made the same way
next time:

- **Naive/aware datetime mixing** is `high`, not `critical`. It produces wrong comparisons rather than corrupted stored data, and it usually surfaces as a visible off-by-hours bug.
- **Check-then-act on shared state** is `critical` when the lost write is data, `high` when it only causes duplicated work.
- **Unvalidated `as` assertions** are `high` rather than `critical` unless the value crosses a trust boundary, in which case the finding is `security`.
- **Shallow copies** are `high`, not `medium`. The aliasing is invisible at the call site, which is the escalation rule for quiet defects.
- **An unawaited async callback** is `critical` rather than `high`. The wrong return value alone would be `high`, but the discarded promise also means a rejected operation is reported to nobody, and a caller that reads resolution as durability can drop data on the strength of it. Both halves are silent.
- **Lexicographic sort** is `high`, not `critical`. The output is wrong but visibly so, and it does not destroy anything beyond the ordering of the caller's array.

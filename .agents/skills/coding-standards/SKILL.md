---
name: coding-standards
description: >-
  Coding standards and quality rules for writing or editing code in any language.
  Its primary goal is one coherent codebase: every change integrates into the
  existing structure (reuse, relocate, restructure) instead of bolting new code
  on top. Enforces small single-purpose functions (~50 lines), small files (~250
  lines, split via subfolders), clear descriptive names, complete docstrings,
  file-level docstrings, specific try/catch error handling, classes for stateful
  logic, comments on non-obvious decisions, named constants over magic numbers,
  and DRY (reuse existing functions instead of duplicating), and it flags
  AI-slop patterns (over-engineering, verbose comments,
  phantom error handling). Use this skill whenever writing new code, editing or
  refactoring existing code — even if they
  don't explicitly ask for a "standard." Apply it proactively to any code you
  produce, and flag violations you encounter with a concrete suggested fix. Also
  use it to set up automated enforcement — it bundles tuned ruff/ESLint configs,
  a pre-commit config, and a line-limit checker — so use it whenever someone
  wants to add a linter, pre-commit hook, or CI check for code quality.
---

# Coding Standards

**Primary goal: one coherent codebase** — clean, maintainable, readable,
extendable — where every change *integrates into* what's there rather than
bolting on a new layer. Optimize for the reader (a stranger, or you in six
months), and make every line earn its place: if you can't say why it's needed for
*this* problem in *this* codebase, cut it. This matters most for AI-written code,
which tends to *add* rather than fit in. The rules have firm targets, but they
serve readability — when they genuinely conflict with it, keep the code readable
and say so; don't game a metric to "pass" it.

## How to apply

- **Writing new code:** follow these from the start.
- **Editing/reviewing:** hold the code you touch to the standard; flag
  pre-existing violations with a concrete fix, but stay scoped — offer, don't
  sprawl into unrelated rewrites.
- **When a rule can't be met cleanly:** don't violate it silently — state the
  tension and propose the fix (a split, a helper, an extracted class).
- **After a change:** note any violations you left behind and how you'd resolve
  them.
- **Enforcement:** ensure `pre-commit` is installed in the repo (install it,
  don't just offer) — see "Enforcement" below.

## The rules

### 1. Zoom out before you add: integrate, don't bolt on

Fit the change into what's already there. Before writing, ask: **what's the
smallest delta?** **what already exists that I can use?** **what shouldn't I
touch?**

- **Search, then reuse (DRY).** Grep for a function/class/module that already
  does this (by name, keyword, in `utils`/`helpers`/`services`) before writing a
  near-twin; reuse or extend it, and flag existing near-duplicates to consolidate.
- **Converge on one home.** Keep each piece of knowledge (a rule, a validation, a
  calculation) in one authoritative place. When a second module needs existing
  logic, move it somewhere both import rather than copying it — two copies drift.
  Relocate for a *real* second consumer, not a hypothetical one.
- **Group** cohesive loose functions into a class (rule 9); **split** a function
  that outgrew one job (rule 2); **prefer editing** existing structures over
  adding parallel ones. A new file/util/abstraction is the last resort.

**Guardrail — don't over-abstract.** Build for a *present* need, never
speculative generality (YAGNI). 
Good abstractions are discovered, not
forced.

### 2. Small, single-purpose functions (~50 lines)

One function, one job — if you describe it with "and", it's two. Treat ~50 lines
of real logic (not the signature, docstring, or blank lines) as the ceiling; past
it you're usually doing more than one thing, so extract the steps into named
helpers. Length is the symptom; single responsibility is the cure.

### 3. Abstractions: extract coherent steps into named functions

Even without reuse, a block that does one nameable thing reads better as a call:
lift the three lines that format query rows into `format_query_results(rows)` so
the caller reads as intentions ("fetch, format, return"), not mechanics. The
test: if you'd explain a block in a short phrase, that phrase is the function
name. This keeps each function at a *single level of abstraction* —
orchestrating named steps or doing detail work, not both (mixing the two is the
usual reason one blows past rule 2's length target). Don't over-fragment: a
function you'd name `add_one(x)` earns nothing; extract when a name genuinely
helps.

### 4. Small files (~250 lines), split via subfolders

A file past ~250 lines is usually several concerns in a trench coat. The budget
counts **code lines only** — docstring lines are excluded (as they are for the
per-function limit in rule 2), so thorough documentation never pushes a file over.
Split by **subfolder/package**, not more sibling files, and present the structure +
rationale before moving code so the user can steer the boundaries:

```
services/orders/
  __init__.py     # re-exports the public surface
  creation.py     # order creation
  pricing.py      # price + discount calculation
  fulfillment.py  # shipping
```

### 5. Clear, descriptive names

Names are your cheapest documentation. Say what the thing is or does; avoid
single letters and cryptic abbreviations, but don't ramble either.

- Good: `active_users`, `retry_count`, `parse_config`, `elapsed_ms`
- Poor: `d`, `tmp2`, `data`, `doStuff`, `list_of_active_user_account_objects`

Loop indices / math (`i`, `x`, `y`) are fine in tiny scopes that match
convention.

### 6. Docstrings that explain what, how, and the shapes

Every function gets a docstring with: **what** it does (one line), **inputs**
(each arg, type, meaning), **how** it works (high-level approach, not
line-by-line — so it won't rot), and **output** (return type + shape). The "how"
is what makes it more than a signature restatement. Use the examples as the template for all docstrings, and keep them up to date — a stale docstring is worse than none.

The three sections are **machine-checked** (see Enforcement), so mind exactly
when each is required — a blank line must precede each `How:`/`Returns:` header
(Google convention, matched by the example above):

- **`How:`** — always required.
- **`Args:`** — required as soon as the function takes **one or more** real
  parameters (`self`/`cls` don't count). A genuinely no-argument function omits it.
- **`Returns:`** — required when the function returns a value. A void function (no
  `return`, a bare `return`, or `-> None`) omits it rather than documenting `None`.

```python
def parse_timestamps(raw_lines: list[str]) -> list[datetime]:
    """Convert raw log lines into parsed timestamps.

    Args:
        raw_lines: Log lines, each starting with an ISO-8601 timestamp then a
            space and the message.

    How:
        Split each line once on the first space, parse with
        datetime.fromisoformat; unparseable lines are skipped so one bad line
        can't abort the batch.

    Returns:
        Parsed timestamps in original order.
    """
```

TypeScript/JSDoc mirrors this: `@param` for inputs, `@remarks` for the how,
`@returns` for the output.

### 7. File-level docstrings

Every file opens with a short docstring stating its purpose — what lives here
and why this file exists. This is the map a reader consults before diving in.

```python
"""Order pricing: computes subtotals, applies discount rules, and returns the
final payable amount. Pure calculation only — no I/O or persistence."""
```

### 8. Specific error handling

Wrap fallible operations (I/O, parsing, network, external calls) in try/catch,
but the value is *specificity*: catch the errors you expect and raise messages
with context. `except Exception: raise Exception("failed")` hides the bug.

```python
try:
    config = json.loads(raw)
except json.JSONDecodeError as err:
    raise ValueError(f"Config at {path} is not valid JSON: {err}") from err
```

Don't swallow errors or catch broadly to silence a warning. **Fail fast** —
surface bad state early, before it flows deep. **Never log secrets or PII**
(passwords, tokens, keys, personal data).

### 9. Classes for stateful logic (not for grouping functions)

Reach for a class when data and the operations on it travel together and carry
*state* — a connection + its queries, a parser + its buffer, a game + its board.
Otherwise, convention (cf. "Stop Writing Classes") is to avoid them:

- A class whose only methods are `__init__` plus one other is really a function.
- To just group related functions, use a **module**, not a class.
- For a bundle of related values with little behavior, use a **`@dataclass`** (or
  named tuple) rather than a hand-rolled class or passing tuples around.

Name classes for what they *are* (`OrderRepository`, `RetryPolicy`), not
`Manager`/`Helper`/`Utils`.

### 10. Comment the non-obvious

Comments explain *why*, not *what* — magic numbers, edge cases, workarounds. Put
them on their own line **above** the code, not inline (they stay readable and
survive reformatting).

```python
# first 3 chars are the warehouse prefix; rest is the item id
sku = raw_code[:3]
```

Don't narrate the obvious (`# increment i`) — it trains readers to ignore
comments.

### 11. Named constants over magic values

A bare `86400` or `"active"` forces the reader to guess and invites drift. Name
it for intent (`SECONDS_PER_DAY`, `STATUS_ACTIVE`): define it at the top of the
file if used once there, or in a central `constants`/`config` if shared. Obvious
identities (`0`, `1`, `-1`, `""`) don't need names.

## Further principles

- **YAGNI:** build the simplest thing that meets the actual requirement; no
  speculative future-proofing.
- **Few parameters (≤5):** group related args into an object/struct
  (`create_user(user_data)`, not five positional args).
- **Early returns, shallow nesting:** guard-clause early; keep nesting ~3 levels,
  then extract.
- **Isolate side effects:** prefer pure functions; keep I/O in thin, obvious
  layers.
- **No dead code:** delete it, don't comment it out — version control is the
  history.
- **Keep docs in sync:** update the docs a behavior change affects, in the same
  change.

## Naming conventions by language

Match the ecosystem's idioms — code should look native to its language.

| Language      | Functions / vars      | Classes / types    | Constants           |
|---------------|-----------------------|--------------------|---------------------|
| Python        | `snake_case`          | `PascalCase`       | `UPPER_SNAKE_CASE`  |
| TypeScript/JS | `camelCase`           | `PascalCase`       | `UPPER_SNAKE_CASE`  |
| Go            | `camelCase`/`PascalCase` (export = capital) | `PascalCase` | `PascalCase`/`UPPER` |
| Rust          | `snake_case`          | `PascalCase`       | `UPPER_SNAKE_CASE`  |
| Java/C#       | `camelCase`/`PascalCase` | `PascalCase`    | `UPPER_SNAKE_CASE`  |

For a language not listed, follow that language's established community
convention rather than importing another language's style.

## Reviewing

Report violations as a short, actionable list — location, rule, concrete fix —
prioritized by impact (a swallowed exception over a slightly-long name). Leave a
clear next action, not a lecture.

## Enforcement

A linter owns the mechanical rules (line counts, naming casing, docstring
*presence*, param counts, magic values, broad excepts); your judgment owns the
rest (single responsibility, meaningful names, abstraction, integration/DRY).
Docstring **section presence** (rule 6's `Args:`/`How:`/`Returns:`, with the no-arg
and void-return exemptions) is now machine-checked too — by `check.py`, since no
off-the-shelf linter checks the custom `How:` section or gates sections on the
signature. Your judgment still owns docstring *content* — whether the "how" is
accurate and the args are meaningfully described, not just present. Tooling is
vendored in a sibling **`linting/`** folder: `ruff.toml` (Python),
`eslint.config.mjs` (TS/JS), `.pre-commit-config.yaml`, and `check.py` (Python-only:
the 50/250 line checks — file length excludes docstrings — and the docstring-section
checks, all measured over the AST). `check.py` needs only Python 3.9+ stdlib;
`ruff`/`eslint` are optional and it prints install hints if missing. **Run `python
linting/check.py <paths>` after editing and before committing.**

**Setup (once per repo; idempotent, never clobber):**

1. Confirm it's a git repo.
2. Vendor the standard (`.agents/skills/coding-standards/`) and the `linting/`
   folder; symlink `.claude/skills -> ../.agents/skills`.
3. Add a repo-root `ruff.toml` that `extend = "linting/ruff.toml"` and
   `extend-exclude`s vendored/generated trees.
4. Add `ruff` + `pre-commit` (and `eslint` + `typescript-eslint` +
   `eslint-plugin-jsdoc` for TS/JS) to the project manifest.
5. Add the pre-commit config (point the line-limit hook at `linting/check.py`;
   merge into an existing config rather than overwriting), then `pre-commit
   install`.
6. Grandfather an existing backlog (below) so new code is strict without a
   big-bang refactor.
7. Run `ruff check .` + `pre-commit run --all-files` and report what you set up.

If `pre-commit` can't be installed, run `check.py` manually before commits.

**Exceptions** (in the repo `ruff.toml`, each with a why-comment, narrowest
first): `# noqa: RULE` for a one-off · `[lint.per-file-ignores]` to grandfather
existing offenders (find them with `ruff check . --select
PLR0913,PLR0915,PLR0912,C901`) · repo-wide `ignore` only as a last resort. Flag
grandfathered debt rather than hiding it.

`linting/SKILL.md` has the full rule→tool mapping, known gaps, and the legacy
`.eslintrc` translation.

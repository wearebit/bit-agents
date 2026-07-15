# Automating the mechanical checks

The standard splits cleanly in two: rules a machine can verify (line counts,
naming casing, docstring *presence*, parameter counts, magic numbers, broad
excepts) and rules that need judgment (single responsibility, docstring
*content*, meaningful names, the abstraction extraction of rule 2, DRY,
comment-the-why). Let the linters own the first set so the skill's attention
goes to the second — the part a tool genuinely can't do.

Bundled files (in the top-level `linting/` folder, separate from this skill):

- `linting/ruff.toml` — Python, tuned to the standard's thresholds
- `linting/eslint.config.mjs` — TypeScript/JS, flat config (ESLint 9+)
- `linting/.pre-commit-config.yaml` — runs all three checkers on commit
- `linting/check.py` — the exact 50-line / 250-line checks the linters can't do

## Rule → tool mapping

| Standard rule | Python (ruff, unless noted) | TypeScript (eslint) |
|---|---|---|
| 1. Function ≤50 lines | `linting/check.py` (ast, docstrings excluded); `PLR0915` statements proxy | `max-lines-per-function` |
| 3. File ≤250 lines | `linting/check.py` (ast, docstring lines excluded) | `max-lines` |
| 4. Naming casing | `N` (pep8-naming) | `@typescript-eslint/naming-convention` |
| 5/6. Docstring present | `D` (pydocstyle) | `jsdoc/require-jsdoc` + `require-param`/`require-returns` |
| 6. Docstring `Args:`/`How:`/`Returns:` sections | `linting/check.py` (ast; `Args` iff ≥1 param, `Returns` iff returns a value) | `require-param`/`require-returns` (no `How` equivalent) |
| 7. No broad/bare except | `BLE001`, `E722` | `no-empty` (`allowEmptyCatch: false`) |
| 11. Magic numbers | `PLR2004` (comparisons only) | `no-magic-numbers` |
| Few params (≤5) | `PLR0913` | `max-params` |
| Shallow nesting (≤3) | `C90` complexity | `max-depth` |
| No dead code | `F401`/`F841` | `no-unused-vars` |

**Section presence is checked; content quality is not.** `ruff`'s `D` confirms a
docstring *exists*; `check.py` additionally confirms the required `Args:`/`How:`/
`Returns:` **sections** are present (Python only — no off-the-shelf tool checks the
custom `How:` section or gates sections on the signature). What stays a judgment
call is whether those sections are *any good* — whether the "how" is accurate and
the args meaningfully described. Same for names: casing is checkable, but whether
`data` is a *good* name isn't. These stay with the skill.

Gaps worth knowing: ruff's magic-value rule fires only in comparisons, not
assignments, so `timeout = 3600` slips past it — the skill should still name it.
Duplication (DRY) detection isn't wired in by default; add `jscpd` or pylint's
`duplicate-code` if a repo wants it.

## What needs installing

`linting/check.py` needs **only Python 3.9+ (standard library, no packages)** —
the 50-line / 250-line checks always work in a bare environment. `ruff` and
`eslint` are **optional**: without them the runner still does the line checks and
prints an install hint for whatever's missing. Install them to get the naming,
docstring-presence, broad-except, and magic-number coverage too.

## Installing ruff

Pick whichever fits the environment:

```bash
# Simplest — into the current environment
pip install ruff

# Isolated tool install (recommended; no dependency clashes)
pipx install ruff
#   or, with uv:
uv tool install ruff

# Project-local dev dependency
uv pip install ruff        # or: pip install ruff inside a venv you activated
```

Fresh virtualenv, if the machine has none:

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install ruff
```

**Docker — no local install at all.** ruff ships an official image; mount the
repo and run the check inside it:

```bash
docker run --rm -v "$(pwd):/src" -w /src ghcr.io/astral-sh/ruff:latest check .
```

Pin a version by replacing `latest` (e.g. `ghcr.io/astral-sh/ruff:0.6.9`).

## Installing eslint (TypeScript/JS)

eslint runs from the project's own `node_modules`, so install it as a dev
dependency:

```bash
npm i -D eslint typescript-eslint eslint-plugin-jsdoc
npx eslint .
```

Dockerized, without touching the host toolchain:

```bash
docker run --rm -v "$(pwd):/src" -w /src node:20-alpine \
  sh -c "npm i -D eslint typescript-eslint eslint-plugin-jsdoc && npx eslint ."
```

## Setup

**Python:**
```bash
pip install ruff                          # see options above if pip isn't ideal
# ruleset already vendored at linting/ruff.toml; the root ruff.toml extends it
ruff check .
```

**TypeScript/JS:**
```bash
npm i -D eslint typescript-eslint eslint-plugin-jsdoc
cp linting/eslint.config.mjs ./eslint.config.mjs
npx eslint .
```

**Exact line thresholds (any language, no install needed):**
```bash
python linting/check.py .                # or pass specific files/dirs
```

**All of it on every commit:**
```bash
pip install pre-commit
cp linting/.pre-commit-config.yaml ./.pre-commit-config.yaml
pre-commit install
```

## Legacy ESLint (.eslintrc)

Projects still on ESLint 8 / eslintrc can translate `eslint.config.mjs` into
`.eslintrc.json`: move each entry of the `rules` object as-is, add
`"plugins": ["@typescript-eslint", "jsdoc"]`, set
`"parser": "@typescript-eslint/parser"`, and extend
`"plugin:@typescript-eslint/recommended"`. The rule names and options are
identical; only the wrapper differs.

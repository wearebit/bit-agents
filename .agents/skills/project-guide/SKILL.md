---
name: project-guide
description: >-
  Governing skill for THIS repository — read it before doing ANY work here.
  Covers what the project is, how to build/run/test it, its architecture and
  conventions, domain rules, and the repo-specific gotchas an agent must know.
  Use for any task in this repo: features, bug fixes, refactors, reviews, tests,
  or commits. PLACEHOLDER — replace the TODOs with real content and keep it
  current as the project evolves.
---

# Project guide

> **PLACEHOLDER.** Rename this skill (`name:` above and the folder) to something
> specific like `myapp-maintainer`, then fill in every TODO. Delete this quote
> block when you do.

Governing skill for this repository. Any agent (Claude, Codex, Gemini, …) should
read this before working here, so behavior is consistent no matter which tool is
driving.

## What this project is

TODO: One paragraph — what the project does, who it's for, the core idea.

## How to run, build, and test

TODO: The exact commands. Be specific about the interpreter/toolchain (e.g. a
virtualenv or conda path), how to start the app, and how to run the full test
suite. State the command an agent must run to verify a change before committing.

## Architecture

TODO: The main layers/modules and how they fit together, so an agent knows where
a given change belongs. Link related skills with `[[skill-name]]` if you add
more.

## Conventions & gotchas

TODO: Anything non-obvious that would trip up a newcomer — naming rules, data
shapes, ordering constraints, "don't touch X", known sharp edges, required
regeneration steps after certain changes.

## When to ask the user

TODO: The decisions that are the user's call rather than the agent's (domain
semantics, ambiguous requirements, irreversible actions). Prefer asking early
over reworking later.

## Coding standards

Code quality is governed by the `coding-standards` skill and enforced at commit
time by pre-commit (`ruff` + the 50/250 line checks). Apply it to all code.

---

## Maintaining this skill (do not delete)

**This file is the repo's memory for agents. Whenever you learn something an
agent must know to work here safely — a new build/test command, an architectural
boundary, a convention, a gotcha, a "we decided X" — add it here in the same
change.** A fact that lives only in one conversation is lost; a fact recorded
here is available to every agent, every session. Keep entries concise and
current; delete anything that becomes wrong.
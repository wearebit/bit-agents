# Agent instructions

Canonical, tool-neutral instructions for any coding agent working in this repo
(Claude, Codex, Gemini, Copilot, …). Tool-specific entrypoints
(`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`) are symlinks to
this file — edit the **AGENTS.md** file, not the symlinks.

This file stays repo-agnostic: it describes the shared conventions only.
**All repo-specific guidance lives in skills** (see below), never here.

## Skills

Reusable, auto-loaded instructions live in `.agents/skills/<name>/SKILL.md`,
written to the open [Agent Skills](https://agentskills.io) spec (plain markdown +
standard frontmatter, no vendor-specific extensions), so every compliant agent
reads them unmodified. `.claude/skills` is a symlink to `.agents/skills`.

**⚠️  CRITICAL: Before ANY code work, trigger the bit-story-workflow skill.** This repo runs the strict Bit workflow for all coding work. If you are about to write or edit code, you are in this workflow — no exceptions.

**Before working, read the skill(s) relevant to your task:**

- **`bit-story-workflow`** — **THE GOVERNING WORKFLOW** for all code changes in this repo (features, fixes, refactors, edits). Trigger it immediately for any code work. Do not skip this — read it first, every time.
- **`project-guide`** — the governing skill for THIS repo (what it is, how to
  run/build/test, architecture, conventions, gotchas). Read it second, and keep
  it updated whenever you learn something an agent must know.
- **`coding-standards`** — the house style for any code you write or edit.

## Workflow & coding standards enforcement

**You MUST use the bit-story-workflow for ANY code change** — features, bug fixes, refactors, edits, small tweaks, anything. No exceptions. Read the [[bit-story-workflow]] skill for the full process (story intake, clarification, multi-phase planning, step-by-step execution with gates, testing, linting, commit).

Code quality is enforced at the agent level and the **git layer**, so it holds regardless of which agent (or human) writes the code:

- **pre-commit** runs the linter + line-length checks on staged files at commit
  time. Install once per clone: `pre-commit install`.
- The linting machinery is vendored in **`linting/`** (canonical `ruff.toml`
  base config, `check.py` line checker, pre-commit template). The repo's root
  `ruff.toml` extends `linting/ruff.toml` and carries only this repo's
  exceptions. Full rules: `.agents/skills/coding-standards/SKILL.md`.

Do not bypass the hooks (`--no-verify`) to land code that violates the standard. Do not skip the workflow for "quick" changes — treat every request as a story to clarify and plan.

## Aliases

Aliases are reminders of great communication and patterns we want to upload.

When you see these exact aliases, expand them and act as if their expansions were given to you directly.

If these are referenced in a longer string, they are not aliases, do not expand.

scr = `Simplify, compress, and repeat your response.`
eli = `Explain this like I'm 18. Simplify your language. Shorten your response.`
foc = `Focus on what matters most here. Whats the true signal? Whats the true value? Boil your response down into the most important thing we need to focus on.`
ref = `Rewrite your responses with reference points`

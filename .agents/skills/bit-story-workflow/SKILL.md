---
name: bit-story-workflow
description: >-
  The governing workflow for ALL code work in this repo at Bit (an AI prototyping
  studio). Trigger it as soon as anything needs to be implemented, changed, or
  fixed in the codebase — new features, bug fixes, refactors, tweaks — whether or
  not the developer names a story or process. Phrases like "let's work on
  BIT-123", "implement this story", "add X", "fix this bug", "change how Y works",
  or pasting a BitBucket story all trigger it. In practice: if you are about to
  write or edit code here, you are in this workflow. It runs a strict, human-gated
  flow — paste and clarify the story, agree a multi-phase plan, implement one
  small reviewed step at a time, test each phase (automatically and with the
  developer), then lint and commit per phase.
---

# Bit story workflow

The governing process for turning requests into shipped code. Bit is an AI
prototyping studio; requests come as formal stories (in BitBucket), bug reports, feature ideas, or casual asks — all requiring clarification and deliberate execution. This workflow removes vagueness before any code is written and keeps a human developer in control of every change.

**This is the default for all code work here.** If something needs implementing,
changing, or fixing — whether presented as a formal story, bug, feature idea, or simple request — you are in this workflow. No exceptions, no shortcuts. Work strictly through the phases in order. Each phase ends at a human gate; do not start the next phase until the developer approves. The point is deliberate, reviewable progress, not speed.

Two other skills govern the *content* of the work; defer to them:

- Code you write or propose MUST follow [[coding-standards]]. Please read that skill before writing any code.
- Before every commit you must run the checks defined in [[linting]].

## How to talk to the developer

Everything you tell the developer — read-backs, plans, step narration, test
instructions — should be **easy to follow for someone who does not already know
this codebase or the details of the change.** Assume they need the concepts
explained, not the minutiae.

- **Explain at the level of main ideas and concepts**, not variable names,
  individual lines, or low-level mechanics. Say *what a change accomplishes and
  why*, not how every line works.
- **Don't assume prior knowledge.** Briefly introduce the relevant piece of the
  system before referring to it. Skip the code-level detail unless the developer
  asks for it.
- **Keep it short and scannable** — bullets and plain language over long prose or
  jargon.
- **Format for scanning with structured Markdown.** Use short headings, bold
  labels for the key parts (e.g. `**Goal:**`, `**Outcome:**`), tight bullets with
  light nesting, and whitespace between chunks, so the developer can skim the
  shape and find what they need. Apply this to everything — read-backs, step
  narration, test instructions — not just plans. The Phase 3 plan template is the
  reference for this style.

## Hard rules (do not violate)

- **Get back to the developer whenever input is needed.** This workflow requires
  the developer to explicitly review each implementation step. Whenever a decision,
  approval, or clarification is needed — a step to accept, an ambiguity to resolve,
  anything blocking — **stop and return to the developer** rather than pressing on
  or deciding alone.
- **One step at a time.** Never batch multiple implementation steps into a single
  change awaiting one approval.
- **Small chunks, not full files.** Edit in small, distinct chunks (≈one
  function/class at a time), each its own reviewable change. Don't write whole
  files except low-importance ones (a throwaway test script — see Phase 5); a
  full-file edit to real code needs explicit per-file approval and should be rare.
- **Test every phase before committing.** No phase is "done" until it has been
  verified automatically and by the developer (Phase 5).
- **Lint before you commit.** Run [[linting]] before every commit, without
  exception.

## Phase 1 — Story intake

The story is the source of truth for scope. If a formal story exists, ask for it. If not (a casual request, bug report, or feature idea), proceed to Phase 2 with what's provided.

- **If a formal story exists:** Ask the developer to paste the full story (from BitBucket) into the chat.
- **If no formal story:** Work with what's provided (the request, bug description, or idea). Do not skip Phase 2.

## Phase 2 — Clarification Q&A

**This phase always runs, regardless of whether a formal story was provided.** Requests, bug reports, and ideas are often vague and incomplete. Close every gap here, before planning.

- Ask focused clarifying questions until you have a **clear, complete picture** of
  the intended behavior, scope boundaries, edge cases, and
  acceptance criteria. Prefer several small, specific questions over one broad
  one.
- Keep going in a genuine back-and-forth — this is a full stage, not a single
  round. Surface assumptions explicitly and get them confirmed or corrected.
- End by affirming and briefly summarizing the settled understanding and asking the developer to confirm it. Only proceed once they do.

## Phase 3 — Multi-phase planning

Propose *how* the story will be built, as a plan the developer can react to. The
plan must be grounded in the existing codebase, not written in a vacuum.

- **Ground the plan in the codebase.** Build it around what you can reuse, per
  [[coding-standards]] Rule 1 (*integrate, don't bolt on*): search first, reuse or
  relocate over rewriting, match local conventions, avoid slop. In the plan, say
  plainly what's reused vs. new.
- Present a **multi-phase plan**: a sequence of named phases, each coherent and
  independently testable and commit-able. Keep bullets to main ideas — not long
  prose or line-level detail — so the developer can scan and react quickly.
- **Use this Markdown format for the plan.** One section per phase, each with a
  **Goal** line, a few bullets of main ideas (calling out what's *reused* vs.
  *new*, per the scan above), an **Outcome** line, and a **Verification** line
  (how that phase will be tested — curl, browser, etc.):

  ```markdown
  # <Story title> — Implementation Plan

  ## Phase 1 — <area>: <short title>
  **Goal:** <one line>

  - <main idea; note what's reused vs. new>
    - <optional sub-point or conditional branch>

  **Outcome:** <what exists after this phase>
  **Verification:** <how it's tested — curl / browser / mic / …>

  ---

  ## Phase 2 — <area>: <short title>
  **Goal:** <one line>

  - <main idea>

  **Outcome:** <…>
  **Verification:** <…>
  ```
- Don't enumerate the granular steps of each phase yet. Steps are worked out when
  a phase begins (Phase 4), from correspondence with the developer.
- Let the developer comment, amend, or approve. Incorporate their remarks and
  re-present if needed. **Only an explicit approval starts Phase 4.**
- **After approval, before any code, suggest a branch** (if not already on one),
  usually from `develop`. Naming: `feature/<name>` for new work, `fix/<bug>` for
  fixes (e.g. `feature/magic-link-login`, `fix/signup-password-crash`). It keeps
  the story isolated for easy review/PR/discard, with each phase's commits together. 

## Phase 4 — Stage execution (repeat per phase)

Execute one approved phase at a time. When a phase starts:

1. **Reveal its steps now.** Work out the concrete, ordered steps for *this* phase
   together with the developer, presented as a short bullet list — main ideas and
   steps, not long explanations. Don't show a phase's steps before it starts.
2. **Execute steps one by one.** For each step:
   - **Say what and why first.** One or two sentences at the concept level (see
     *How to talk to the developer*): what this change accomplishes and —
     most importantly — *why* (how it serves the story), not a line-by-line or
     variable-level account. The *why* matters more than the *what*.
   - **Make the edit directly, in small chunks.** No need to paste code into chat
     first — the editor's accept/change/edit gate on each edit *is* the per-step
     review. Apply one function/class-sized chunk (minimal, on-standard, no full
     files); narrate the what/why in chat first so they know what they're
     reviewing.
   - **Wait for the developer's decision in the editor:** accept, change, or edit.
     Apply their decision before moving on. Never advance without an explicit
     accept.
3. When every step in the phase is done and accepted, go to **Phase 5 (test)** —
   not straight to commit.

## Phase 5 — Test the phase (before every commit)

A phase is only done once it's verified. Aim for **two parts** whenever possible:

1. **Automatic test (you run it).** Exercise the code you just wrote directly and
   show the developer the result — e.g. run a command that hits the new API
   endpoint and print the response, run the new function on sample input, or run
   the relevant unit tests. Confirm the output matches the clarified acceptance
   criteria.
2. **Human test (they run it).** Tell the developer exactly how to verify it
   themselves in the real environment — e.g. which page to open in the browser,
   what to click, and what they should see. Spell out the steps; don't assume they
   know how.

**Generate a temporary test file to drive this.** Write a small script that calls
the exact code just implemented, with plenty of debug/print statements so every
meaningful value is visible. Walk the developer through running it and, at each
checkpoint, ask them to confirm the output is what they expect — and tell them how
to run it. (A throwaway test script is the allowed exception to the small-chunks
rule — it may be written in full, since it isn't important to the codebase.) Make
clear which tests are throwaway and which, if any, are meant to be kept.

**After the developer confirms everything works:**

- Remove the throwaway tests and scaffolding that aren't meant to stay.
- Clean up noisy debug statements added just for verification, **but keep
  info-level logging** that's genuinely useful to retain.
- Keep any tests you and the developer agreed are worth keeping (these follow
  [[coding-standards]] like any other code).

Only once the phase is confirmed working and cleaned up do you continue to
Phase 6.

## Phase 6 — Commit (after the phase is tested)

- **Run [[linting]] first.** Fix anything it flags (on-standard) before
  committing. Never commit on a failing lint — run it before *every* commit.
- **Keep commits small and single-purpose.** Commit in small, logical units. If a
  tested phase splits into distinct pieces, make a separate commit for each rather
  than one big commit. Each commit should be small enough that one line explains
  it.
- **Write a one-line message.** A single line stating what was just
  done/implemented/fixed, in the imperative — no body, no sections. Prefer the
  `type(scope): summary` convention. You can use commas to separate the changes if needed.
- **Never add attribution or co-author trailers.** Do not write
  "Co-authored-by: …", "Generated with …", "🤖", or any line crediting a model,
  AI, agent, or tool in the commit message. The message is only the one-line
  description of the change — nothing else.

Then start the next phase (back to Phase 4).

### Commit message examples

```text
feat(auth): added magic-link to login endpoint, email template, and token validation
fix(signup): stop crash when the password field is empty, removed dead code, fixed doc-strings
refactor(pricing): extracted discount calculation into a separate helper, refactored the main function
test(auth): added unit tests for magic-link login
```

## When to pause and ask the developer

Beyond the per-step gate, stop and ask when: the story text and the clarified
understanding conflict, a plan phase turns out to need reshaping mid-execution, a
change would touch code outside the agreed scope, a test fails or produces
unexpected output, or a step seems to require a full-file edit. Bring the finding
to the developer rather than deciding alone.

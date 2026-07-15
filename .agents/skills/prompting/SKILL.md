---
name: prompting
description: >-
  Use this skill whenever you write, improve, debug, or evaluate a prompt for any
  LLM — system prompts, agent instructions, tool descriptions, few-shot examples,
  personas, or one-off prompts. Covers the model-agnostic foundation here, then
  routes to vendor- and model-specific guidance (Claude, OpenAI/GPT, Gemini; room
  for more). Trigger it for "write me a prompt for…", "why isn't my prompt
  working", "how do I get [model] to do X", "improve this system prompt", or "make
  the model always output JSON" — even when the word "prompt" is never said.
---

# Prompting

Model-agnostic foundation for writing prompts, plus routing to vendor/model
guidance. Every frontier model is trained differently, but the core below shows up
in all their official guides. **Apply this foundation first, then layer the
matching vendor/model file** (see routing at the bottom) for model-specific
tactics — reasoning parameters, tag conventions, verbosity defaults, and quirks.

## The foundation

- **Treat the prompt as a spec, not a suggestion.** Under-specification is the
  #1 failure mode. Write for a competent contractor with zero context on your
  norms. Test: would a colleague with no background know exactly what "done" looks
  like from the prompt alone? If they'd guess, the model guesses too — and guesses
  regress to generic output.
- **Structure it.** Most working prompts decompose into: **role** (one sentence
  steers tone and relevance for almost no cost) · **context** (facts/data the
  model can't know) · **task** · **constraints** · **output format** ·
  **examples**. Not every prompt needs all six; when one underperforms, check
  which are missing.
- **Put long context first.** For any non-trivial document or codebase dump
  (~20k+ tokens), place the material *before* the instructions. Instructions read
  with the material fresh outperform instructions the model must hold in mind
  while skimming.
- **State the task as an instruction, not a question.** "Summarize the risks in
  this contract" beats "Can you tell me about the risks?" — hedged phrasing gets
  hedged, suggestion-only answers.
- **Phrase constraints positively.** "Respond in plain prose, no headers or
  bullets" beats "don't use markdown" — a concrete target beats an infinite space
  of "not that."
- **Show, don't just tell.** 2–5 diverse, edge-case-covering examples are one of
  the highest-leverage levers for controlling format, tone, and edge handling —
  often ranked above extra instruction text. Keep formatting *identical* across
  examples, wrap each clearly (`<example>…</example>` or Input:/Output:), and cut
  prose that the examples already make obvious.
- **Explain the why, not just the what.** "Always cite sources, since a human
  editor fact-checks this before publishing" generalizes to novel cases and stays
  maintainable in a way that a bare "always cite sources" does not.
- **Use consistent delimiters.** Separate distinct chunks with XML-style tags
  (`<context>`, `<instructions>`) or Markdown headers. Pick one style and stay
  consistent; mixing styles or reusing tag names inconsistently degrades
  section-following.
- **Set reasoning depth and verbosity explicitly.** Don't rely on defaults — a
  quick classification and a multi-step debug want very different settings.
  Request it in the prompt ("think carefully before answering" vs. "answer
  directly") or via the model's parameter (see the vendor file for exact names).
- **Avoid contradictions more than length.** A short prompt with no internal
  conflicts beats a long one with even one. Conflicting rules don't average out —
  the model burns effort reconciling them, producing degraded output. Check each
  new rule against what's already there.

## Iterate empirically

- Define what "good" looks like, draft, run on realistic inputs, **read** the
  output (don't skim), and change **one thing at a time** based on what you see.
- **Read the failure, not the score.** Fix the specific cause (missing context,
  ambiguous instruction, conflicting constraint, wrong format spec) rather than
  adding emphasis ("PLEASE make sure to…").
- **Meta-prompt.** Give the model the current prompt plus a desired and an
  undesired example, and ask what phrases to add or remove. The executing model is
  often the best critic of its own prompt.
- **Clarify first.** For ambiguous templates, have the model ask 1–3 clarifying
  questions before generating, rather than confidently guessing wrong.
- **Red-team pass.** For planning or argument prompts, add a second pass where the
  model argues against its own first answer before finalizing.

## Diagnostic checklist

When a prompt misbehaves, walk this in order:

1. Is the task a clear instruction, placed *after* any long context?
2. Would a no-context colleague know what "done" looks like?
3. Are there 2+ examples, formatted identically?
4. Any negative constraint that could be a positive instruction?
5. Any two instructions that could conflict in an edge case?
6. Is reasoning depth and verbosity set for this task's difficulty?
7. Do you know the target model? If so, read its file below — several
   highest-leverage fixes are model-specific.

## Routing — vendor and model files

Read the vendor's `general.md` first, then the model-specific file:

- **Claude, all models** → `Claude/general.md`
  - Fable 5 / Mythos 5 → `Claude/models/fable-5.md`
  - Sonnet 5 → `Claude/models/sonnet-5.md`
  - Opus 4.8 → `Claude/models/opus-4.8.md`
- **OpenAI, GPT-5 family** → `OpenAI/general.md`
  - GPT-5.5 → `OpenAI/models/gpt-5.5.md`
  - GPT-5.4 / mini / nano → `OpenAI/models/gpt-5.4.md`
  - GPT-4.1 (non-reasoning) → `OpenAI/models/gpt-4.1.md`
  - gpt-realtime (speech-to-speech / Realtime API) → `OpenAI/models/gpt-realtime.md`
- **Gemini, all models** → `Gemini/general.md`
  - Gemini 3 → `Gemini/models/gemini-3.md`
  - Gemini Live API (real-time voice/video, e.g. gemini-live-2.5-flash) → `Gemini/models/gemini-live.md`

If no file exists for the target model, fall back to the vendor's `general.md` (or
the closest family file) and note the gap so it can be added.

```
prompting/
  SKILL.md            ← you are here (foundation + router)
  Claude/  general.md + models/{fable-5, sonnet-5, opus-4.8}.md
  OpenAI/  general.md + models/{gpt-5.5, gpt-5.4, gpt-4.1, gpt-realtime}.md
  Gemini/  general.md + models/{gemini-3, gemini-live}.md
```

## Adding a model or vendor

Add a model file under `<Vendor>/models/<model-slug>.md` and a bullet to the
routing list above; add a new vendor as a sibling folder of `Claude/` with its own
`general.md` and `models/`. Do **not** create a nested `SKILL.md` — skill
discovery only reads the single `SKILL.md` at this folder's root, so everything
below it must be plain markdown files this router points to.

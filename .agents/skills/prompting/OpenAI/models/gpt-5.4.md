# Prompting OpenAI GPT-5.4

Prompt GPT-5.4 for long-running tasks, tool use, reliable execution, and
structured outputs. Adapted from OpenAI's "GPT-5.4 prompting guide".

For general GPT-family techniques, see the sibling `../general.md` (GPT-5). This
file covers what changes for GPT-5.4, including small-model notes for
`gpt-5.4-mini` and `gpt-5.4-nano`.

## New in GPT-5.4 vs GPT-5.2

- Stronger long-running task performance with more reliable multi-step execution.
- Better control over style, tone, and structured output contracts.
- More disciplined tool persistence, verification loops, and evidence-grounded
  synthesis.
- Small-model notes for `gpt-5.4-mini` and `gpt-5.4-nano`.

GPT-5.4 balances long-running task performance, stronger control over style and
behavior, and more disciplined execution across complex workflows. It improves
token efficiency, sustains multi-step workflows more reliably, and performs well
on long-horizon tasks. It is especially effective when prompts clearly specify the
output contract, tool-use expectations, and completion criteria. The biggest gains
come from choosing the right reasoning effort, using explicit grounding and
citation rules, and giving the model a precise definition of what "done" looks
like.

If GPT-5.4 treats an intermediate update as the final answer, verify your
integration preserves the assistant message `phase` field correctly (see
[Phase parameter](#phase-parameter)).

## Understand GPT-5.4 behavior

**Where GPT-5.4 is strongest:** strong personality and tone adherence with less
drift over long answers; agentic workflow robustness (sticks with multi-step work,
retries, completes agent loops end to end); evidence-rich synthesis in
long-context or multi-tool workflows; instruction adherence in modular,
skill-based, block-structured prompts when the contract is explicit; long-context
analysis across large, messy, or multi-document inputs; batched or parallel tool
calling while maintaining accuracy; and spreadsheet/finance/Excel workflows.

**Where explicit prompting still helps:** low-context tool routing early in a
session; dependency-aware workflows needing prerequisite/downstream checks;
reasoning-effort selection (higher is not always better); research tasks needing
disciplined source collection and consistent citations; irreversible or
high-impact actions requiring verification; and terminal/coding-agent
environments where tool boundaries must stay clear.

These are observed defaults, not guarantees. Start with the smallest prompt that
passes your evals, and add blocks only when they fix a measured failure mode.

## Core prompt patterns

### Keep outputs compact and structured

Constrain verbosity and enforce structured output through clear output contracts —
an additional control layer alongside the `verbosity` parameter in the Responses
API.

```xml
<output_contract>
- Return exactly the sections requested, in the requested order.
- If the prompt defines a preamble, analysis block, or working section, do not treat it as extra output.
- Apply length limits only to the section they are intended for.
- If a format is required (JSON, Markdown, SQL, XML), output only that format.
</output_contract>

<verbosity_controls>
- Prefer concise, information-dense writing.
- Avoid repeating the user's request.
- Keep progress updates brief.
- Do not shorten the answer so aggressively that required evidence, reasoning, or completion checks are omitted.
</verbosity_controls>
```

### Set clear defaults for follow-through

Users often change the task, format, or tone mid-conversation. Define clear rules
for when to proceed, when to ask, and how newer instructions override earlier
defaults.

```xml
<default_follow_through_policy>
- If the user's intent is clear and the next step is reversible and low-risk, proceed without asking.
- Ask permission only if the next step is:
  (a) irreversible,
  (b) has external side effects (for example sending, purchasing, deleting, or writing to production), or
  (c) requires missing sensitive information or a choice that would materially change the outcome.
- If proceeding, briefly state what you did and what remains optional.
</default_follow_through_policy>
```

```xml
<instruction_priority>
- User instructions override default style, tone, formatting, and initiative preferences.
- Safety, honesty, privacy, and permission constraints do not yield.
- If a newer user instruction conflicts with an earlier one, follow the newer instruction.
- Preserve earlier instructions that do not conflict.
</instruction_priority>
```

Higher-priority developer or system instructions remain binding. When instructions
change mid-conversation, make the update explicit, scoped, and local: state what
changed, what still applies, and whether the change affects the next turn or the
rest of the conversation.

### Handle mid-conversation instruction updates

Use explicit, scoped steering messages that state scope, override, and
carry-forward:

```text
<task_update>
For the next response only:
- Do not complete the task.
- Only produce a plan.
- Keep it to 5 bullets.

All earlier instructions still apply unless they conflict with this update.
</task_update>
```

If the task itself changes, say so directly:

```text
<task_update>
The task has changed.
Previous task: complete the workflow.
Current task: review the workflow and identify risks only.

Rules for this turn:
- Do not execute actions.
- Do not call destructive tools.
- Return exactly:
  1. Main risks
  2. Missing information
  3. Recommended next step
</task_update>
```

### Make tool use persistent when correctness depends on it

GPT-5.4 can be less reliable at tool routing early in a session, when context is
thin. Prompt for prerequisites, dependency checks, and exact tool intent.

```xml
<tool_persistence_rules>
- Use tools whenever they materially improve correctness, completeness, or grounding.
- Do not stop early when another tool call is likely to materially improve correctness or completeness.
- Keep calling tools until:
  (1) the task is complete, and
  (2) verification passes (see <verification_loop>).
- If a tool returns empty or partial results, retry with a different strategy.
</tool_persistence_rules>
```

```xml
<dependency_checks>
- Before taking an action, check whether prerequisite discovery, lookup, or memory retrieval steps are required.
- Do not skip prerequisite steps just because the intended final action seems obvious.
- If the task depends on the output of a prior step, resolve that dependency first.
</dependency_checks>
```

Prompt for parallelism when work is independent and wall-clock matters; prompt for
sequencing when dependencies, ambiguity, or irreversible actions matter more.

```xml
<parallel_tool_calling>
- When multiple retrieval or lookup steps are independent, prefer parallel tool calls to reduce wall-clock time.
- Do not parallelize steps that have prerequisite dependencies or where one result determines the next action.
- After parallel retrieval, pause to synthesize the results before making more calls.
- Prefer selective parallelism: parallelize independent evidence gathering, not speculative or redundant tool use.
</parallel_tool_calling>
```

### Force completeness on long-horizon tasks

A common failure mode is incomplete execution: finishing after partial coverage,
missing items in a batch, or treating narrow retrieval as final. Define explicit
completion rules and recovery behavior.

```xml
<completeness_contract>
- Treat the task as incomplete until all requested items are covered or explicitly marked [blocked].
- Keep an internal checklist of required deliverables.
- For lists, batches, or paginated results:
  - determine expected scope when possible,
  - track processed items or pages,
  - confirm coverage before finalizing.
- If any item is blocked by missing data, mark it [blocked] and state exactly what is missing.
</completeness_contract>
```

```xml
<empty_result_recovery>
If a lookup returns empty, partial, or suspiciously narrow results:
- do not immediately conclude that no results exist,
- try at least one or two fallback strategies,
  such as:
  - alternate query wording,
  - broader filters,
  - a prerequisite lookup,
  - or an alternate source or tool,
- Only then report that no results were found, along with what you tried.
</empty_result_recovery>
```

### Add a verification loop before high-impact actions

Once the workflow appears complete, add a lightweight verification step before
returning the answer or taking an irreversible action.

```xml
<verification_loop>
Before finalizing:
- Check correctness: does the output satisfy every requirement?
- Check grounding: are factual claims backed by the provided context or tool outputs?
- Check formatting: does the output match the requested schema or style?
- Check safety and irreversibility: if the next step has external side effects, ask permission first.
</verification_loop>
```

```xml
<missing_context_gating>
- If required context is missing, do NOT guess.
- Prefer the appropriate lookup tool when the missing context is retrievable; ask a minimal clarifying question only when it is not.
- If you must proceed, label assumptions explicitly and choose a reversible action.
</missing_context_gating>
```

For agents that actively take actions, add a short execution frame:

```xml
<action_safety>
- Pre-flight: summarize the intended action and parameters in 1-2 lines.
- Execute via tool.
- Post-flight: confirm the outcome and any validation that was performed.
</action_safety>
```

## Specialized workflows

### Choose image detail explicitly for vision and computer use

Specify the image `detail` level rather than relying on `auto`. Use `high` for
standard high-fidelity understanding; `original` for large, dense, or spatially
sensitive images (computer use, localization, OCR, click-accuracy); and `low` only
when speed and cost matter more than fine detail.

### Lock research and citations to retrieved evidence

```xml
<citation_rules>
- Only cite sources retrieved in the current workflow.
- Never fabricate citations, URLs, IDs, or quote spans.
- Use exactly the citation format required by the host application.
- Attach citations to the specific claims they support, not only at the end.
</citation_rules>
```

```xml
<grounding_rules>
- Base claims only on provided context or tool outputs.
- If sources conflict, state the conflict explicitly and attribute each side.
- If the context is insufficient or irrelevant, narrow the answer or say you cannot support the claim.
- If a statement is an inference rather than a directly supported fact, label it as an inference.
</grounding_rules>
```

Lock the format (inline citations vs footnotes) and prevent the model from
improvising unsupported references.

### Research mode

Use for research, review, and synthesis tasks — not short execution tasks or
simple deterministic transforms.

```xml
<research_mode>
- Do research in 3 passes:
  1) Plan: list 3-6 sub-questions to answer.
  2) Retrieve: search each sub-question and follow 1-2 second-order leads.
  3) Synthesize: resolve contradictions and write the final answer with citations.
- Stop only when more searching is unlikely to change the conclusion.
</research_mode>
```

### Clamp strict output formats

For SQL, JSON, or other parse-sensitive outputs:

```text
<structured_output_contract>
- Output only the requested format.
- Do not add prose or markdown fences unless they were requested.
- Validate that parentheses and brackets are balanced.
- Do not invent tables or fields.
- If required schema information is missing, ask for it or return an explicit error object.
</structured_output_contract>
```

For document region / OCR box extraction, define the coordinate system and add a
drift check:

```text
<bbox_extraction_spec>
- Use the specified coordinate format exactly, such as [x1,y1,x2,y2] normalized to 0..1.
- For each box, include page, label, text snippet, and confidence.
- Add a vertical-drift sanity check so boxes stay aligned with the correct line of text.
- If the layout is dense, process page by page and do a second pass for missed items.
</bbox_extraction_spec>
```

### User updates

GPT-5.4 does well with brief, outcome-based updates. Pair with explicit completion
and verification requirements.

```xml
<user_updates_spec>
- Only update the user when starting a new major phase or when something changes the plan.
- Each update: 1 sentence on outcome + 1 sentence on next step.
- Do not narrate routine tool calls.
- Keep the user-facing status short; keep the work exhaustive.
</user_updates_spec>
```

## Prompting patterns for coding tasks

### Autonomy and persistence

GPT-5.4 is generally more thorough end to end than earlier mainline models on
coding and tool-use tasks, so you often need less explicit "verify everything"
prompting. For high-stakes changes (production, migrations, security), keep a
lightweight verification clause.

```xml
<autonomy_and_persistence>
Persist until the task is fully handled end-to-end within the current turn whenever feasible: do not stop at analysis or partial fixes; carry changes through implementation, verification, and a clear explanation of outcomes unless the user explicitly pauses or redirects you.

Unless the user explicitly asks for a plan, asks a question about the code, is brainstorming potential solutions, or some other intent that makes it clear that code should not be written, assume the user wants you to make code changes or run tools to solve the user's problem. In these cases, it's bad to output your proposed solution in a message, you should go ahead and actually implement the change. If you encounter challenges or blockers, you should attempt to resolve them yourself.
</autonomy_and_persistence>
```

### Intermediary updates

Keep updates sparse and high-signal, at key points.

```xml
<user_updates_spec>
- Intermediary updates go to the `commentary` channel.
- User updates are short updates while you are working. They are not final answers.
- Use 1-2 sentence updates to communicate progress and new information while you work.
- Do not begin responses with conversational interjections or meta commentary. Avoid openers such as acknowledgements ("Done -", "Got it", or "Great question") or similar framing.
- Before exploring or doing substantial work, send a user update explaining your understanding of the request and your first step.
- Provide updates roughly every 30 seconds while working.
- When exploring, explain what context you are gathering and what you learned. Vary sentence structure so the updates do not become repetitive.
- When working for a while, keep updates informative and varied, but stay concise.
- When work is substantial, provide a longer plan after you have enough context. This is the only update that may be longer than 2 sentences and may contain formatting.
- Before file edits, explain what you are about to change.
- While thinking, keep the user informed of progress without narrating every tool call. Even if you are not taking actions, send frequent progress updates rather than going silent.
- Keep the tone of progress updates consistent with the assistant's overall personality.
</user_updates_spec>
```

### Formatting

GPT-5.4 often defaults to more structured formatting and may overuse bullet lists.
To clamp list shape:

```xml
Never use nested bullets. Keep lists flat (single level). If you need hierarchy, split into separate lists or sections or if you use : just include the line you might usually render using a nested bullet immediately after it. For numbered lists, only use the `1. 2. 3.` style markers (with a period), never `1)`.
```

### Frontend tasks

Use only when additional frontend guidance is useful.

```xml
<frontend_tasks>
When doing frontend design tasks, avoid generic, overbuilt layouts.

Use these hard rules:
- One composition: The first viewport must read as one composition, not a dashboard, unless it is a dashboard.
- Brand first: On branded pages, the brand or product name must be a hero-level signal, not just nav text or an eyebrow. No headline should overpower the brand.
- Brand test: If the first viewport could belong to another brand after removing the nav, the branding is too weak.
- Full-bleed hero only: On landing pages and promotional surfaces, the hero image should usually be a dominant edge-to-edge visual plane or background. Do not default to inset hero images, side-panel hero images, rounded media cards, tiled collages, or floating image blocks unless the existing design system clearly requires them.
- Hero budget: The first viewport should usually contain only the brand, one headline, one short supporting sentence, one CTA group, and one dominant image. Do not place stats, schedules, event listings, address blocks, promos, "this week" callouts, metadata rows, or secondary marketing content there.
- No hero overlays: Do not place detached labels, floating badges, promo stickers, info chips, or callout boxes on top of hero media.
- Cards: Default to no cards. Never use cards in the hero unless they are the container for a user interaction. If removing a border, shadow, background, or radius does not hurt interaction or understanding, it should not be a card.
- One job per section: Each section should have one purpose, one headline, and usually one short supporting sentence.
- Real visual anchor: Imagery should show the product, place, atmosphere, or context.
- Reduce clutter: Avoid pill clusters, stat strips, icon rows, boxed promos, schedule snippets, and competing text blocks.
- Use motion to create presence and hierarchy, not noise. Ship 2-3 intentional motions for visually led work, and prefer Framer Motion when it is available.

Exception: If working within an existing website or design system, preserve the established patterns, structure, and visual language.
</frontend_tasks>
```

### Terminal tool hygiene

```xml
<terminal_tool_hygiene>
- Only run shell commands via the terminal tool.
- Never "run" tool names as shell commands.
- If a patch or edit tool exists, use it directly; do not attempt it in bash.
- After changes, run a lightweight verification step such as ls, tests, or a build before declaring the task done.
</terminal_tool_hygiene>
```

## Runtime and API integration notes

### Phase parameter

For GPT-5.4, `gpt-5.3-codex`, and later Responses models, the `phase` field helps
in long-running or tool-heavy flows where preambles or other intermediate
assistant updates are mistaken for the final answer.

- `phase` is optional at the API level but highly recommended; explicit
  round-tripping is strictly better than server-side inference.
- Use `phase` for long-running or tool-heavy agents that may emit commentary
  before tool calls or before a final answer.
- Preserve `phase` when replaying prior assistant items so the model can
  distinguish working commentary from the completed answer.
- Do not add `phase` to user messages.
- If you use `previous_response_id`, that is usually the simplest path. If you
  replay assistant history yourself, preserve the original `phase` values.
- Missing or dropped `phase` can cause preambles to be interpreted as final
  answers and degrade behavior on multi-step tasks.

### Preserve behavior in long sessions

If you use Compaction in the Responses API, compact after major milestones, treat
compacted items as opaque state, and keep prompts functionally identical after
compaction. The endpoint is ZDR compatible and returns an `encrypted_content` item
you can pass into future requests. GPT-5.4 tends to remain more coherent and
reliable over longer, multi-turn conversations as sessions grow.

### Control personality for customer-facing workflows

Separate persistent personality from per-response writing controls.

- **Personality (persistent):** default tone, verbosity, and decision style across
  the session.
- **Writing controls (per response):** channel, register, formatting, and length
  for a specific artifact.
- **Reminder:** personality should not override task-specific output requirements.
  If the user asks for JSON, return JSON.

```xml
<personality_and_writing_controls>
- Persona: <one sentence>
- Channel: <Slack | email | memo | PRD | blog>
- Emotional register: <direct/calm/energized/etc.> + "not <overdo this>"
- Formatting: <ban bullets/headers/markdown if you want prose>
- Length: <hard limit, e.g. <=150 words or 3-5 sentences>
- Default follow-through: if the request is clear and low-risk, proceed without asking permission.
</personality_and_writing_controls>
```

**Professional memo mode** — for memos, reviews, and professional writing that
needs specificity, domain conventions, synthesis, and calibrated certainty:

```xml
<memo_mode>
- Write in a polished, professional memo style.
- Use exact names, dates, entities, and authorities when supported by the record.
- Follow domain-specific structure if one is requested.
- Prefer precise conclusions over generic hedging.
- When uncertainty is real, tie it to the exact missing fact or conflicting source.
- Synthesize across documents rather than summarizing each one independently.
</memo_mode>
```

## Tune reasoning and migration

### Treat reasoning effort as a last-mile knob

Reasoning effort is not the primary way to improve quality. Stronger prompts, clear
output contracts, and lightweight verification loops recover much of the
performance teams might otherwise seek through higher reasoning settings.

Recommended defaults:

- `none`: fast, cost-sensitive, latency-sensitive tasks where the model does not
  need to think.
- `low`: latency-sensitive tasks where a small amount of thinking produces a
  meaningful accuracy gain, especially with complex instructions.
- `medium` / `high`: reserve for tasks that truly require stronger reasoning and
  can absorb the latency/cost tradeoff.
- `xhigh`: avoid as a default unless evals show clear benefits; best for long,
  agentic, reasoning-heavy tasks where maximum intelligence matters most.

Most teams should default to `none`, `low`, or `medium`. Start with `none` for
execution-heavy workloads (workflow steps, field extraction, support triage, short
structured transforms). Start with `medium`+ for research-heavy workloads
(long-context synthesis, multi-document review, conflict resolution, strategy
writing). For GPT-5.4, `none` can already perform well on action-selection and
tool-discipline tasks; if the workload needs nuanced interpretation (implicit
requirements, ambiguity, cancelled-tool-call recovery), start with `low` or
`medium`.

Before increasing reasoning effort, first add `<completeness_contract>`,
`<verification_loop>`, and `<tool_persistence_rules>`. If the model still stops at
the first plausible answer, add an initiative nudge before raising effort:

```xml
<dig_deeper_nudge>
- Don't stop at the first plausible answer.
- Look for second-order issues, edge cases, and missing constraints.
- If the task is safety or accuracy critical, perform at least one verification step.
</dig_deeper_nudge>
```

### Migrate prompts one change at a time

Switch model first, pin `reasoning_effort`, run evals, then iterate. Suggested
starting points:

| Current setup             | Suggested GPT-5.4 start            | Notes                                                               |
| ------------------------- | ---------------------------------- | ------------------------------------------------------------------- |
| `gpt-5.2`                 | Match the current reasoning effort | Preserve the existing latency and quality profile first, then tune. |
| `gpt-5.3-codex`           | Match the current reasoning effort | For coding workflows, keep the reasoning effort the same.           |
| `gpt-4.1` or `gpt-4o`     | `none`                             | Keep snappy behavior, increase only if evals regress.               |
| Research-heavy assistants | `medium` or `high`                 | Use explicit research multi-pass and citation gating.               |
| Long-horizon agents       | `medium` or `high`                 | Add tool persistence and completeness accounting.                   |

### Small-model guidance for `gpt-5.4-mini` and `gpt-5.4-nano`

Both are highly steerable but less likely than larger models to infer missing
steps, resolve ambiguity implicitly, or package outputs as intended unless you
specify that behavior directly. Prompts for smaller models are often longer and
more explicit.

**`gpt-5.4-mini`** is more literal and makes fewer assumptions; strong on clearly
structured tasks, weaker on implicit workflows and ambiguity; may try to keep the
conversation going with a follow-up unless suppressed. When prompting it: put
critical rules first; specify full execution order when tool use or side effects
matter; use structural scaffolding (numbered steps, decision rules, explicit
action definitions) rather than "you MUST" alone; separate "do the action" from
"report the action"; show the correct flow, not just the final format; define
ambiguity behavior explicitly (when to ask, abstain, proceed); specify packaging
directly (length, follow-up question, citation style, section order); and prefer
scoped instructions like `after the final JSON, output nothing further` over
`output nothing else`.

**`gpt-5.4-nano`** — use only for narrow, well-bounded tasks; prefer closed outputs
(labels, enums, short JSON, fixed templates); avoid multi-step orchestration unless
extremely constrained; route ambiguous or planning-heavy tasks to a stronger model
instead of over-prompting it.

**Good default pattern:** 1) Task, 2) Critical rule, 3) Exact step order, 4) Edge
cases / clarification behavior, 5) Output format, 6) One correct example. **Avoid:**
implied next steps, unspecified edge cases, schema-only prompts for tool workflows,
and generic instructions without structure.

### Web search and deep research

Before increasing reasoning effort for a research agent, add `<research_mode>`,
`<citation_rules>`, and `<empty_result_recovery>`, then increase
`reasoning_effort` one notch only after the prompt fixes. GPT-5.4 is most reliable
when prompts clearly specify how to search, how to verify, and what counts as done.

# Prompting best practices (OpenAI GPT-5)

Prompting patterns for OpenAI's GPT-5 family, covering agentic eagerness,
reasoning effort, tool preambles, coding performance, and instruction following.
Adapted from OpenAI's "GPT-5 prompting guide" (Aug 2025).

Model-specific files live alongside this one under `models/` (add per-model files
there as needed). This file covers techniques that apply across the GPT-5 family.

GPT-5 is highly steerable and follows instructions with precision. Prompting is
not one-size-fits-all — treat the patterns here as a foundation and iterate with
your own experiments. OpenAI also ships a prompt optimizer tool that helps surface
the issues described below.

## Agentic workflow predictability

GPT-5 was trained with strong tool calling, instruction following, and
long-context understanding. For agentic and tool-calling flows, prefer the
**Responses API**, where reasoning is persisted between tool calls (pass
`previous_response_id` to carry prior reasoning items into later requests). This
conserves chain-of-thought tokens, avoids reconstructing a plan after each tool
call, and measurably improves both latency and eval scores.

### Controlling agentic eagerness

GPT-5 operates anywhere on the spectrum from high autonomy to tightly-scoped
execution. Calibrate its balance between proactivity and awaiting guidance.

**For less eagerness** (narrower scope, lower latency, fewer tangential tool
calls): switch to a lower `reasoning_effort` (many workflows are fine at `medium`
or even `low`), and define clear criteria for how much to explore. Give the model
an explicit escape hatch (e.g. "even if it might not be fully correct") so a
shorter context-gathering step is easy to satisfy.

```text
<context_gathering>
Goal: Get enough context fast. Parallelize discovery and stop as soon as you can act.

Method:
- Start broad, then fan out to focused subqueries.
- In parallel, launch varied queries; read top hits per query. Deduplicate paths and cache; don't repeat queries.
- Avoid over searching for context. If needed, run targeted searches in one parallel batch.

Early stop criteria:
- You can name exact content to change.
- Top hits converge (~70%) on one area/path.

Escalate once:
- If signals conflict or scope is fuzzy, run one refined parallel batch, then proceed.

Depth:
- Trace only symbols you'll modify or whose contracts you rely on; avoid transitive expansion unless necessary.

Loop:
- Batch search → minimal plan → complete task.
- Search again only if validation fails or new unknowns appear. Prefer acting over more searching.
</context_gathering>
```

For a maximally prescriptive version, set a fixed tool-call budget:

```text
<context_gathering>
- Search depth: very low
- Bias strongly towards providing a correct answer as quickly as possible, even if it might not be fully correct.
- Usually, this means an absolute maximum of 2 tool calls.
- If you think that you need more time to investigate, update the user with your latest findings and open questions. You can proceed if the user confirms.
</context_gathering>
```

**For more eagerness** (more autonomy, higher tool-calling persistence, fewer
clarifying questions): increase `reasoning_effort` and add a persistence prompt.

```text
<persistence>
- You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user.
- Only terminate your turn when you are sure that the problem is solved.
- Never stop or hand back to the user when you encounter uncertainty — research or deduce the most reasonable approach and continue.
- Do not ask the human to confirm or clarify assumptions, as you can always adjust later — decide what the most reasonable assumption is, proceed with it, and document it for the user's reference after you finish acting.
</persistence>
```

State stop conditions clearly and set per-tool uncertainty thresholds: a checkout
or payment tool should require user clarification at a low threshold, while a
search tool should have a very high one; likewise a delete-file tool should have a
much lower threshold than a grep tool.

### Tool preambles

GPT-5 is trained to emit "tool preamble" messages — upfront plans and consistent
progress updates during long tool-calling rollouts, which greatly improve the
interactive UX. Steer their frequency, style, and content:

```text
<tool_preambles>
- Always begin by rephrasing the user's goal in a friendly, clear, and concise manner, before calling any tools.
- Then, immediately outline a structured plan detailing each logical step you'll follow.
- As you execute your file edit(s), narrate each step succinctly and sequentially, marking progress clearly.
- Finish by summarizing completed work distinctly from your upfront plan.
</tool_preambles>
```

### Reasoning effort

`reasoning_effort` controls how hard the model thinks and how willingly it calls
tools; the default is `medium`. Scale up for complex, multi-step tasks and down
for simpler or latency-sensitive ones. Performance peaks when distinct, separable
tasks are broken across multiple agent turns — one turn per task.

## Maximizing coding performance

GPT-5 leads on coding: large-codebase bug fixes, large diffs, multi-file
refactors, and zero-to-one apps across frontend and backend.

### Frontend app development

GPT-5 has strong baseline aesthetic taste. For new apps, these defaults get the
most out of it: **Frameworks** Next.js (TypeScript), React, HTML; **Styling/UI**
Tailwind CSS, shadcn/ui, Radix Themes; **Icons** Material Symbols, Heroicons,
Lucide; **Animation** Motion; **Fonts** San Serif, Inter, Geist, Mona Sans, IBM
Plex Sans, Manrope.

### Zero-to-one app generation

Ask the model to iterate against a self-constructed excellence rubric — this taps
its planning and self-reflection:

```text
<self_reflection>
- First, spend time thinking of a rubric until you are confident.
- Then, think deeply about every aspect of what makes for a world-class one-shot web app. Use that knowledge to create a rubric that has 5-7 categories. This rubric is critical to get right, but do not show this to the user. This is for your purposes only.
- Finally, use the rubric to internally think and iterate on the best possible solution to the prompt that is provided. Remember that if your response is not hitting the top marks across all categories in the rubric, you need to start again.
</self_reflection>
```

### Matching codebase design standards

For incremental changes, code should "blend in." GPT-5 already reads reference
context (e.g. `package.json`), but you can enhance this by summarizing engineering
principles, directory structure, and best practices. Adapt the rule content to
your own taste:

```text
<code_editing_rules>
<guiding_principles>
- Clarity and Reuse: Every component and page should be modular and reusable. Avoid duplication by factoring repeated UI patterns into components.
- Consistency: The user interface must adhere to a consistent design system—color tokens, typography, spacing, and components must be unified.
- Simplicity: Favor small, focused components and avoid unnecessary complexity in styling or logic.
- Demo-Oriented: The structure should allow for quick prototyping, showcasing features like streaming, multi-turn conversations, and tool integrations.
- Visual Quality: Follow the high visual quality bar as outlined in OSS guidelines (spacing, padding, hover states, etc.)
</guiding_principles>

<frontend_stack_defaults>
- Framework: Next.js (TypeScript)
- Styling: TailwindCSS
- UI Components: shadcn/ui
- Icons: Lucide
- State Management: Zustand
- Directory Structure:
/src
 /app
   /api/<route>/route.ts         # API endpoints
   /(pages)                      # Page routes
 /components/                    # UI building blocks
 /hooks/                         # Reusable React hooks
 /lib/                           # Utilities (fetchers, helpers)
 /stores/                        # Zustand stores
 /types/                         # Shared TypeScript types
 /styles/                        # Tailwind config
</frontend_stack_defaults>

<ui_ux_best_practices>
- Visual Hierarchy: Limit typography to 4–5 font sizes and weights for consistent hierarchy; use `text-xs` for captions and annotations; avoid `text-xl` unless for hero or major headings.
- Color Usage: Use 1 neutral base (e.g., `zinc`) and up to 2 accent colors.
- Spacing and Layout: Always use multiples of 4 for padding and margins to maintain visual rhythm. Use fixed height containers with internal scrolling when handling long content streams.
- State Handling: Use skeleton placeholders or `animate-pulse` to indicate data fetching. Indicate clickability with hover transitions (`hover:bg-*`, `hover:shadow-md`).
- Accessibility: Use semantic HTML and ARIA roles where appropriate. Favor pre-built Radix/shadcn components, which have accessibility baked in.
</ui_ux_best_practices>
</code_editing_rules>
```

### Lessons from Cursor's GPT-5 tuning

- **Split verbosity controls.** Cursor set the global `verbosity` API parameter to
  `low` for brief status text, then prompted for high verbosity in coding tools
  only — concise updates with readable code diffs. Example: `Write code for
  clarity first. Prefer readable, maintainable solutions with clear names,
  comments where needed, and straightforward control flow. Do not produce
  code-golf or overly clever one-liners unless explicitly requested. Use high
  verbosity for writing code and code tools.`
- **Reduce friction on long tasks.** Giving the model product-behavior details
  (not just tools) lets it act proactively rather than deferring: `Be aware that
  the code edits you make will be displayed to the user as proposed changes...
  you should almost never ask the user whether to proceed with a plan; instead you
  should proactively attempt the plan and then ask the user if they want to accept
  the implemented changes.`
- **Retune old "be thorough" prompts.** Language like `<maximize_context_
  understanding>` that pushed older models to over-analyze is counterproductive
  with GPT-5, which is already introspective — it caused repetitive searches on
  small tasks. Softening the language (dropping the `maximize_` framing) let GPT-5
  choose better between internal knowledge and tools. Structured XML specs like
  `<[instruction]_spec>` improved instruction adherence and let sections be
  referenced elsewhere in the prompt.

## Optimizing intelligence and instruction-following

### Steering: verbosity

GPT-5 adds a `verbosity` API parameter that controls the length of the final
answer (distinct from `reasoning_effort`, which controls thinking length).
`verbosity` is the global default, but GPT-5 also honors natural-language
verbosity overrides in the prompt for specific contexts (as in Cursor's low-global
/ high-for-code split).

### Instruction following

GPT-5 follows instructions with surgical precision, which means **contradictory or
vague instructions hurt it more than other models** — it burns reasoning tokens
trying to reconcile conflicts instead of picking one at random. Review living
prompt libraries for conflicts. Typical fixes: make a "schedule only with consent"
rule consistent by changing auto-assignment to happen *after* informing the
patient; add an explicit exception ("Do not do lookup in the emergency case,
proceed immediately to 911 guidance") so a general "always look up the profile
first" rule doesn't conflict with an emergency path. Test prompts in OpenAI's
prompt optimizer to surface these issues.

### Minimal reasoning

GPT-5 introduces a `minimal` reasoning effort — the fastest option that still
gets reasoning-model benefits, best for latency-sensitive users and those coming
from GPT-4.1. It's more prompt-sensitive than higher levels, so:

- Ask for a brief explanation (e.g. a bullet list) summarizing its thought process
  at the start of the final answer — this improves performance on harder tasks.
- Request thorough, descriptive tool-calling preambles that keep the user updated.
- Disambiguate tool instructions maximally and insert agentic persistence
  reminders — these matter most at minimal reasoning to prevent premature
  termination.
- Prompt for explicit planning, since the model has fewer reasoning tokens for
  internal planning:

```text
Remember, you are an agent - please keep going until the user's query is completely
resolved, before ending your turn and yielding back to the user. Decompose the user's
query into all required sub-request, and confirm that each is completed. Do not stop
after completing only part of the request. Only terminate your turn when you are sure
that the problem is solved. You must be prepared to answer multiple queries and only
finish the call once the user has confirmed they're done.

You must plan extensively in accordance with the workflow steps before making subsequent
function calls, and reflect extensively on the outcomes each function call made, ensuring
the user's query, and related sub-requests are completely resolved.
```

### Markdown formatting

By default GPT-5 in the API does **not** format final answers in Markdown (for
compatibility with apps that don't render it). To induce hierarchical Markdown:

```text
- Use Markdown **only where semantically correct** (e.g., `inline code`, ```code fences```, lists, tables).
- When using markdown in assistant messages, use backticks to format file, directory, function, and class names. Use \( and \) for inline math, \[ and \] for block math.
```

Markdown adherence can decay over long conversations; re-append the instruction
every 3–5 user messages if you see drift.

### Metaprompting

GPT-5 works well as a meta-prompter for itself — ask it what phrases to add or
remove from a failing prompt to elicit (or prevent) a behavior:

```text
When asked to optimize prompts, give answers from your own perspective - explain what
specific phrases could be added to, or deleted from, this prompt to more consistently
elicit the desired behavior or prevent the undesired behavior.

Here's a prompt: [PROMPT]

The desired behavior from this prompt is for the agent to [DO DESIRED BEHAVIOR], but
instead it [DOES UNDESIRED BEHAVIOR]. While keeping as much of the existing prompt intact
as possible, what are some minimal edits/additions that you would make to encourage the
agent to more consistently address these shortcomings?
```

## Appendix: reference patterns

- **File edits via `apply_patch`.** For coding agents, OpenAI recommends the
  `apply_patch` tool with the V4A diff format (`*** Begin Patch` / `*** Update
  File:` / `@@` context anchors / `-`/`+` lines / `*** End Patch`) to match the
  training distribution. Prefer `rg` / `rg --files` over `ls -R`, `find`, or
  `grep` in large repos.
- **Verification.** For thorough coding rollouts (e.g. SWE-Bench style),
  emphasize that not all tests are visible: "you must double and triple check your
  solutions to ensure they pass any edge cases that are covered in the hidden
  tests, not just the visible ones."
- **Agentic coding harness blocks.** OpenAI's published harnesses combine
  `<persistence>`, `<exploration>` (decompose the request, map scope, check
  dependencies, resolve ambiguity, define the output contract, form an execution
  plan), `<verification>` (verify code runs; kill long-running processes),
  `<efficiency>`, and `<final_instructions>` sections — a useful template for your
  own agentic system prompts.

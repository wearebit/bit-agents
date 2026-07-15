# Prompting best practices (all current Claude models)

Comprehensive guide to prompt engineering techniques for Claude's latest models,
covering clarity, examples, XML structuring, thinking, and agentic systems.

This is the reference for prompt engineering with Claude's latest models,
including Claude Fable 5, Claude Mythos 5, Claude Opus 4.8, Claude Opus 4.7,
Claude Opus 4.6, Claude Sonnet 5, Claude Sonnet 4.6, and Claude Haiku 4.5.

Model-specific guidance lives alongside this file under `models/`:

- Fable 5 / Mythos 5 → `models/fable-5.md`
- Sonnet 5 → `models/sonnet-5.md`
- Opus 4.8 → `models/opus-4.8.md`

Read the relevant model file for behavioral differences and what to change; this
file covers techniques that apply across all current models.

## General principles

The techniques in this section and the sections that follow apply to all current
Claude models, including Claude Fable 5 and Claude Mythos 5.

### Be clear and direct

Claude responds well to clear, explicit instructions. Being specific about your
desired output can help enhance results. If you want "above and beyond" behavior,
explicitly request it rather than relying on the model to infer this from vague
prompts.

Think of Claude as a brilliant but new employee who lacks context on your norms
and workflows. The more precisely you explain what you want, the better the
result.

**Golden rule:** Show your prompt to a colleague with minimal context on the task
and ask them to follow it. If they'd be confused, Claude will be too.

- Be specific about the desired output format and constraints.
- Provide instructions as sequential steps using numbered lists or bullet points
  when the order or completeness of steps matters.

**Example — creating an analytics dashboard.** Less effective: `Create an
analytics dashboard`. More effective: `Create an analytics dashboard. Include as
many relevant features and interactions as possible. Go beyond the basics to
create a fully-featured implementation.`

### Add context to improve performance

Providing context or motivation behind your instructions, such as explaining to
Claude why such behavior is important, can help Claude better understand your
goals and deliver more targeted responses.

**Example — formatting preferences.** Less effective: `NEVER use ellipses`. More
effective: `Your response will be read aloud by a text-to-speech engine, so never
use ellipses since the text-to-speech engine will not know how to pronounce
them.` Claude is smart enough to generalize from the explanation.

### Use examples effectively

Examples are one of the most reliable ways to steer Claude's output format, tone,
and structure. A few well-crafted examples (known as few-shot or multishot
prompting) improve accuracy and consistency.

When adding examples, make them:

- **Relevant:** Mirror your actual use case closely.
- **Diverse:** Cover edge cases and vary enough that Claude doesn't pick up
  unintended patterns.
- **Structured:** Wrap examples in `<example>` tags (multiple examples in
  `<examples>` tags) so Claude can distinguish them from instructions.

Include 3–5 examples for best results. You can also ask Claude to evaluate your
examples for relevance and diversity, or to generate additional ones based on
your initial set.

### Structure prompts with XML tags

XML tags help Claude parse complex prompts unambiguously, especially when your
prompt mixes instructions, context, examples, and variable inputs. Wrapping each
type of content in its own tag (e.g. `<instructions>`, `<context>`, `<input>`)
reduces misinterpretation.

Best practices:

- Use consistent, descriptive tag names across your prompts.
- Nest tags when content has a natural hierarchy (documents inside `<documents>`,
  each inside `<document index="n">`).

### Give Claude a role

Setting a role in the system prompt focuses Claude's behavior and tone for your
use case. Even a single sentence makes a difference — for example, a `system`
value of `You are a helpful coding assistant specializing in Python.` steers tone
and depth for a coding Q&A. Set it via the `system` parameter of the Messages
API.

### Long context prompting

When working with large documents or data-rich inputs (20k+ tokens), structure
your prompt carefully to get the best results:

- **Put longform data at the top:** Place your long documents and inputs near the
  top of your prompt, above your query, instructions, and examples. This improves
  performance across all models. Queries at the end can improve response quality
  by up to 30% in tests, especially with complex, multi-document inputs.
- **Structure document content and metadata with XML tags:** When using multiple
  documents, wrap each document in `<document>` tags with `<document_content>`
  and `<source>` (and other metadata) subtags for clarity.
- **Ground responses in quotes:** For long document tasks, ask Claude to quote
  relevant parts of the documents first before carrying out its task. This helps
  Claude cut through the noise of the rest of the document's contents.

Example multi-document structure:

```xml
<documents>
  <document index="1">
    <source>annual_report_2023.pdf</source>
    <document_content>
      {{ANNUAL_REPORT}}
    </document_content>
  </document>
  <document index="2">
    <source>competitor_analysis_q2.xlsx</source>
    <document_content>
      {{COMPETITOR_ANALYSIS}}
    </document_content>
  </document>
</documents>

Analyze the annual report and competitor analysis. Identify strategic advantages
and recommend Q3 focus areas.
```

### Model self-knowledge

If you would like Claude to identify itself correctly in your application or use
specific API strings:

```text
The assistant is Claude, created by Anthropic. The current model is Claude Opus
4.8.
```

For LLM-powered apps that need to specify model strings:

```text
When an LLM is needed, please default to Claude Opus 4.8 unless the user requests
otherwise. The exact model string for Claude Opus 4.8 is claude-opus-4-8.
```

## Output and formatting

### Communication style and verbosity

Claude's latest models have a more concise and natural communication style
compared to previous models:

- **More direct and grounded:** Provides fact-based progress reports rather than
  self-celebratory updates.
- **More conversational:** Slightly more fluent and colloquial, less
  machine-like.
- **Less verbose:** May skip detailed summaries for efficiency unless prompted
  otherwise.

This means Claude may skip verbal summaries after tool calls, jumping directly to
the next action. If you prefer more visibility into its reasoning:

```text
After completing a task that involves tool use, provide a quick summary of the
work you've done.
```

### Control the format of responses

There are a few particularly effective ways to steer output formatting:

1. **Tell Claude what to do instead of what not to do.** Instead of "Do not use
   markdown in your response," try "Your response should be composed of smoothly
   flowing prose paragraphs."
2. **Use XML format indicators.** Try "Write the prose sections of your response
   in `<smoothly_flowing_prose_paragraphs>` tags."
3. **Match your prompt style to the desired output.** The formatting style used
   in your prompt may influence Claude's response style. For example, removing
   markdown from your prompt can reduce the volume of markdown in the output.
4. **Use detailed prompts for specific formatting preferences.** For more control
   over markdown and formatting usage, provide explicit guidance:

````text
<avoid_excessive_markdown_and_bullet_points>
When writing reports, documents, technical explanations, analyses, or any long-form
content, write in clear, flowing prose using complete paragraphs and sentences. Use
standard paragraph breaks for organization and reserve markdown primarily for `inline
code`, code blocks (```...```), and simple headings (## and ###). Avoid using **bold**
and *italics*.

DO NOT use ordered lists (1. ...) or unordered lists (*) unless: a) you're presenting
truly discrete items where a list format is the best option, or b) the user explicitly
requests a list or ranking

Instead of listing items with bullets or numbers, incorporate them naturally into
sentences. This guidance applies especially to technical writing. Using prose instead of
excessive formatting will improve user satisfaction. NEVER output a series of overly
short bullet points.

Your goal is readable, flowing text that guides the reader naturally through ideas
rather than fragmenting information into isolated points.
</avoid_excessive_markdown_and_bullet_points>
````

### LaTeX output

Claude's latest models default to LaTeX for mathematical expressions, equations,
and technical explanations. If you prefer plain text, add the following
instructions to your prompt:

```text
Format your response in plain text only. Do not use LaTeX, MathJax, or any markup
notation such as \( \), $, or \frac{}{}. Write all math expressions using standard
text characters (e.g., "/" for division, "*" for multiplication, and "^" for
exponents).
```

### Document creation

Claude's latest models create presentations, animations, and visual documents
with strong instruction following, and usually produce usable output on the first
try. For best results:

```text
Create a professional presentation on [topic]. Include thoughtful design
elements, visual hierarchy, and engaging animations where appropriate.
```

### Migrating away from prefilled responses

Starting with Claude 4.6 models and Claude Mythos Preview, prefilled responses
(providing a partial assistant message for Claude to continue from) on the last
assistant turn are no longer supported. Requests with prefilled assistant
messages to these models return a 400 error. Model intelligence and instruction
following have advanced such that most use cases of prefill no longer require it.
Earlier models continue to support prefills, and adding assistant messages
elsewhere in the conversation is not affected. Common prefill scenarios and how to
migrate:

- **Controlling output formatting.** Prefills forced formats like JSON/YAML or
  classification. Migration: use the Structured Outputs feature, or ask the model
  to conform to your output structure (newer models reliably match complex
  schemas, especially with retries). For classification, use tools with an enum
  field or structured outputs.
- **Eliminating preambles.** Prefills like `Here is the requested summary:\n`
  skipped introductory text. Migration: instruct in the system prompt ("Respond
  directly without preamble. Do not start with phrases like 'Here is...',
  'Based on...'"), output within XML tags, use structured outputs or tool
  calling, or strip stray preambles in post-processing.
- **Avoiding bad refusals.** Migration: Claude is much better at appropriate
  refusals now; clear prompting in the `user` message without prefill should
  suffice.
- **Continuations.** Migration: move the continuation to the user message and
  include the interrupted text ("Your previous response was interrupted and ended
  with `[previous_response]`. Continue from where you left off."), or retry.
- **Context hydration and role consistency.** Migration: inject previously
  prefilled-assistant reminders into the user turn; for agentic systems, hydrate
  via tools or during context compaction.

## Tool use

### Tool usage

Claude's latest models are trained for precise instruction following and benefit
from explicit direction to use specific tools. If you say "can you suggest some
changes," Claude will sometimes provide suggestions rather than implementing
them, even if making changes might be what you intended.

For Claude to take action, be more explicit. Less effective (Claude will only
suggest): `Can you suggest some changes to improve this function?`. More
effective (Claude will make the changes): `Change this function to improve its
performance.` or `Make these edits to the authentication flow.`

To make Claude more proactive about taking action by default:

```text
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is
unclear, infer the most useful likely action and proceed, using tools to discover any
missing details instead of guessing. Try to infer the user's intent about whether a tool
call (e.g., file edit or read) is intended or not, and act accordingly.
</default_to_action>
```

If you want the model to be more hesitant by default, only taking action if
requested:

```text
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed to make
changes. When the user's intent is ambiguous, default to providing information, doing
research, and providing recommendations rather than taking action. Only proceed with
edits, modifications, or implementations when the user explicitly requests them.
</do_not_act_before_instructions>
```

Claude Opus 4.5 and Claude Opus 4.6 are also more responsive to the system prompt
than previous models. If your prompts were designed to reduce undertriggering on
tools or skills, these models may now overtrigger. The fix is to dial back
aggressive language: where you might have said "CRITICAL: You MUST use this tool
when...", use more normal prompting like "Use this tool when...".

### Optimize parallel tool calling

Claude's latest models run independent tool calls in parallel: multiple
speculative searches during research, reading several files at once, executing
bash commands in parallel. This behavior is steerable — while the model has a high
success rate without prompting, you can boost this to ~100%:

```text
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the tool
calls, make all of the independent tool calls in parallel. Prioritize calling tools
simultaneously whenever the actions can be done in parallel rather than sequentially.
For example, when reading 3 files, run 3 tool calls in parallel to read all 3 files into
context at the same time. Maximize use of parallel tool calls where possible to increase
speed and efficiency. However, if some tool calls depend on previous calls to inform
dependent values like the parameters, do NOT call these tools in parallel and instead
call them sequentially. Never use placeholders or guess missing parameters in tool
calls.
</use_parallel_tool_calls>
```

To reduce parallel execution: `Execute operations sequentially with brief pauses
between each step to ensure stability.`

## Thinking and reasoning

### Overthinking and excessive thoroughness

Claude Opus 4.6 does more upfront exploration than previous models, especially at
higher effort settings. This initial work often helps optimize final results, but
the model may gather extensive context or pursue multiple threads without being
prompted. If your prompts previously encouraged more thoroughness, tune that
guidance:

- **Replace blanket defaults with more targeted instructions.** Instead of
  "Default to using [tool]," use "Use [tool] when it would enhance your
  understanding of the problem."
- **Remove over-prompting.** Tools that undertriggered in previous models are
  likely to trigger appropriately now. Instructions like "If in doubt, use
  [tool]" will cause overtriggering.
- **Use effort as a fallback.** If Claude continues to be overly aggressive, use a
  lower `effort` setting.

To constrain reasoning:

```text
When you're deciding how to approach a problem, choose an approach and commit to
it. Avoid revisiting decisions unless you encounter new information that directly
contradicts your reasoning. If you're weighing two approaches, pick one and see it
through. You can always course-correct later if the chosen approach fails.
```

If you need a hard ceiling on thinking costs, extended thinking with a
`budget_tokens` cap is still functional on Opus 4.6 and Sonnet 4.6 but is
deprecated. On Claude Opus 4.7 and later, and on Claude Fable 5 and Claude Mythos
5, setting `budget_tokens` returns a 400 error. Prefer lowering the effort setting
or using `max_tokens` as a hard limit with adaptive thinking.

### Leverage thinking & interleaved thinking capabilities

Claude's latest models offer thinking capabilities especially helpful for tasks
involving reflection after tool use or complex multi-step reasoning. Claude Opus
4.6, 4.7, 4.8, and Claude Sonnet 4.6 use adaptive thinking
(`thinking: {type: "adaptive"}`), where Claude dynamically decides when and how
much to think. On Claude Fable 5 and Claude Mythos 5, thinking is always on and
adaptive thinking is the only mode. Claude calibrates thinking based on the
`effort` parameter and query complexity.

You can guide Claude's thinking behavior:

```text
After receiving tool results, carefully reflect on their quality and determine
optimal next steps before proceeding. Use your thinking to plan and iterate based
on this new information, and then take the best next action.
```

The triggering behavior for adaptive thinking is promptable. If the model thinks
more often than you'd like (which can happen with large or complex system
prompts):

```text
Extended thinking adds latency and should only be used when it will meaningfully
improve answer quality - typically for problems that require multi-step reasoning.
When in doubt, respond directly.
```

If you are migrating from extended thinking with `budget_tokens`, replace the
thinking configuration with `thinking: {type: "adaptive"}` and move budget
control to the `effort` parameter (`output_config: {effort: "high"}`). If you are
not using extended thinking, no changes are required. On Claude Opus 4.6 through
4.8 and Claude Sonnet 4.6, thinking is off when you omit the `thinking`
parameter; on Claude Fable 5 and Claude Mythos 5, thinking is always on.

Additional guidance:

- **Prefer general instructions over prescriptive steps.** "Think thoroughly"
  often produces better reasoning than a hand-written step-by-step plan.
- **Multishot examples work with thinking.** Use `<thinking>` tags inside
  few-shot examples to show the reasoning pattern.
- **Manual chain-of-thought as a fallback.** When thinking is off, ask Claude to
  think through the problem, using `<thinking>` and `<answer>` tags to separate
  reasoning from output.
- **Ask Claude to self-check.** Append "Before you finish, verify your answer
  against [test criteria]."
- When extended thinking is disabled, Claude Opus 4.5 is particularly sensitive
  to the word "think" and its variants; consider "consider," "evaluate," or
  "reason through" instead.

## Agentic systems

### Long-horizon reasoning and state tracking

Claude's latest models handle long-horizon reasoning tasks with strong state
tracking, maintaining orientation across extended sessions by making steady
advances on a few things at a time. This especially emerges over multiple context
windows, where Claude can work on a complex task, save state, and continue with a
fresh context window.

#### Context awareness and multi-window workflows

Claude Sonnet 5, Sonnet 4.6, Sonnet 4.5, and Haiku 4.5 feature context awareness,
enabling the model to track its remaining context window ("token budget"). If you
are using an agent harness that compacts context or saves context to external
files (like Claude Code), add this to your prompt so Claude behaves accordingly:

```text
Your context window will be automatically compacted as it approaches its limit, allowing
you to continue working indefinitely from where you left off. Therefore, do not stop
tasks early due to token budget concerns. As you approach your token budget limit, save
your current progress and state to memory before the context window refreshes. Always be
as persistent and autonomous as possible and complete tasks fully, even if the end of
your budget is approaching. Never artificially stop any task early regardless of the
context remaining.
```

For tasks spanning multiple context windows: use a different prompt for the first
window (set up a framework, write tests, create setup scripts), have the model
write tests in a structured format (e.g. `tests.json`), set up quality-of-life
tools (e.g. `init.sh` to start servers, run tests and linters), consider starting
fresh over compaction (Claude's latest models discover state from the filesystem
effectively), and provide verification tools (Playwright MCP server, computer
use). Encourage complete usage of context:

```text
This is a very long task, so it may be beneficial to plan out your work clearly.
It's encouraged to spend your entire output context working on the task - just
make sure you don't run out of context with significant uncommitted work. Continue
working systematically until you have completed this task.
```

State management best practices: use structured formats (JSON) for state data
like test results; use unstructured text for progress notes; use git for state
tracking and checkpoints; emphasize incremental progress.

### Balancing autonomy and safety

Without guidance, Claude Opus 4.6 may take actions that are difficult to reverse
or affect shared systems (deleting files, force-pushing, posting to external
services). To have it confirm before risky actions:

```text
Consider the reversibility and potential impact of your actions. You are encouraged to
take local, reversible actions like editing files or running tests, but for actions that
are hard to reverse, affect shared systems, or could be destructive, ask the user before
proceeding.

Examples of actions that warrant confirmation:
- Destructive operations: deleting files or branches, dropping database tables, rm -rf
- Hard to reverse operations: git push --force, git reset --hard, amending published commits
- Operations visible to others: pushing code, commenting on PRs/issues, sending
messages, modifying shared infrastructure

When encountering obstacles, do not use destructive actions as a shortcut. For example,
don't bypass safety checks (e.g. --no-verify) or discard unfamiliar files that may be
in-progress work.
```

### Research and information gathering

For optimal research results: provide clear success criteria, encourage source
verification, and for complex tasks use a structured approach:

```text
Search for this information in a structured way. As you gather data, develop several
competing hypotheses. Track your confidence levels in your progress notes to improve
calibration. Regularly self-critique your approach and plan. Update a hypothesis tree or
research notes file to persist information and provide transparency. Break down this
complex research task systematically.
```

### Subagent orchestration

Claude's latest models orchestrate subagents natively, recognizing when tasks
benefit from delegation. To take advantage: ensure well-defined subagent tools are
available and described, let Claude orchestrate naturally, and watch for overuse
(Claude Opus 4.6 has a strong predilection for subagents and may spawn them where
a direct grep is faster). If you see excessive subagent use:

```text
Use subagents when tasks can run in parallel, require isolated context, or involve
independent workstreams that don't need to share state. For simple tasks, sequential
operations, single-file edits, or tasks where you need to maintain context across steps,
work directly rather than delegating.
```

### Chain complex prompts

With adaptive thinking and subagent orchestration, Claude handles most multi-step
reasoning internally. Explicit prompt chaining (breaking a task into sequential
API calls) is still useful when you need to inspect intermediate outputs or
enforce a specific pipeline structure. The most common pattern is
self-correction: generate a draft → have Claude review it against criteria → have
Claude refine based on the review, each as a separate API call.

### Reduce file creation in agentic coding

Claude's latest models may create new files for testing and iteration
(a 'temporary scratchpad'), which can improve outcomes. To minimize net new file
creation:

```text
If you create any temporary new files, scripts, or helper files for iteration,
clean up these files by removing them at the end of the task.
```

### Overeagerness

Claude Opus 4.5 and 4.6 have a tendency to overengineer by creating extra files,
adding unnecessary abstractions, or building in unrequested flexibility. To keep
solutions minimal:

```text
Avoid over-engineering. Only make changes that are directly requested or clearly
necessary. Keep solutions simple and focused:

- Scope: Don't add features, refactor code, or make "improvements" beyond what was
asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need
extra configurability.

- Documentation: Don't add docstrings, comments, or type annotations to code you didn't
change. Only add comments where the logic isn't self-evident.

- Defensive coding: Don't add error handling, fallbacks, or validation for scenarios
that can't happen. Trust internal code and framework guarantees. Only validate at system
boundaries (user input, external APIs).

- Abstractions: Don't create helpers, utilities, or abstractions for one-time
operations. Don't design for hypothetical future requirements. The right amount of
complexity is the minimum needed for the current task.
```

### Avoid focusing on passing tests and hard-coding

Claude can sometimes focus too heavily on making tests pass at the expense of
general solutions. To get solutions that generalize:

```text
Please write a high-quality, general-purpose solution using the standard tools
available. Do not create helper scripts or workarounds to accomplish the task more
efficiently. Implement a solution that works correctly for all valid inputs, not just
the test cases. Do not hard-code values or create solutions that only work for specific
test inputs. Instead, implement the actual logic that solves the problem generally.

Focus on understanding the problem requirements and implementing the correct algorithm.
Tests are there to verify correctness, not to define the solution. Provide a principled
implementation that follows best practices and software design principles.

If the task is unreasonable or infeasible, or if any of the tests are incorrect, please
inform me rather than working around them. The solution should be robust, maintainable,
and extendable.
```

### Minimizing hallucinations in agentic coding

To encourage grounded answers and minimize hallucinations:

```text
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file,
you MUST read the file before answering. Make sure to investigate and read relevant
files BEFORE answering questions about the codebase. Never make any claims about code
before investigating unless you are certain of the correct answer - give grounded and
hallucination-free answers.
</investigate_before_answering>
```

## Capability-specific tips

### Improved vision capabilities

Claude Opus 4.5 and 4.6 have improved vision capabilities: better image
processing and data extraction, particularly with multiple images in context.
These improvements carry over to computer use. You can analyze videos by breaking
them into frames. One effective technique is giving Claude a crop tool or skill —
testing shows consistent uplift when Claude can "zoom" into relevant regions.

### Frontend design

Claude Opus 4.5 and 4.6 build complex web applications with strong frontend
design. Without guidance, models can default to generic patterns users call the
"AI slop" aesthetic. To create distinctive frontends:

```text
<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this
creates what users call the "AI slop" aesthetic. Avoid this: make creative, distinctive
frontends that surprise and delight.

Focus on:
- Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic
fonts like Arial and Inter; opt instead for distinctive choices that elevate the
frontend's aesthetics.
- Color & Theme: Commit to a cohesive aesthetic. Use CSS variables for consistency.
Dominant colors with sharp accents outperform timid, evenly-distributed palettes. Draw
from IDE themes and cultural aesthetics for inspiration.
- Motion: Use animations for effects and micro-interactions. Prioritize CSS-only
solutions for HTML. Use Motion library for React when available. Focus on high-impact
moments: one well-orchestrated page load with staggered reveals (animation-delay)
creates more delight than scattered micro-interactions.
- Backgrounds: Create atmosphere and depth rather than defaulting to solid colors. Layer
CSS gradients, use geometric patterns, or add contextual effects that match the overall
aesthetic.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts)
- Clichéd color schemes (particularly purple gradients on white backgrounds)
- Predictable layouts and component patterns
- Cookie-cutter design that lacks context-specific character

Interpret creatively and make unexpected choices that feel genuinely designed for the
context. Vary between light and dark themes, different fonts, different aesthetics. You
still tend to converge on common choices (Space Grotesk, for example) across
generations. Avoid this: it is critical that you think outside the box!
</frontend_aesthetics>
```

## Migration considerations

When migrating to Claude 4.6 models from earlier generations:

1. **Be specific about desired behavior.** Describe exactly what you'd like to see
   in the output.
2. **Frame your instructions with modifiers.** Instead of "Create an analytics
   dashboard," use "Create an analytics dashboard. Include as many relevant
   features and interactions as possible. Go beyond the basics to create a
   fully-featured implementation."
3. **Request specific features explicitly.** Animations and interactive elements
   should be requested explicitly when desired.
4. **Update thinking configuration.** Claude 4.6 models use adaptive thinking
   (`thinking: {type: "adaptive"}`) instead of manual thinking with
   `budget_tokens`. Use the effort parameter to control thinking depth.
5. **Migrate away from prefilled responses.** Prefilled responses on the last
   assistant turn are no longer supported starting with Claude 4.6 models.
6. **Tune anti-laziness prompting.** If your prompts previously encouraged the
   model to be more thorough or use tools more aggressively, dial back that
   guidance — Claude 4.6 models are more proactive and may overtrigger.
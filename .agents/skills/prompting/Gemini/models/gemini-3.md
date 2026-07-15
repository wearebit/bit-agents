# Prompting Google Gemini 3

Prompting guidance specific to Gemini 3 models. Adapted from Google's Gemini API
"Prompt design strategies" guide.

For general Gemini technique, see the sibling `../general.md`. This file covers
what's specific to Gemini 3.

Gemini 3 models are designed for advanced reasoning and instruction following.
They respond best to prompts that are direct, well-structured, and clearly define
the task and any constraints.

## Core prompting principles

- **Be precise and direct.** State your goal clearly and concisely; avoid
  unnecessary or overly persuasive language.
- **Use consistent structure.** Use clear delimiters to separate parts of the
  prompt — XML-style tags (`<context>`, `<task>`) or Markdown headings. Pick one
  format and use it consistently within a prompt.
- **Define parameters.** Explicitly explain any ambiguous terms.
- **Control output verbosity.** By default Gemini 3 gives direct, efficient
  answers. If you want a more conversational or detailed response, explicitly
  request it.
- **Handle multimodal inputs coherently.** Treat text, images, audio, and video
  as equal-class inputs, and reference each modality clearly in your instructions.
- **Prioritize critical instructions.** Put essential behavioral constraints,
  persona/role, and output-format requirements in the system instruction or at the
  very beginning of the user prompt.
- **Structure for long contexts.** Supply all large context (documents, code)
  first, then place your specific instructions or question at the very *end*.
- **Anchor context.** After a large block of data, bridge to your query with a
  transition like "Based on the information above…".

> **Default sampling parameters.** Keep `temperature`, `top_p`, and `top_k` at
> their defaults for Gemini 3.x. Lowering temperature below 1.0 can cause looping
> or degraded performance, especially on complex math or reasoning.

## Enhancing reasoning and planning

Gemini 2.5 and 3 series models automatically generate internal "thinking" text to
improve reasoning, so it's generally unnecessary to have the model outline, plan,
or detail reasoning steps in the returned response itself. For heavy-reasoning
problems, a simple request like "Think very hard before answering" can improve
performance, at the cost of extra thinking tokens.

## Gemini 3 Flash strategies

Add these clauses to the system instructions where relevant:

- **Current-day accuracy** (helps the model use the correct current date in tool
  calls):

```text
For time-sensitive user queries that require up-to-date information, you MUST follow the provided current time (date and year) when formulating search queries in tool calls. Remember it is 2026 this year.
```

- **Knowledge-cutoff accuracy:**

```text
Your knowledge cutoff date is January 2025.
```

- **Grounding performance** (restrict answers strictly to provided context):

```text
You are a strictly grounded assistant limited to the information provided in the User Context. In your answers, rely **only** on the facts that are directly mentioned in that context. You must **not** access or utilize your own knowledge or common sense to answer. Do not assume or infer from the provided facts; simply report them exactly as they appear. Your answer must be factual and fully truthful to the provided text, leaving absolutely no room for speculation or interpretation. Treat the provided context as the absolute limit of truth; any facts or details that are not directly mentioned in the context must be considered **completely untruthful** and **completely unsupported**. If the exact answer is not explicitly written in the context, you must state that the information is not available.
```

## Structured prompting examples

Tags or Markdown help the model distinguish instructions, context, and tasks.

**XML:**

```text
<role>
You are a helpful assistant.
</role>

<constraints>
1. Be objective.
2. Cite sources.
</constraints>

<context>
[Insert User Input Here - The model knows this is data, not instructions]
</context>

<task>
[Insert the specific user request here]
</task>
```

**Markdown:**

```text
# Identity
You are a senior solution architect.

# Constraints
- No external libraries allowed.
- Python 3.11+ syntax only.

# Output format
Return a single code block.
```

## Example template combining best practices

Iterate on this for your use case.

**System instruction:**

```text
<role>
You are Gemini 3, a specialized assistant for [Insert Domain, e.g., Data Science].
You are precise, analytical, and persistent.
</role>

<instructions>
1. **Plan**: Analyze the task and create a step-by-step plan.
2. **Execute**: Carry out the plan.
3. **Validate**: Review your output against the user's task.
4. **Format**: Present the final answer in the requested structure.
</instructions>

<constraints>
- Verbosity: [Specify Low/Medium/High]
- Tone: [Specify Formal/Casual/Technical]
</constraints>

<output_format>
Structure your response as follows:
1. **Executive Summary**: [Short overview]
2. **Detailed Response**: [The main content]
</output_format>
```

**User prompt:**

```text
<context>
[Insert relevant documents, code snippets, or background info here]
</context>

<task>
[Insert specific user request here]
</task>

<final_instruction>
Remember to think step-by-step before answering.
</final_instruction>
```

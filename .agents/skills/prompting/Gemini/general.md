# Prompting best practices (Google Gemini)

Prompt design technique for Google's Gemini, combining Google's "Gemini for
Workspace: Prompting 101" (conversational framework) and the Gemini API "Prompt
design strategies" guide (API-side technique).

Model-specific files live alongside this one under `models/`:

- Gemini 3 → `models/gemini-3.md`

Read the relevant model file for behavior specific to that generation; this file
covers technique that applies across Gemini surfaces (Gemini Advanced, the API,
and Gemini embedded in Workspace apps). Prompt design is iterative — treat
everything here as a starting point and refine against observed responses.

## The four building blocks: Persona, Task, Context, Format

An effective Gemini prompt is built from up to four parts. You don't need all
four every time, but using several improves results.

- **Persona** — who the model should act as ("You are a program manager in
  [industry]").
- **Task** — what to do. **Always include a verb/command** (summarize, write,
  classify, create, draft). This is the single most important component.
- **Context** — the details, background, and data it should draw on (in
  Workspace, tag your own files with `@file name`).
- **Format** — the shape of the output ("Limit to bullet points", "put it in a
  table", "one sentence").

Example combining all four:

```text
You are a program manager in [industry]. Draft an executive summary email to [persona] based on [details about relevant program docs]. Limit to bullet points.
```

## Clear and specific instructions

The most effective way to customize behavior is clear, specific instructions —
a question, step-by-step tasks, or a full description of the desired experience.

**Input** is the required text you want a response to. Four common kinds:

- **Question** — the model answers ("What's a good name for a flower shop that
  specializes in dried flowers? List 5 options, names only.").
- **Task** — the model performs an action ("Give me a list of just the 5 things I
  must bring on a camping trip.").
- **Entity** — the model operates on something you give it ("Classify the
  following as [large, small]: Elephant, Mouse, Snail.").
- **Completion** — you provide partial content and the model continues it (see
  below).

### Partial-input completion

Generative models work like advanced autocompletion: give partial content and the
model continues it, taking any examples or context into account. This is often
cleaner than describing a format in prose. For example, to get a JSON order object
that omits unordered items, show one example and let the model complete the next:

```text
Valid fields are cheeseburger, hamburger, fries, and drink.
Order: Give me a cheeseburger and fries
Output:
{ "cheeseburger": 1, "fries": 1 }
Order: I want two burgers, a drink, and fries.
Output:
```

For complex JSON schemas, prefer the Gemini API's **structured output** feature
over prompt-only formatting.

### Constraints

State what to do and not do, e.g. length limits: "Summarize this text in one
sentence: …".

### Response format

Specify the output format (table, bulleted list, elevator pitch, keywords,
sentence, paragraph). A system instruction can set a default, e.g. "All questions
should be answered comprehensively with details, unless the user requests a
concise response specifically."

The **completion strategy** also shapes format: instead of asking for an outline
and letting the model choose the format, seed the start of the outline and let it
continue the pattern:

```text
Create an outline for an essay about hummingbirds.
I. Introduction
*
```

## Zero-shot vs few-shot prompts

Including examples (few-shot) shows the model what "getting it right" looks like;
prompts with no examples are zero-shot. Few-shot prompts regulate formatting,
phrasing, scoping, and patterning. **Always include few-shot examples when you
can** — prompts without them are usually less effective, and clear examples can
even let you drop instructions entirely.

- **Optimal number:** a few examples is often enough; experiment. Too many can
  cause the model to overfit to the examples.
- **Consistent formatting:** keep structure identical across examples (XML tags,
  whitespace, newlines, splitters). Showing the response format is a primary
  purpose of examples, so inconsistency produces inconsistent output.

Example: two few-shot examples that prefer the shorter of two explanations reliably
steer the model to pick concise answers, where the zero-shot version picked the
verbose one.

## Add context

Include the information the model needs to solve the problem rather than assuming
it already has it. Grounding a request in provided text turns a generic answer
into a specific one — e.g. pasting a router's LED troubleshooting table alongside
"Answer the question using the text below. Respond with only the text provided."
yields the exact relevant step instead of generic advice.

## Break down complex prompts

- **Break down instructions:** one prompt per instruction, and choose which to run
  based on the user's input, rather than cramming many instructions into one.
- **Chain prompts:** for multi-step tasks, make each step a prompt where the
  output of one feeds the next; the last output is the result.
- **Aggregate responses:** run different operations on different portions of the
  data in parallel and combine the results.

## Experiment with model parameters

Each request includes parameters that control generation; different values give
different results, and available parameters differ by model.

- **Max output tokens** — cap on generated tokens (~4 chars/token; 100 tokens ≈
  60–80 words).
- **Temperature** — randomness in token selection. Lower is more deterministic
  (0 always picks the highest-probability token); higher is more diverse/creative.
- **`topK`** — sample from the K highest-probability tokens (`topK` 1 = greedy).
- **`topP`** — sample from the most-probable tokens until their probabilities sum
  to `topP` (default 0.95).
- **`stop_sequences`** — character sequences that halt generation; avoid sequences
  likely to appear in the output.

> **Gemini 3.x:** although you *can* modify `temperature`, `top_p`, and `top_k`,
> Google strongly recommends keeping them at their defaults for Gemini 3.x models.
> Changing them (e.g. temperature below 1.0) can cause looping or degraded
> performance, especially on complex math or reasoning.

## Prompt iteration strategies

Design usually takes a few iterations. When results fall short:

- **Use different phrasing.** Different wording of the same request yields
  different responses ("How do I bake a pie?" vs "Suggest a recipe for a pie." vs
  "What's a good pie recipe?").
- **Switch to an analogous task.** If the model won't follow instructions one way,
  reframe — e.g. turn "Which category does X belong to: …" into an explicit
  "Multiple choice problem: … Options: -a -b -c" to force a single-option answer.
- **Change the order of prompt content.** The order of examples, context, and
  input can affect the response; try reordering.

## Fallback responses

A fallback response ("I'm not able to help with that, as I'm only a language
model.") is returned when the prompt or response trips a safety filter. If you get
one, try increasing the temperature.

## Grounding and code execution

Gemini can use tools to avoid hallucinations:

- **Grounding with Google Search** connects the model to real-time web content —
  enable it whenever the model may need obscure or recent facts.
- **Code execution** lets the model generate and run Python — enable it whenever
  the model needs arithmetic, counting, or calculation.

## Agentic workflows

Deep agentic workflows often need explicit instructions controlling how the model
reasons, plans, and executes, and require you to configure the trade-off between
computational cost (latency, tokens) and task accuracy. Dimensions you can steer:

- **Reasoning and strategy** — logical decomposition (how thoroughly to analyze
  constraints, prerequisites, order of operations), problem diagnosis (depth of
  cause analysis and abductive reasoning), and information exhaustiveness
  (analyze everything vs. prioritize speed).
- **Execution and reliability** — adaptability (stick to the plan vs. pivot on
  contradicting observations), persistence and recovery (self-correction vs.
  token cost / loop risk), and risk assessment (low-risk reads vs. high-risk
  writes).
- **Interaction and output** — ambiguity and permission handling (when to assume
  vs. pause and ask), verbosity (explain actions vs. stay silent during
  execution), and precision and completeness (exact figures and every edge case
  vs. ballpark estimates).

Google publishes a benchmark-evaluated system-instruction template for agents that
must follow a complex rulebook while interacting with a user. It instructs the
agent to act as a strong reasoner/planner and, before any action, to reason
methodically about: (1) logical dependencies and constraints (resolved in
importance order: policy rules → order of operations → prerequisites → user
preferences); (2) risk assessment (missing optional params on exploratory reads is
low-risk — prefer calling the tool over asking); (3) abductive reasoning and
hypothesis exploration (look beyond obvious causes, don't discard low-probability
ones prematurely); (4) outcome evaluation and adaptability (regenerate hypotheses
when disproven); (5) information availability (tools, policies, history, and asking
the user); (6) precision and grounding (quote exact applicable policy text); (7)
completeness (exhaustively incorporate requirements; avoid premature conclusions);
(8) intelligent persistence (retry transient errors up to any stated limit; change
strategy on other errors); and (9) inhibiting the response until all reasoning is
complete, since actions can't be undone. Adapt it to your own constraints.

## Review before acting

Generative AI output can be unpredictable. Before putting a Gemini output into
action, review it for clarity, relevance, and accuracy. The model assists; the
final output is yours.

## Leveling up

- **Break it up.** Use separate prompts for several related tasks.
- **Give constraints.** Include character limits or a number of options for
  specific results.
- **Assign a role.** Open with a role to encourage the right voice.
- **Ask for feedback.** Give the project and desired output, then ask "What
  questions do you have for me that would help you provide the best output?".
- **Consider tone.** Request a specific tone matched to the audience.
- **Say it another way.** Rephrase and refine when results fall short.

Observed rule of thumb from Workspace usage: the most effective prompts average
around **21 words** of relevant context, yet people often try prompts under nine
words. Add context.

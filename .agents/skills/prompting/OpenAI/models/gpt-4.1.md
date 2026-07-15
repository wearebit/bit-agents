# Prompting OpenAI GPT-4.1

Prompt GPT-4.1 for coding, instruction following, long context, and tool use.
Adapted from OpenAI's "GPT-4.1 prompting guide".

For general GPT-family techniques, see the sibling `../general.md`. GPT-4.1 is not
a reasoning model, so its patterns differ from the GPT-5 family; this file is the
canonical reference for the GPT-4.1 family.

## New in GPT-4.1 vs GPT-4o

- Closer and more literal instruction following than previous GPT models.
- Stronger coding and long-context behavior (1M-token context window).
- Better API-native tool use when schemas are passed through the `tools` field.
- Prompt migration guidance for agentic workflows and diff generation.

GPT-4.1 follows instructions more closely and more literally than its
predecessors, which inferred intent more liberally. This makes it highly steerable
and responsive to well-specified prompts: if behavior differs from what you
expect, a single sentence firmly and unequivocally clarifying the desired behavior
is almost always enough to steer it. Because it follows instructions literally,
prompts optimized for other models may not transfer directly — implicit rules are
no longer inferred as strongly. AI engineering is empirical; build evals and
iterate.

## 1. Agentic workflows

### System prompt reminders

Include three key reminders in agent prompts. These transform the model from a
chatbot-like state into an "eager" agent; together they raised OpenAI's internal
SWE-bench Verified score by ~20%.

**Persistence** (prevents premature yielding):

```text
You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Only terminate your turn when you are sure that the problem is solved.
```

**Tool-calling** (reduces hallucination/guessing):

```text
If you are not sure about file content or codebase structure pertaining to the user's request, use your tools to read files and gather the relevant information: do NOT guess or make up an answer.
```

**Planning** (optional — makes the model plan and reflect in text between tool
calls; raised the SWE-bench pass rate a further ~4%):

```text
You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.
```

### Tool calls

Pass tools exclusively via the API `tools` field rather than injecting descriptions
into the prompt and writing a custom parser — this keeps the model in distribution
and raised SWE-bench pass rate ~2% versus manual injection. Name tools and their
params clearly, with a thorough but concise `description`. For complex tools, put
usage examples in an `# Examples` section of the system prompt rather than in the
`description` field.

### Sample SWE-bench Verified system prompt

The canonical prompt behind OpenAI's highest SWE-bench Verified score. Reusable as
a general agentic-coding template:

```text
You will be tasked to fix an issue from an open-source repository.

Your thinking should be thorough and so it's fine if it's very long. You can think step by step before and after each action you decide to take.

You MUST iterate and keep going until the problem is solved.

You already have everything you need to solve this problem in the /testbed folder, even without internet connection. I want you to fully solve this autonomously before coming back to me.

Only terminate your turn when you are sure that the problem is solved. Go through the problem step by step, and make sure to verify that your changes are correct. NEVER end your turn without having solved the problem, and when you say you are going to make a tool call, make sure you ACTUALLY make the tool call, instead of ending your turn.

THE PROBLEM CAN DEFINITELY BE SOLVED WITHOUT THE INTERNET.

Take your time and think through every step - remember to check your solution rigorously and watch out for boundary cases, especially with the changes you made. Your solution must be perfect. If not, continue working on it. At the end, you must test your code rigorously using the tools provided, and do it many times, to catch all edge cases. If it is not robust, iterate more and make it perfect. Failing to test your code sufficiently rigorously is the NUMBER ONE failure mode on these types of tasks; make sure you handle all edge cases, and run existing tests if they are provided.

You MUST plan extensively before each function call, and reflect extensively on the outcomes of the previous function calls. DO NOT do this entire process by making function calls only, as this can impair your ability to solve the problem and think insightfully.

# Workflow
## High-Level Problem Solving Strategy
1. Understand the problem deeply. Carefully read the issue and think critically about what is required.
2. Investigate the codebase. Explore relevant files, search for key functions, and gather context.
3. Develop a clear, step-by-step plan. Break down the fix into manageable, incremental steps.
4. Implement the fix incrementally. Make small, testable code changes.
5. Debug as needed. Use debugging techniques to isolate and resolve issues.
6. Test frequently. Run tests after each change to verify correctness.
7. Iterate until the root cause is fixed and all tests pass.
8. Reflect and validate comprehensively. After tests pass, think about the original intent, write additional tests to ensure correctness, and remember there are hidden tests that must also pass before the solution is truly complete.

(Then the detailed per-step sections: Deeply Understand the Problem, Codebase Investigation, Develop a Detailed Plan, Making Code Changes, Debugging, Testing, Final Verification, and Final Reflection and Additional Testing — each expanding the step above with concrete tactics like reading files before editing, fixing root causes over symptoms, running tests after each change, and writing new tests for hidden edge cases.)
```

## 2. Long context

GPT-4.1 has a 1M-token input context window, useful for structured document
parsing, re-ranking, selecting relevant information while ignoring irrelevant
context, and multi-hop reasoning. Needle-in-a-haystack performance is very good up
to the full 1M tokens, but performance can degrade as more items must be retrieved
or when a task requires knowledge of the entire context (e.g. graph search).

**Tuning context reliance** — control the mix of external vs. internal knowledge:

```text
# Instructions
// for internal knowledge
- Only use the documents in the provided External Context to answer the User Query. If you don't know the answer based on this context, you must respond "I don't have the information needed to answer that", even if a user insists on you answering the question.
// For internal and external knowledge
- By default, use the provided external context to answer the User Query, but if other basic knowledge is needed to answer, and you're confident in the answer, you can use some of your own knowledge to help answer the question.
```

**Prompt organization** — in long context, place instructions at both the
beginning and end of the provided context (best); if only once, above the context
beats below.

## 3. Chain of thought

GPT-4.1 is not a reasoning model, but prompting it to think step by step breaks
problems into manageable pieces and improves output quality, at the cost of more
output tokens. Start with a basic instruction at the end of your prompt:

```text
First, think carefully step by step about what documents are needed to answer the query. Then, print out the TITLE and ID of each document. Then, format the IDs into a list.
```

Improve the CoT prompt by auditing failures (misunderstanding intent, insufficient
context gathering, faulty step-by-step thinking) and codifying strategies that
work. A more methodical example:

```text
# Reasoning Strategy
1. Query Analysis: Break down and analyze the query until you're confident about what it might be asking. Consider the provided context to help clarify any ambiguous or confusing information.
2. Context Analysis: Carefully select and analyze a large set of potentially relevant documents. Optimize for recall - it's okay if some are irrelevant, but the correct documents must be in this list, otherwise your final answer will be wrong. Analysis steps for each:
    a. Analysis: An analysis of how it may or may not be relevant to answering the query.
    b. Relevance rating: [high, medium, low, none]
3. Synthesis: summarize which documents are most relevant and why, including all documents with a relevance rating of medium or higher.

# User Question
{user_question}

# External Context
{external_context}

First, think carefully step by step about what documents are needed to answer the query, closely adhering to the provided Reasoning Strategy. Then, print out the TITLE and ID of each document. Then, format the IDs into a list.
```

## 4. Instruction following

GPT-4.1 follows instructions literally, so specify explicitly what to do or not
do. Recommended workflow for developing instructions:

1. Start with a high-level "Response Rules" / "Instructions" section of bullets.
2. To change a specific behavior, add a dedicated section (e.g. `# Sample
   Phrases`).
3. For a required sequence, add an ordered list and instruct the model to follow
   the steps.
4. If behavior still isn't right: check for conflicting/underspecified/wrong
   instructions (GPT-4.1 tends to follow the instruction closest to the end of the
   prompt); add examples demonstrating the behavior, and make sure any behavior in
   examples is also stated in the rules; avoid all-caps/bribes/tips by default (add
   only if needed — and note that pre-existing such techniques can make GPT-4.1
   over-attend to them).

**Common failure modes:**

- "You must call a tool before responding" can induce hallucinated tool inputs or
  null-value calls when the model lacks information. Mitigate with: "if you don't
  have enough information to call the tool, ask the user for the information you
  need."
- Given sample phrases, the model may repeat them verbatim; instruct it to vary
  them.
- Without instruction, the model may add explanatory prose or extra formatting;
  constrain with instructions and examples.

**Customer-service example** (best-practice structure — diverse rules,
specificity, detail sections, and one example that incorporates all rules):

```text
You are a helpful customer service agent working for NewTelco, helping a user efficiently fulfill their request while adhering closely to provided guidelines.

# Instructions
- Always greet the user with "Hi, you've reached NewTelco, how can I help you?"
- Always call a tool before answering factual questions about the company, its offerings or products, or a user's account. Only use retrieved context and never rely on your own knowledge for any of these questions.
    - However, if you don't have enough information to properly call the tool, ask the user for the information you need.
- Escalate to a human if the user requests.
- Do not discuss prohibited topics (politics, religion, controversial current events, medical, legal, or financial advice, personal conversations, internal company operations, or criticism of any people or company).
- Rely on sample phrases whenever appropriate, but never repeat a sample phrase in the same conversation. Feel free to vary the sample phrases to avoid sounding repetitive and make it more appropriate for the user.
- Always follow the provided output format for new messages, including citations for any factual statements from retrieved policy documents.
- If you're going to call a tool, always message the user with an appropriate message before and after calling the tool.
- Maintain a professional and concise tone in all responses, and use emojis between sentences.
- If you've resolved the user's request, ask if there's anything else you can help with.

# Precise Response Steps (for each response)
1. If necessary, call tools to fulfill the user's desired action. Always message the user before and after calling a tool to keep them in the loop.
2. In your response to the user
    a. Use active listening and echo back what you heard the user ask for.
    b. Respond appropriately given the above guidelines.

# Sample Phrases
## Deflecting a Prohibited Topic
- "I'm sorry, but I'm unable to discuss that topic. Is there something else I can help you with?"
- "That's not something I'm able to provide information on, but I'm happy to help with any other questions you may have."
## Before calling a tool
- "To help you with that, I'll just need to verify your information."
- "Let me check that for you—one moment, please."
## After calling a tool
- "Okay, here's what I found: [response]"
- "So here's what I found: [response]"

# Output Format
- Always include your final response to the user.
- When providing factual information from retrieved context, always include citations immediately after the relevant statement(s): for a single source [NAME](ID); for multiple sources [NAME](ID), [NAME](ID).
- Only provide information about this company, its policies, its products, or the customer's account, and only if it is based on information provided in context.
```

## 5. General advice

**Prompt structure** — a good starting point:

```text
# Role and Objective
# Instructions
## Sub-categories for more detailed instructions
# Reasoning Steps
# Output Format
# Examples
## Example 1
# Context
# Final instructions and prompt to think step by step
```

**Delimiters** — general guidance:

1. **Markdown** — start here: titles for sections/subsections (to H4+), inline
   backticks / backtick blocks for code, standard lists.
2. **XML** — also performs well; convenient to wrap sections with start/end, add
   metadata to tags, and nest. Example nesting examples in an example section:

```text
<examples>
<example1 type="Abbreviate">
<input>San Francisco</input>
<output>- SF</output>
</example1>
</examples>
```

3. **JSON** — highly structured and well understood, especially in coding
   contexts, but verbose and requires character escaping.

For large numbers of documents in context: XML performed well
(`<doc id='1' title='The Fox'>...</doc>`); the `ID: 1 | TITLE: ... | CONTENT: ...`
format also performed well; **JSON performed particularly poorly** for document
lists. Match the delimiter to the content (e.g. don't use XML delimiters around
documents that themselves contain lots of XML).

**Caveats:**

- The model can resist producing very long, repetitive outputs (e.g. analyzing
  hundreds of items one by one). If needed, instruct strongly to output in full, or
  break the problem down.
- Parallel tool calls can occasionally be incorrect; test, and consider setting
  `parallel_tool_calls` to false if you see issues.

## Appendix: generating and applying file diffs

GPT-4.1 has substantially improved diff capabilities. OpenAI's recommended,
extensively-trained format is **V4A**, exposed through an `apply_patch` tool.

The `apply_patch` tool takes an `input` string of this shape:

```text
%%bash
apply_patch <<"EOF"
*** Begin Patch
[YOUR_PATCH]
*** End Patch
EOF
```

`[YOUR_PATCH]` uses the V4A diff format:

```text
*** [ACTION] File: [path/to/file]   (ACTION = Add | Update | Delete)
[context_before]
- [old_code]
+ [new_code]
[context_after]
```

Key rules: no line numbers — context uniquely identifies code. Show 3 lines of
context above and below each change (don't duplicate context between changes within
3 lines of each other). If 3 lines are insufficient to identify the snippet
uniquely, use `@@ class/def` anchors, and stack multiple `@@` statements when even
one anchor plus 3 lines isn't unique:

```text
%%bash
apply_patch <<"EOF"
*** Begin Patch
*** Update File: pygorithm/searching/binary_search.py
@@ class BaseClass
@@     def search():
-        pass
+        raise NotImplementedError()
*** End Patch
EOF
```

File references must be relative, never absolute. `apply_patch` always prints
"Done!" regardless of success; detect problems by reading warning/logging lines
printed *before* "Done!".

**Reference implementation.** OpenAI open-sources a self-contained pure-Python 3.9+
`apply_patch.py` (used in model training) that parses V4A patches and applies them
to a set of text files: a `Parser` that reads `*** Add/Update/Delete File`
sections and `@@` context anchors, fuzzy context matching (`find_context` /
`find_context_core` with rstrip/strip fallbacks and a fuzz counter), conversion of
the parsed `Patch` into a `Commit` of `FileChange`s, and filesystem helpers
(`open_file` / `write_file` / `remove_file`) plus a `main()` that reads patch text
from stdin. Make it executable and available as `apply_patch` on the PATH where the
model runs commands. (Not reproduced here in full — pull it from OpenAI's guide if
you need the exact source.)

**Other effective diff formats.** In testing, the SEARCH/REPLACE format (from
Aider's polyglot benchmark) and a pseudo-XML format with no internal escaping both
had high success rates. Both (1) avoid line numbers and (2) give the exact code to
replace and its replacement with clear delimiters between them:

```text
path/to/file.py
>>>>>>> SEARCH
def search():
    pass
=======
def search():
   raise NotImplementedError()
<<<<<<< REPLACE
```

```text
<edit>
<file>path/to/file.py</file>
<old_code>
def search():
    pass
</old_code>
<new_code>
def search():
   raise NotImplementedError()
</new_code>
</edit>
```

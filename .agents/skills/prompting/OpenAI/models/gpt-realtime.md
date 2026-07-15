# Prompting OpenAI gpt-realtime

Prompt `gpt-realtime` — OpenAI's speech-to-speech (S2S) model behind the
generally available Realtime API — with labeled prompt sections, bulleted rules,
sample phrases, and pacing/pronunciation controls tuned for voice. Adapted from
OpenAI's "Realtime Prompting Guide" (Minhajul Hoque).

Realtime is a different medium from text: the model both listens to and speaks
audio, so techniques that never come up for text models (speaking pace,
pronunciation, handling unclear audio, masking tool latency with spoken
preambles) become central. The model-agnostic foundation in the parent
`SKILL.md` still applies — treat the prompt as a spec, structure it, phrase
constraints positively, iterate empirically. The sibling `../general.md` (GPT-5)
and `gpt-4.1.md` cover text-family tactics; OpenAI recommends GPT-4.1-style
prompting for the instruction/tool portions of a Realtime prompt. This file
covers what is specific to voice.

## General tips

- **Iterate relentlessly.** Small wording changes make or break behavior. One
  real example: swapping "inaudible" → "unintelligible" measurably improved
  noisy-input handling.
- **Prefer bullets over paragraphs.** Short, clear bullets outperform long prose.
- **Guide with examples.** The model follows sample phrases closely, so a few
  well-chosen ones steer style hard.
- **Be precise.** Ambiguous or conflicting instructions degrade performance, the
  same way they do on GPT-5.
- **Pin the language** if you see unwanted language switching (see below).
- **Add a variety rule** to reduce robotic, repetitive phrasing (see below).
- **CAPITALIZE key rules** for emphasis — capitalized rules stand out and are
  easier for the model to follow.
- **Convert non-text rules to text.** Instead of `IF x > 3 THEN ESCALATE`, write
  "IF MORE THAN THREE FAILURES THEN ESCALATE".

## Prompt structure

Use clear, labeled sections so the model can find and follow them, and so you can
iterate on one problematic section at a time. Keep each section focused on one
thing. Add domain-specific sections (Compliance, Brand Policy) as needed and drop
ones you don't (e.g. Reference Pronunciations if pronunciation is fine).

```text
# Role & Objective         — who you are and what "success" means
# Personality & Tone       — the voice and style to maintain
# Context                  — retrieved context, relevant info
# Reference Pronunciations — phonetic guides for tricky words
# Tools                    — names, usage rules, and preambles
# Instructions / Rules     — do's, don'ts, and approach
# Conversation Flow        — states, goals, and transitions
# Safety & Escalation      — fallback and handoff logic
```

## Role and objective

Pin who the agent is and what "done" means. The model adheres tightly to an
explicit role — including accent and character — so state it plainly.

```text
# Role & Objective
You are a french quebecois speaking customer service bot. Your task is to answer the user's question.
```

```text
# Role & Objective
You are a high-energy game-show host guiding the caller to guess a secret number from 1 to 100 to win 1,000,000$.
```

## Personality and tone

Sets voice, brevity, and pacing so replies sound natural and consistent. Reach
for this when responses feel flat, overly verbose, or inconsistent across turns.
Tune warmth/formality and default length; for regulated domains, favor neutral
precision.

```text
# Personality & Tone
## Personality
- Friendly, calm and approachable expert customer service assistant.

## Tone
- Warm, concise, confident, never fawning.

## Length
- 2–3 sentences per turn.
```

The model can also follow complex, shifting emotional directions within a single
response:

```text
# Personality & Tone
- Start your response very happy
- Midway, change to sad
- At the end change your mood to very angry
```

### Speed

The API `speed` parameter changes playback rate, not how the model *composes*
speech. To actually sound faster without sounding rushed, instruct the pacing —
and tell it not to shorten the content, only speed up delivery.

```text
## Pacing
- Deliver your audio response fast, but do not sound rushed.
- Do not modify the content of your response, only increase speaking speed for the same response.
```

### Language

Lock output to a target language to prevent accidental switching in multilingual
or noisy environments. Swap "English" for your target language, or layer more
complex rules (e.g. explain in one language, practice in another for a tutor).

```text
## Language
- The conversation will be only in English.
- Do not respond in any other language even if the user asks.
- If the user speaks another language, politely explain that support is limited to English.
```

A language tutor can deliberately code-switch by scoping each language to a task:

```text
## Language
### Explanations
Use English when explaining grammar, vocabulary, or cultural context.

### Conversation
Speak in French when conducting practice, giving examples, or engaging in dialogue.
```

### Variety

The model follows sample phrases closely, which keeps it on-brand but can make it
recycle the same openings and fillers until it sounds robotic. Add a variety
constraint when that happens. Tune strictness ("don't reuse the same opener more
than once every N turns") and whitelist must-keep legal/compliance/brand phrases.

```text
## Variety
- Do not repeat the same sentence twice.
- Vary your responses so it doesn't sound robotic.
```

## Reference pronunciations

Give phonetic hints for brand names, technical terms, and locations that are
often mispronounced. Keep it a short list and update it as you hear errors.
gpt-realtime follows these reliably (e.g. it now says "sequel" for SQL where the
older `gpt-4o-realtime-preview` did not).

```text
# Reference Pronunciations
When voicing these words, use the respective pronunciations:
- Pronounce "SQL" as "sequel."
- Pronounce "PostgreSQL" as "post-gress."
- Pronounce "Kyiv" as "KEE-iv."
- Pronounce "Huawei" as "HWAH-way"
```

### Alphanumeric pronunciations

S2S can blur or merge digits and letters when reading back phone numbers, card
numbers, 2FA codes, order IDs, serials, or addresses. Force character-by-character
delivery with separators, then confirm and re-confirm after corrections.
Optionally add a phonetic disambiguator ("A as in Alpha").

```text
# Instructions/Rules
- When reading numbers or codes, speak each character separately, separated by hyphens (e.g., 4-1-5).
- Repeat EXACTLY the provided number, do not forget any.
```

If you use a conversation-flow / state-machine prompt, you can instead scope this
to the specific state that collects the number:

```json
{
  "id": "3_get_and_verify_phone",
  "description": "Request phone number and verify by repeating it back.",
  "instructions": [
    "Politely request the user's phone number.",
    "Once provided, confirm it by repeating each digit and ask if it's correct.",
    "If the user corrects you, confirm AGAIN to make sure you understand."
  ],
  "examples": [
    "I'll need some more information to access your account if that's okay. May I have your phone number, please?",
    "You said 0-2-1-5-5-5-1-2-3-4, correct?",
    "You said 4-5-6-7-8-9-0-1-2-3, correct?"
  ],
  "transitions": [{
    "next_step": "4_authentication_DOB",
    "condition": "Once phone number is confirmed"
  }]
}
```

The effect: "The number is 55119765423" becomes "The number is:
5-5-1-1-1-9-7-6-5-4-2-3."

## Instructions

For the instruction and rule portions of the prompt, OpenAI recommends
GPT-4.1-style prompting (see `gpt-4.1.md`). As with GPT-4.1 and GPT-5, conflicting,
ambiguous, or unclear instructions degrade the model — it drifts from rules, skips
phases, or misuses tools.

### Audit your prompt with a critique pass

Run your prompt through GPT-5 first to surface ambiguity, missing definitions, and
conflicts before you ship:

```text
## Role & Objective
You are a **Prompt-Critique Expert**.
Examine a user-supplied LLM prompt and surface any weaknesses following the instructions below.

## Instructions
Review the prompt that is meant for an LLM to follow and identify the following issues:
- Ambiguity: Could any wording be interpreted in more than one way?
- Lacking Definitions: Are there any class labels, terms, or concepts that are not defined that might be misinterpreted by an LLM?
- Conflicting, missing, or vague instructions: Are directions incomplete or contradictory?
- Unstated assumptions: Does the prompt assume the model has to be able to do something that is not explicitly stated?

## Do **NOT** list issues of the following types:
- Invent new instructions, tool calls, or external information. You do not know what tools need to be added that are missing.
- Issues that you are unsure about.

## Output Format
"""
# Issues
- Numbered list; include brief quote snippets.

# Improvements
- Numbered list; provide the revised lines you would change and how you would change them.

# Revised Prompt
- Revised prompt where you have applied all your improvements surgically with minimal edits to the original prompt
"""
```

To fix a specific failure mode, give GPT-5 the current prompt plus the observed
issue and ask for tightened variants:

```text
Here's my current prompt to an LLM:
[BEGIN OF CURRENT PROMPT]
{CURRENT_PROMPT}
[END OF CURRENT PROMPT]

But I see this issue happening from the LLM:
[BEGIN OF ISSUE]
{ISSUE}
[END OF ISSUE]
Can you provide some variants of the prompt so that the model can better understand the constraints to alleviate the issue?
```

### No audio or unclear audio

Background noise, partial words, or silence can make the model think it heard
something and respond anyway. Tell it how to behave on unclear input — ask for
clarification, or repeat the last question, depending on your use case.

```text
# Instructions/Rules
...
## Unclear audio
- Always respond in the same language the user is speaking in, if unintelligible.
- Only respond to clear audio or text.
- If the user's audio is not clear (e.g. ambiguous input/background noise/silent/unintelligible) or if you did not fully hear or understand the user, ask for clarification using {preferred_language} phrases.
```

### Background music or sounds

Occasionally the model emits unintended humming, rhythmic noise, or sound-like
artifacts. Steer it away explicitly, adapting the wording to the specific artifact
you hear:

```text
# Instructions/Rules
...
- Do not include any sound effects or onomatopoeic expressions in your responses.
```

## Tools

Tell the model when and when not to call each tool, which arguments to collect,
what to say while a call runs, and how to handle errors.

### Tool selection

gpt-realtime follows instructions well — which means a prompt that mentions tools
not present in the `tools` list (or descriptions that contradict the prompt) leads
to bad responses. Keep the prompt's tool section and the actual `tools` list in
sync, with non-contradictory descriptions.

### Tool call preambles

Having the model speak a short line at the same time it fires a tool call masks
latency and reassures the user.

```text
# Tools
- Before any tool call, say one short line like "I'm checking that now." Then call the tool immediately.
```

To control the wording more tightly, put sample preamble phrases directly in the
tool's `description`:

```python
tools = [
  {
    "name": "lookup_account",
    "description": "Retrieve a customer account using either an email or phone number to enable verification and account-specific actions.\n\nPreamble sample phrases:\n- For security, I'll pull up your account using the email on file.\n- Let me look up your account by {email} now.\n- One moment—I'm opening your account details.",
    "parameters": { "...": "..." }
  }
]
```

### Tool calls without confirmation

If the model asks permission before obvious calls, tell it to be proactive:

```text
# Tools
- When calling a tool, do not ask for any user confirmation. Be proactive.
```

If it then jumps to tools too eagerly, soften the wording — swap "proactive" for
something gentler to get a calmer approach.

### Tool call performance

As the number of tools grows, state explicitly when to use and — just as
importantly — when *not* to use each one, plus valid call sequences.

```text
# Tools
- When you call any tools, you must output at the same time a response letting the user know that you are calling the tool.

## lookup_account(email_or_phone)
Use when: verifying identity or viewing plan/outage flags.
Do NOT use when: the user is clearly anonymous and only asks general questions.

## check_outage(address)
Use when: user reports connectivity issues or slow speeds.
Do NOT use when: question is billing-only.

## refund_credit(account_id, minutes)
Use when: confirmed outage > 240 minutes in the past 7 days.
Do NOT use when: outage is unconfirmed; route to Diagnose → check_outage first.

## escalate_to_human(account_id, reason)
Use when: user seems very frustrated, abuse/harassment, repeated failures, billing disputes >$50, or user requests escalation.
```

Add explicit failure-handling instructions for any tool that can fail
unpredictably, so the model responds gracefully.

### Tool-level behavior

Instead of one global rule, tag tools with the behavior they need — e.g. READ
tools proactive, WRITE tools confirmation-first.

```text
# TOOLS
- For the tools marked PROACTIVE: do not ask for confirmation and do not output a preamble.
- For the tools marked CONFIRMATION FIRST: always ask for confirmation.
- For the tools marked PREAMBLES: before the call, say one short line like "I'm checking that now." Then call the tool immediately.

## lookup_account(email_or_phone) — PROACTIVE
Use when: verifying identity or accessing billing.

## refund_credit(account_id, minutes) — CONFIRMATION FIRST
Use when: confirmed outage > 240 minutes in the past 7 days (credit 60 minutes).
Confirmation phrase: "I can issue a credit for this outage—would you like me to go ahead?"

## escalate_to_human(account_id, reason) — PREAMBLES
Use when: harassment, threats, self-harm, repeated failure, billing disputes > $50, frustration, or escalation request.
Preamble: "Let me connect you to a senior agent who can assist further."
```

### Tool output formatting

Long strings a tool returns that must be repeated verbatim are out-of-distribution
— training-time tool outputs look like JSON objects with named fields. A raw
string plus a separate "repeat exactly" instruction invites paraphrasing,
truncation, or blended-in commentary. Wrap the output in a small, stable JSON
envelope and make the verbatim requirement machine-explicit.

More error-prone — raw string:

```text
I just sent you an email with the verification link. Please open it and click "Confirm".
```

More reliable — wrapped JSON:

```json
{
  "response_text": "I just sent you an email with the verification link. Please open it and click \"Confirm\".",
  "require_repeat_verbatim": true
}
```

Document the shape in both the Tools section and next to the tool definition,
e.g. "If `require_repeat_verbatim` is true, output exactly `response_text` and
nothing else; do not add, omit, or reorder fields."

### Rephrase supervisor tool (responder–thinker)

A common architecture: the realtime model is the *responder* (speaks) while a
stronger text model is the *thinker* (planning, policy lookups). Text replies
aren't automatically good speech, so instruct the responder to rephrase the
thinker's text into a short, natural, speech-first reply before voicing it.

```text
# Tools
## Supervisor Tool
Name: getNextResponseFromSupervisor(relevantContextFromLastUserMessage: string)

When to call:
- Any request outside the allow list.
- Any factual, policy, account, or process question.

When not to call:
- Simple greetings and basic chitchat.
- Requests to repeat or clarify.

Usage rules and preamble:
1) Say a neutral filler phrase, then immediately call the tool. Approved fillers: "One moment.", "Let me check.", "Just a second." Fillers must not imply success or failure.
2) Do not mention the "Supervisor" in the filler.
3) relevantContextFromLastUserMessage is a one-line summary of the latest user message; use an empty string if nothing salient.
4) After the tool returns, apply Rephrase Supervisor and send your reply.

### Rephrase Supervisor
- Start with a brief conversational opener ("Thanks for waiting—", "I've got that pulled up now.") then flow into the answer.
- Keep it short: no more than 2 sentences.
- Template: opener + one-sentence gist + up to 3 key details + a quick confirmation or choice.
- Read numbers for speech: money naturally ("$45.20" → "forty-five dollars and twenty cents"), phone numbers 3-3-4, addresses digit-by-digit, dates/times plainly.
```

Without rephrasing: "Your current credit card balance is positive at 32,323,232
AUD." With it: "Just finished checking that—your credit card balance is
thirty-two million three hundred twenty-three thousand two hundred thirty-two
dollars in your favor. Your last payment was processed on August first. Does that
match what you expected?"

### Common tools

The model was trained on these common tools. If your use case is similar, keep the
names, signatures, and descriptions close to these to stay in-distribution.

```text
# answer(question: string)
Description: Call this when the customer asks a question that you don't have an answer to or asks to perform an action.

# escalate_to_human()
Description: Call this when a customer asks for escalation, or to talk to someone else, or expresses dissatisfaction with the call.

# finish_session()
Description: Call this when a customer says they're done or doesn't want to continue. If ambiguous, confirm before calling.
```

## Conversation flow

Structure the dialogue into goal-driven phases, each with a goal, how-to-respond
rules, and concrete exit criteria. This stops the model from stalling, skipping
steps, or jumping ahead, and it makes error modes easier to isolate. Keep "Exit
when" concrete and minimal.

```text
# Conversation Flow
## 1) Greeting
Goal: Set tone and invite the reason for calling.
How to respond:
- Identify as NorthLoop Internet Support.
- Keep the opener brief and invite the caller's goal.
- Confirm the caller is a NorthLoop customer.
Exit when: Caller confirms they're a customer and states a goal or symptom.

## 2) Discover
Goal: Classify the issue and capture minimal details.
How to respond:
- Determine billing vs connectivity with one targeted question.
- For connectivity: collect the service address. For billing: collect email or phone.
Exit when: Intent and address (connectivity) or email/phone (billing) are known.

## 3) Verify
Goal: Confirm identity and retrieve the account.
How to respond:
- Call lookup_account(email_or_phone). If it fails, try the alternate identifier once; otherwise offer escalation.
Exit when: Account ID is returned.

## 4) Diagnose
Goal: Decide outage vs local issue.
How to respond:
- Call check_outage(address). If outage=true, skip local steps. If false, guide a short reboot/cabling check, confirming each result.
Exit when: Root cause known.

## 5) Resolve
Goal: Apply fix, credit, or appointment.
How to respond:
- Outage > 240 min in the last 7 days → refund_credit(account_id, 60).
- outage=false and issue persists → offer a window and schedule_technician(account_id, window).
Exit when: A fix/credit/appointment is applied and acknowledged.

## 6) Confirm/Close
Goal: Confirm outcome and end cleanly.
How to respond:
- Restate the result and next step; invite final questions; close politely.
Exit when: Caller declines more help.
```

### Sample phrases

Sample phrases are anchor examples for style, brevity, and tone — without locking
the model into one rigid response. Always include the "vary your responses"
warning, and add the Variety constraint if the model starts parroting them
verbatim.

```text
# Sample Phrases
- Below are examples for inspiration. DO NOT ALWAYS USE THESE, VARY YOUR RESPONSES.
Acknowledgements: "On it." "One moment." "Good question."
Clarifiers: "Do you want A or B?" "What's the deadline?"
Empathy (brief): "That's frustrating—let's fix it."
Closers: "Anything else before we wrap?" "Happy to help next time."
```

A strong pattern is to embed sample phrases inside each conversation-flow state so
the model learns what a good response in that state sounds like:

```text
## 1) Greeting
Goal: Set tone and invite the reason for calling.
Sample phrases (do not always repeat the same phrases, vary your responses):
- "Thanks for calling NorthLoop Internet—how can I help today?"
- "You've reached NorthLoop Support. What's going on with your service?"
Exit when: Caller states an initial goal or symptom.
```

## Advanced conversation flow

As use cases grow, balance maintainability against simplicity — too many rigid
states overload the model, hurting performance and making conversations feel
robotic. Design flows that *reduce* the model's perceived complexity.

### As a state machine

Encode states and transitions as a JSON structure. It's easy to reason about
coverage, spot edge cases, version, and diff, and it gives fine-grained control
over exactly when the conversation moves on.

```json
# Conversation States
[
  {
    "id": "1_greeting",
    "description": "Begin with a warm greeting, identifying the service and offering help.",
    "instructions": [
      "Use the company name 'Snowy Peak Boards' and provide a warm welcome.",
      "Let them know upfront that account-specific help needs some verification details."
    ],
    "examples": ["Hello, this is Snowy Peak Boards. Thanks for reaching out! How can I help you today?"],
    "transitions": [
      { "next_step": "2_get_first_name", "condition": "Once greeting is complete." },
      { "next_step": "3_get_and_verify_phone", "condition": "If the user provides their first name." }
    ]
  },
  {
    "id": "2_get_first_name",
    "description": "Ask for the user's first name only.",
    "instructions": [
      "Politely ask, 'Who do I have the pleasure of speaking with?'",
      "Do NOT verify or spell back the name; just accept it."
    ],
    "examples": ["Who do I have the pleasure of speaking with?"],
    "transitions": [{ "next_step": "3_get_and_verify_phone", "condition": "Once name is obtained, OR already provided." }]
  }
]
```

### Dynamic flow via `session.update`

Instead of exposing every rule and tool at once, provide only what's relevant to
the active phase, then swap the instructions and tools with a `session.update`
event when the phase's exit conditions are met. This lowers the model's cognitive
load.

```python
from typing import Dict, List, Literal

State = Literal["verify", "resolve"]

# Allowed transitions
TRANSITIONS: Dict[State, List[State]] = {
    "verify": ["resolve"],
    "resolve": []  # terminal
}

def build_state_change_tool(current: State) -> dict:
    allowed = TRANSITIONS[current]
    readable = ", ".join(allowed) if allowed else "no further states (terminal)"
    return {
        "type": "function",
        "name": "set_conversation_state",
        "description": (
            f"Switch the conversation phase. Current: '{current}'. "
            f"You may switch only to: {readable}. "
            "Call this AFTER exit criteria are satisfied."
        ),
        "parameters": {
            "type": "object",
            "properties": {"next_state": {"type": "string", "enum": allowed}},
            "required": ["next_state"]
        }
    }

# Minimal business tools per state
TOOLS_BY_STATE: Dict[State, List[dict]] = {
    "verify": [{
        "type": "function",
        "name": "lookup_account",
        "description": "Fetch account by email or phone.",
        "parameters": {
            "type": "object",
            "properties": {"email_or_phone": {"type": "string"}},
            "required": ["email_or_phone"]
        }
    }],
    "resolve": [{
        "type": "function",
        "name": "schedule_technician",
        "description": "Book a technician visit.",
        "parameters": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string"},
                "window": {"type": "string", "enum": ["10-12 ET", "14-16 ET"]}
            },
            "required": ["account_id", "window"]
        }
    }]
}

# Short, phase-specific instructions
INSTRUCTIONS_BY_STATE: Dict[State, str] = {
    "verify": (
        "# Role & Objective\n"
        "Verify identity to access the account.\n\n"
        "# Conversation (Verify)\n"
        "- Ask for the email or phone on the account.\n"
        "- Read back digits one-by-one (e.g., '4-1-5… Is that correct?').\n"
        "Exit when: Account ID is returned.\n"
        "When exit is satisfied: call set_conversation_state(next_state=\"resolve\")."
    ),
    "resolve": (
        "# Role & Objective\n"
        "Apply a fix by booking a technician.\n\n"
        "# Conversation (Resolve)\n"
        "- Offer two windows: '10–12 ET' or '2–4 ET'.\n"
        "- Book the chosen window.\n"
        "Exit when: Appointment is confirmed.\n"
        "When exit is satisfied: end the call politely."
    )
}

def build_session_update(state: State) -> dict:
    """Return the JSON payload for a Realtime `session.update` event."""
    return {
        "type": "session.update",
        "session": {
            "instructions": INSTRUCTIONS_BY_STATE[state],
            "tools": TOOLS_BY_STATE[state] + [build_state_change_tool(state)]
        }
    }
```

## Safety and escalation

A reliable path to a human matters for voice agents. Define concrete escalation
triggers and exactly what to say — and note the character-count-style rules are
written out as text ("2 failed attempts", "3 consecutive no-match events") per the
general tip on converting non-text rules to text.

```text
# Safety & Escalation
When to escalate (no extra troubleshooting):
- Safety risk (self-harm, threats, harassment)
- User explicitly asks for a human
- Severe dissatisfaction (e.g., "extremely frustrated," repeated complaints, profanity)
- 2 failed tool attempts on the same task, OR 3 consecutive no-match/no-input events
- Out-of-scope or restricted (e.g., real-time news, financial/legal/medical advice)

What to say WHILE calling the escalate_to_human tool (MANDATORY):
- "Thanks for your patience—I'm connecting you with a specialist now."
- Then call the tool: escalate_to_human

Examples that require escalation:
- "This is the third time the reset didn't work. Just get me a person."
- "I am extremely frustrated!"
```

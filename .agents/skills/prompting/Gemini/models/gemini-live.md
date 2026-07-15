# Prompting Google Gemini Live API

Prompting guidance for the Gemini **Live API** — the low-latency, persistent
WebSocket interface for real-time voice (and video) agents, covering models such
as `gemini-live-2.5-flash` and `gemini-3.1-flash-live-preview`. Adapted from
Google's "Live API best practices" guide.

> **Preview.** The Live API is in preview; details may change.

Live is a different medium from text: the model streams audio in and out over a
persistent session, so concerns that never arise for text prompts — speaking
persona/accent, per-turn re-billing of the growing context, interruption
handling, session resumption, audio resampling — become first-class. The
model-agnostic foundation in the parent `SKILL.md` and the sibling `../general.md`
still apply; `gemini-3.md` covers the reasoning-model tactics. This file covers
what's specific to real-time voice.

## Design clear system instructions

Give the model a clearly-defined set of system instructions (SIs) ordered as
**persona → conversational rules → guardrails**. Put each distinct agent in its
own SI rather than combining agents.

1. **Persona.** Give the agent's name, role, and characteristics. If you specify
   an accent, also specify the output language (e.g. a British accent *for an
   English speaker*).
2. **Conversational rules.** List them in the order you expect them followed, and
   distinguish one-time steps from loops:
   - *One-time element:* gather the customer's details once (name, location,
     loyalty card number).
   - *Conversational loop:* the user may move freely between recommendations,
     pricing, returns, and delivery — tell the model it's fine to stay in this
     loop as long as the user wants.
3. **Tool calls in distinct sentences.** Spell out invocation as its own step,
   e.g. "Your first step is to gather user information. First, ask the user for
   their name, location, and loyalty card number. Then invoke `get_user_info`
   with these details."
4. **Guardrails.** State what you don't want, with concrete "if *x* happens, do
   *y*" examples. If precision is still lacking, the word **unmistakably** nudges
   the model to be exact.

## Define tools precisely

Be specific in tool definitions, and always state *under what conditions* a tool
should be invoked. Include names, descriptions, parameters, and an explicit
invocation condition per tool (see the example below). The model performs best on
tasks with **single** function calls, so decompose multi-call flows into distinct,
condition-gated steps.

## Craft effective prompts

- **Use clear prompts with examples.** Show what the model should and shouldn't
  do, and keep to one persona/role per prompt. Prefer prompt *chaining* over
  lengthy multi-page prompts — the model does best with single function calls.
- **Provide starting commands.** The Live API waits for user input before
  responding. To have it open the conversation, include an instruction to greet
  the user or begin — and include user info so it can personalize the greeting.

## Specify language

For the cascaded `gemini-live-2.5-flash`, match the API's `language_code` to the
language the user speaks. If the model must respond in a non-English language, add
this to the system instructions (the capitalization and "unmistakably" are
deliberate):

```text
RESPOND IN {OUTPUT_LANGUAGE}. YOU MUST RESPOND UNMISTAKABLY IN {OUTPUT_LANGUAGE}.
```

## Streaming and audio

These are client-side implementation rules, but they directly affect latency and
perceived responsiveness, so treat them as part of the agent design.

- **Chunk size.** Send audio in 20–40 ms chunks. Don't buffer significantly
  (e.g. 1 s) before sending — small chunks (20–100 ms) minimize latency.
- **Resampling.** Resample microphone input (often 44.1 kHz or 48 kHz) down to
  16 kHz before transmitting.
- **Interruption handling.** When the user speaks while the model is replying, the
  server sends a `server_content` message with `"interrupted": true`. Immediately
  discard your client-side audio buffer so the agent stops talking over the user.
- **`generationComplete`.** Use this signal to know when the model has finished a
  response, so the UI can update or the next action can proceed.

## Session and context management

Native audio tokens accumulate fast — roughly **25 tokens per second of audio** —
so long sessions need active management:

- **Context window compression.** Without it, audio-only sessions cap at ~15
  minutes and audio-video at ~2 minutes. Enable `ContextWindowCompressionConfig`
  to extend sessions to unlimited duration (see *Managing costs* for tuning).
- **Session resumption.** The server may periodically reset the WebSocket. Retain
  the latest token from `SessionResumptionUpdate` messages and pass it as the
  handle on reconnect to resume without losing context. Tokens are valid for 2
  hours after the last session terminates.
- **`GoAway` messages.** The server sends `GoAway` before terminating a
  connection. Listen for it and use `timeLeft` to gracefully wrap up or reconnect
  before the connection closes.

## Pricing and billing

The Live API bills strictly by token usage, and because the session is persistent,
costs **compound**: each turn (one user input + the model's response) is billed
for *all* tokens currently in the context window — new tokens plus accumulated
history, re-processed up to your configured window size. Cost per turn therefore
rises as the conversation lengthens.

- **Audio tokens.** History is retained as raw audio tokens (to preserve tone), so
  every turn is billed for the accumulated audio at the standard audio input rate.
- **Transcription surcharge.** Enabling `inputAudioTranscription` or
  `outputAudioTranscription` adds text-output-rate charges for the generated
  transcription text, *on top of* audio token costs.
- **Managing costs with context limits.** Configure `contextWindowCompression`
  with a compression trigger (e.g. 25,000 tokens) and a sliding window (e.g. 8,000
  tokens). The API evicts older tokens past the threshold, then bills subsequent
  turns only for the retained history plus new tokens.
- **Proactive audio mode.** When enabled, input tokens are billed the entire time
  the API is listening; output tokens only when it responds. Not supported on
  `gemini-3.1-flash-live-preview` — for that model you're billed for audio only
  while actively streaming input.

## Example: career coach

Combines the SI design (persona → rules → guardrails) with condition-gated tool
calls. Note the CAPITALIZED constraints and the "for as long as the client wants"
loop marker.

```text
**Persona:**
You are Laura, a career coach from Brooklyn, NY. You specialize in providing data driven advice to give your clients a fresh perspective on the career questions they're navigating. Your special sauce is providing quantitative, data-driven insights to help clients think about their issues in a different way. You leverage statistics, research, and psychology as much as possible. You only speak to your clients in English, no matter what language they speak to you in.

**Conversational Rules:**
1. **Introduce yourself:** Warmly greet the client.
2. **Intake:** Ask for your client's full name, date of birth, and state they're calling in from. Call `create_client_profile` to create a new patient profile.
3. **Discuss the client's issue:** Get a sense of what the client wants to cover in the session. DO NOT repeat what the client is saying back to them. Don't ask more than a few questions here.
4. **Reframe the client's issue with real data:** NO PLATITUDES. Start providing data-driven insights, embedded as general facts within conversation. Show them a new way of thinking about something. Let this step go on for as long as the client wants. If the client mentions wanting to take any actions, call `add_action_items_to_profile` to remind them later.
5. **Next appointment:** Call `get_next_appointment` to see if one is already scheduled. If so, share the date/time and confirm attendance. If not, call `get_available_appointments`, share the openings, ask their preference, and save it with `schedule_appointment`. If the client prefers to schedule offline, let them know that's fine and to use the patient portal.

**General Guidelines:** Be a witty, snappy conversational partner. Keep responses short and progressively disclose more if the client requests it. Don't repeat back what the client says. Each response should be a net new addition, not a recap. Be relatable by bringing in your own background growing up professionally in Brooklyn, NY. If a client tries to get you off track, gently bring them back to the workflow above.

**Guardrails:** If the client is being hard on themselves, never encourage that. Your ultimate goal is to create a supportive environment for your clients to thrive.
```

### Tool definitions

Each function includes a name, description, parameters, and — critically — an
**invocation condition** stated inside the description, so the model knows exactly
when to call it and in what sequence.

```json
[
  {
    "name": "create_client_profile",
    "description": "Creates a new client profile with their personal details. Returns a unique client ID. \n**Invocation Condition:** Invoke this tool *only after* the client has provided their full name, date of birth, AND state. This should only be called once at the beginning of the 'Intake' step.",
    "parameters": {
      "type": "object",
      "properties": {
        "full_name": { "type": "string", "description": "The client's full name." },
        "date_of_birth": { "type": "string", "description": "The client's date of birth in YYYY-MM-DD format." },
        "state": { "type": "string", "description": "The 2-letter postal abbreviation for the client's state (e.g., 'NY', 'CA')." }
      },
      "required": ["full_name", "date_of_birth", "state"]
    }
  },
  {
    "name": "add_action_items_to_profile",
    "description": "Adds a list of actionable next steps to a client's profile using their client ID. \n**Invocation Condition:** Invoke this tool *only after* a list of actionable next steps has been discussed and agreed upon with the client. Requires the `client_id` obtained from the start of the session.",
    "parameters": {
      "type": "object",
      "properties": {
        "client_id": { "type": "string", "description": "The unique ID of the client, obtained from create_client_profile." },
        "action_items": {
          "type": "array",
          "items": { "type": "string" },
          "description": "A list of action items for the client (e.g., ['Update resume', 'Research three companies'])."
        }
      },
      "required": ["client_id", "action_items"]
    }
  },
  {
    "name": "get_next_appointment",
    "description": "Checks if a client has a future appointment already scheduled using their client ID. Returns the appointment details or null. \n**Invocation Condition:** Invoke this tool at the *start* of the 'Next Appointment' step. This is used to check if an appointment *already exists*.",
    "parameters": {
      "type": "object",
      "properties": {
        "client_id": { "type": "string", "description": "The unique ID of the client." }
      },
      "required": ["client_id"]
    }
  },
  {
    "name": "get_available_appointments",
    "description": "Fetches a list of the next available appointment slots. \n**Invocation Condition:** Invoke this tool *only if* `get_next_appointment` was called and returned `null` (or empty), indicating no future appointment is scheduled.",
    "parameters": { "type": "object", "properties": {} }
  },
  {
    "name": "schedule_appointment",
    "description": "Books a new appointment for a client at a specific date and time. \n**Invocation Condition:** Invoke this tool *only after* `get_available_appointments` has been called, openings have been presented, and the client has *explicitly confirmed* the specific date and time.",
    "parameters": {
      "type": "object",
      "properties": {
        "client_id": { "type": "string", "description": "The unique ID of the client." },
        "appointment_datetime": { "type": "string", "description": "The chosen appointment slot in ISO 8601 format (e.g., '2025-10-30T14:30:00')." }
      },
      "required": ["client_id", "appointment_datetime"]
    }
  }
]
```

# Tone Guide

## Funny mode — default

Use dry, brief, evidence-led humor. The joke should sharpen the diagnosis, not replace it. The draft reply itself must be visibly funny; a funny diagnosis followed by an ordinary professional email fails funny mode.

The joke must make sense immediately. If the reader has to decode a metaphor before understanding the problem, rewrite it. Prefer a familiar reaction, an obvious contradiction, a revealing count, or one simple joke about a specific unsupported claim. Then state the requested fix in plain language.

Good shapes:

- `A human was here.`
- `There is a useful memo inside this memo.`
- `1,842 words entered. No recommendation emerged.`
- `The reader has been assigned the thinking.`
- `The chatbot packaging is still attached.`

Rules:

- Use at most one joke in the diagnosis and one artifact-specific comic turn in the reply.
- Prefer counts and observable contradictions over generic snark.
- Short, familiar reactions such as `Seriously, bruh?` or `Be so for real.` are allowed when they fit the user's voice. Use one, not a stack.
- Keep the joke to one idea. Do not stack metaphors, puns, or comic images.
- Avoid clever metaphors that make the reader translate the joke before acting on the request.
- Avoid emojis, obscure meme slang, theatrical outrage, and claims about who wrote the document.
- Roast the document, never the sender.
- Keep the draft reply safe to send to a colleague.
- Use ordinary workplace language. Internal rubric terms are for scoring only.

Funny-mode acceptance test:

1. The reply opens with or contains one comic turn tied to a real receipt from this artifact.
2. The comic turn would sound out of place in the serious reply. If it would not, the reply is not funny enough.
3. After the joke, the reply names the minimum concrete revision needed.
4. Removing the joke leaves a useful, sendable request.
5. A colleague understands both the joke and the request on the first read.

Bad contrast:

- Funny: `Please clarify whether this is a 90-day or six-month pilot and add the requested evidence.`
- Serious: `Please clarify the pilot duration and add the requested evidence.`

The first version is not funny; it is merely more specific.

Good contrast:

- Funny: `Seriously, bruh? Is this a 90-day pilot or a six-month pilot? The memo says both. Pick one timeline, use our Q2 utilization, SLA, and survey data, and remove the chatbot's offer to make slides.`
- Serious: `Please resolve the conflicting pilot durations and rebuild the recommendation around our Q2 utilization, SLA, and survey data. Include the scope, metrics, risks, checkpoint, and a clear go or no-go, and remove the closing presentation offer.`

## Plain-language boundary

Use `Human delta` as the named concept in the verdict table: it means what the person contributed beyond the obvious generated answer. Do not use it inside the diagnosis or draft reply.

Translate the remaining internal labels:

- `reader burden` → say what work the recipient still has to do
- `review diligence` → say whether unfinished drafting language remains
- `evidence-backed path` → say `choose one option and show us why`
- `decision-ready recommendation` → say `recommend one option and tell us what decision you need`

Explain the human-delta rating with concrete facts, judgment, or decisions from the document. For every other phrase, if a colleague would have to ask what it means, rewrite it before rendering. Prefer verbs and concrete nouns: `choose`, `show`, `name`, `cut`, `verify`, `owner`, `date`, `cost`, and `result`.

## Serious mode

Use direct, neutral workplace language. Preserve the same verdict, receipts, and requested revision. Remove jokes rather than euphemizing the evidence.

## Draft-reply requirements

- **ACCEPT:** No draft unless requested.
- **REQUEST_COMPRESSION:** Name the useful thinking, specify the shorter shape, and request the decision or action first.
- **REQUEST_JUDGMENT:** Ask for the sender's recommendation, verification, constraints, tradeoffs, or other missing human delta relevant to the assignment.
- **RETURN_FOR_REVISION:** State what work remains with the reader and list the minimum components required in the revision.
- **REQUEST_CONTEXT:** Ask for the original assignment or missing source. Do not accuse.

Do not offer to rewrite the document for the recipient.

## Funny draft-reply bank

Use these as patterns, not canned text. Preserve the document's real nouns, evidence, decisions, and requested action. Select no more than one joke and make the revision request concrete. A pattern must be customized enough that its joke could not be pasted onto an unrelated document.

### Request compression

- `Six pages, one recommendation, and it does not appear until page six. Please move it to page one and cut anything that does not change it.`

### Request judgment

- `Bold strategy: recommend every option and choose none. Pick one, show us why, and name the tradeoff you are accepting.`
- `This has 14 priorities, which is a creative way to have zero priorities. Pick the top two and tell us what can wait.`

### Return for revision

- `Seriously, bruh? This says [duration A] here and [duration B] there. Pick one timeline, show the evidence behind it, and tell us what decision you need.`
- `The 30% estimate appears to come from the Department of Vibes. Add the actual source, check the number, and revise the recommendation if it does not hold up.`
- `Be so for real. This document gives the reader three surprise jobs: check the numbers, reconcile the plan, and make the recommendation. Please do those before sending it back.`

### AI paste residue

- `The chatbot is still offering to make slides. Delete that line, check for any other assistant leftovers, and resend the reviewed version.`
- `The prompt is still in the document. At least the chatbot showed its work. Remove it, finish the placeholders, and send back only the version meant for the reader.`

### Request context

- `Mind reading is not installed. Send the original assignment and intended reader so I can tell whether this did the job.`

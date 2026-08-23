# Tone Guide

## Funny readout — default

Use dry, brief, evidence-led humor in the diagnosis. The joke should sharpen one specific receipt from the document, not replace the evidence.

Good shapes:

- `A human was here.`
- `1,842 words entered. No recommendation emerged.`
- `The chatbot packaging is still attached.`
- `Two timelines. Zero requested evidence. Seriously, bruh?`

Rules:

- Use at most one joke in the diagnosis.
- Prefer an observable contradiction or revealing count over a metaphor.
- Short reactions such as `Seriously, bruh?` or `Be so for real.` are allowed when they fit the evidence.
- The joke must make sense immediately. Do not stack metaphors, puns, or comic images.
- Roast the document and the burden it creates, never the sender.
- Keep jokes out of receipts, ratings, trust findings, and limitations.

Funny-mode acceptance test:

1. The diagnosis contains one unmistakable comic turn tied to a real receipt.
2. A colleague understands the joke on the first read.
3. The joke would sound out of place in the serious diagnosis.
4. Removing the joke leaves the evidence and recommended action intact.

## Serious readout

Use direct, neutral workplace language. Preserve the same verdict, receipts, trust findings, and recommended action. Remove the joke without softening the evidence.

## Plain-language boundary

Use `Human delta` as the named concept in the verdict table: it means what the person contributed beyond the obvious generated answer. Keep it out of the diagnosis and any optional send-back version.

Translate the remaining internal labels:

- `reader burden` → say what work the recipient still has to do
- `review diligence` → say whether unfinished drafting language remains
- `evidence-backed path` → say `choose one option and show us why`
- `decision-ready recommendation` → say `recommend one option and tell us what decision you need`

Prefer concrete verbs and nouns such as `choose`, `show`, `name`, `cut`, `verify`, `owner`, `date`, `cost`, and `result`.

## Optional send-back versions

The initial workslop readout does not include an outbound message. After a result that calls for compression, judgment, or revision, offer to turn the readout into one of these formats:

- **Short Slack or Teams reply:** one to three sentences with the main failure and the minimum revision needed.
- **Professional revision request:** a neutral workplace message that names the evidence, decision, or cleanup required.
- **Blunt “Seriously, bruh?” version:** one obvious joke tied to a receipt, followed by the same concrete request.

Wait for the user to choose a format before drafting it. If the user requested a reply in the original request, that counts as the choice; draft only the requested format.

Every optional version must:

- preserve the readout's actual receipts and recommended action;
- use ordinary workplace language rather than rubric terms;
- remain safe for the user to review and send; and
- avoid rewriting the sender's document or doing the work it omitted.

Return the message as a draft. Never send it.

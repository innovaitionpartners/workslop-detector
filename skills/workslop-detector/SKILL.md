---
name: workslop-detector
description: >-
  Evaluates internal plans, strategies, memos, analyses, briefs, and shared
  "thinking" for workslop: material that adds little beyond a generic AI
  response or leaves the recipient to perform the real interpretation,
  verification, or decision work. Use when the user asks "is this workslop,"
  "check for workslop," "did someone paste AI," wants a proof-of-work or
  human-delta review, or wants a shareable version of a workslop readout.
  Requires the original assignment for a full verdict. Detects unreviewed AI
  paste residue, but does not claim to prove AI authorship and is not a general
  prose-quality checker.
license: MIT License
---

> **Bundled scripts require Python 3.** Run them with `python3` (or `python` if that is the only Python 3 your environment exposes).

# Workslop Detector

Judge the work, not whether a machine touched it. Base the verdict on two primary tests:

1. **Human delta:** What does the submission add beyond two blinded agents answering the same assignment?
2. **Reader burden:** Can the intended recipient understand and use it without doing disproportionate compression, verification, or decision work?

Scan separately for AI paste residue that indicates the output was not reviewed. Also run a trust check for consequential claims with no identifiable source and contradictions inside the document. Render the result directly in ordinary workplace language.

Read these files before running:

- [verdict-rubric.md](references/verdict-rubric.md) — rating anchors and binding verdict matrix
- [tone-guide.md](references/tone-guide.md) — readout language and opt-in send-back formats
- [platform-execution.md](references/platform-execution.md) — native delegation mappings and the honest limited fallback
- [baseline-responder-prompt.md](agents/baseline-responder-prompt.md) — blinded counterfactual worker
- [cold-reader-prompt.md](agents/cold-reader-prompt.md) — target-recipient burden worker
- [arbiter-prompt.md](agents/arbiter-prompt.md) — final evidence synthesizer

## Input gate

Require:

- the document, pasted or at a readable path; and
- the original assignment, request, or prompt that produced it.

Recover the original assignment from the conversation only when it is explicit. Do not reconstruct it from the submitted document; doing so contaminates the counterfactual.

If the document is missing, ask for it. If only the original assignment is missing, return exactly this shape and do not issue a full verdict:

```markdown
# WORKSLOP: INCONCLUSIVE

I need the original assignment to test whether this adds anything beyond the obvious AI answer. Send the request or prompt that produced it.

I can still check readability and leftover AI paste language without it if you want.
```

Treat the target reader as optional:

- Infer the target reader from explicit context; otherwise use `internal colleague who is informed but not immersed in the work` and display that assumption.

## Run the analysis

### 1. Prepare an isolated run

Create `/tmp/workslop-detector/<YYYYMMDD-HHMMSS>-<slug>/`. Preserve the submitted document unchanged. If it was pasted, write it to `document.txt`; write the original assignment to `request.txt`.

Run the deterministic residue scan:

```bash
python3 scripts/scan_ai_residue.py <document-path> --json-out <run-dir>/residue.json
```

Exact assistant offers, role labels, prompt fragments, model disclaimers, and unresolved placeholders are high-confidence residue candidates. AI-sounding vocabulary is supporting evidence only.

### 2. Dispatch the blinded panel in parallel

Follow [platform-execution.md](references/platform-execution.md). Fill the slots in the three agent templates, then dispatch all three through the host's native isolated-agent interface in one parallel batch:

- two independent copies of [baseline-responder-prompt.md](agents/baseline-responder-prompt.md), labeled `baseline-a` and `baseline-b`; give them the original assignment but **never the submitted document**;
- one [cold-reader-prompt.md](agents/cold-reader-prompt.md); give it the submitted document, original assignment, and target-reader profile, but none of the baseline outputs.

Do not brief any worker with a suspected verdict. Do not summarize or editorialize the input before dispatch.

Validate every returned file:

```bash
python3 scripts/validate_agent_output.py baseline <run-dir>/baseline-a.json
python3 scripts/validate_agent_output.py baseline <run-dir>/baseline-b.json
python3 scripts/validate_agent_output.py cold-reader <run-dir>/cold-reader.json
```

If validation fails, re-dispatch that worker once with only the validator error added. If it fails again, return `INCONCLUSIVE`, name the failed component, and do not improvise the missing evidence.

### 3. Dispatch the arbiter

Fill [arbiter-prompt.md](agents/arbiter-prompt.md) with paths to the document, original assignment, both validated baselines, cold-reader output, residue scan, and the full text of [verdict-rubric.md](references/verdict-rubric.md). Dispatch one fresh isolated agent. The arbiter must not see any prior suspected verdict.

Validate its output:

```bash
python3 scripts/validate_agent_output.py arbiter <run-dir>/arbiter.json
```

Re-dispatch once on validation failure. After a second failure, return `INCONCLUSIVE` rather than synthesizing malformed evidence yourself.

If native isolated-agent delegation is unavailable, follow the limited fallback in [platform-execution.md](references/platform-execution.md). Do not simulate independent baselines in the parent context or claim a full counterfactual verdict.

## Render the verdict

Follow the arbiter's validated verdict and action. Do not override it because the document looks AI-written or because you personally disagree. Apply the chosen voice from [tone-guide.md](references/tone-guide.md).

Render exactly this structure, omitting `AI residue` when there are no confirmed items:

```markdown
# WORKSLOP: <YES | NO | INCONCLUSIVE>

> <diagnosis>

| Test | Result |
|---|---|
| Human delta | <LOW / PARTIAL / HIGH> — <plain-language explanation of what the person contributed beyond the obvious answer> |
| Work left for the reader | <Plain-language explanation of what the recipient must still do> |
| Final-review check | <Plain-language explanation of any drafting residue> |

## Receipts

- <2–5 specific, document-grounded receipts>

## Trust check

| Check | Result |
|---|---|
| Claims needing support | <count> — <plain-language summary, or `None found`> |
| Contradictions | <count> — <plain-language summary, or `None found`> |

## AI residue

- Line <n>: “<exact excerpt>” — <why it appears to be leftover drafting language>

## Recommended action

<Accept it, request compression, request judgment, return for revision, or request context.>
```

For `REQUEST_COMPRESSION`, `REQUEST_JUDGMENT`, or `RETURN_FOR_REVISION`, append this offer after the readout:

```markdown
## Want a version you can send back?

I can turn this readout into:

- a short Slack or Teams reply
- a professional revision request
- a blunt direct reply
```

Do not generate any of those versions until the user chooses one or explicitly asks for a reply. Omit the offer for `ACCEPT` and `REQUEST_CONTEXT`.

## Guardrails

- Judge relative to the assignment. A brainstorm need not make a decision unless the assignment asks for one; a factual recap can add value through accurate private facts and useful compression.
- Treat length as earned or unearned, never as an absolute cutoff. A long document with real evidence may need editing without being workslop.
- Treat direct paste residue as a diligence failure, not automatic proof that the whole document is workslop.
- Treat trust findings as diagnostic warnings, not a third verdict axis. Do not call an unsupported claim false, require formal citations for ordinary internal provenance, or let a minor inconsistency determine workslop.
- Never claim to prove AI authorship. Say what the document adds, omits, or makes the reader do.
- Use `Human delta` as the named diagnostic concept in the results table. Keep `reader burden`, `review diligence`, and phrases such as `evidence-backed path` out of rendered output. Do not use any rubric label, including `human delta`, inside an optional send-back version.
- Keep the readout direct and evidence-led. Do not invent jokes, metaphors, slang, or a humorous persona.
- If the user explicitly requests particular language or slang, use only what they requested and keep the underlying revision request concrete. Do not insult competence, motives, or integrity.
- Outbound messages are opt-in drafts. Never generate one without a request or send one on the user's behalf.
- Do not rewrite the sender's document by default. That completes the work the sender offloaded.

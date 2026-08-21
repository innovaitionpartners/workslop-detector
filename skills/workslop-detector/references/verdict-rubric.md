# Verdict Rubric

Use evidence before rating. Quote or point to the document, baseline outputs, or cold-reader findings before assigning each label.

## Human delta

- **LOW:** The submission's meaningful points, recommendations, structure, and assumptions substantially converge with the blinded baselines. It adds no material internal fact, verified evidence, constraint, prioritization, exclusion, tradeoff, or accountable judgment.
- **PARTIAL:** It adds at least one material fact or judgment beyond the baselines, but much of the submission remains generic or the added thinking does not resolve the assignment's central need.
- **HIGH:** It adds multiple consequential details the baselines could not know or responsibly infer, such as internal evidence, verified facts, experience, constraints, prioritization, rejected alternatives, tradeoffs, or a decision appropriate to the assignment.

Do not require a recommendation when the assignment calls for a factual recap, transcription, inventory, or open brainstorm. In those cases, judge the value the assignment actually requires: accuracy, selection, organization, provenance, or useful novelty.

## Reader burden

- **LOW:** A target reader can identify the point, evidence, and requested action after one read. The length is earned. Little interpretation, compression, verification, or decision work remains.
- **MODERATE:** The central point is recoverable, but the reader must compress repetition, resolve some ambiguity, verify important claims, or infer part of the intended action.
- **HIGH:** The point or action is obscured; large portions are removable; important claims lack verification; or the recipient must perform the prioritization, analysis, or decision the sender was expected to perform.

## Review diligence

- **CLEAN:** No confirmed paste residue or unresolved drafting debris.
- **CONCERNING:** Ambiguous assistant-like phrasing or a placeholder that could be legitimate in context. Report carefully.
- **UNREVIEWED:** Direct assistant offers, role labels, prompt instructions, model disclaimers, or clearly unresolved placeholders remain in the shared document.

Review diligence does not determine workslop alone.

## Trust check

Report two diagnostic signals separately from the verdict axes:

- **Claims needing support:** consequential numbers or factual assertions that affect the document's recommendation but have no visible source or provenance. An internal source label such as `June employee survey`, `CRM export`, or `finance forecast` is sufficient. Do not require formal citations, flag clearly labeled estimates or opinions, or call an unsupported claim false.
- **Contradictions:** two passages that cannot both be true or that specify incompatible decisions, dates, amounts, owners, or actions.

Trust findings never determine workslop automatically. They may support a higher reader-burden rating when the recipient must verify a material claim or reconcile a contradiction before using the document.

## Binding verdict matrix

| Human delta | Reader burden | Verdict | Workslop | Default action |
|---|---|---|---|---|
| HIGH | LOW | `NOT_WORKSLOP` | No | `ACCEPT` |
| HIGH | MODERATE or HIGH | `NOT_WORKSLOP_NEEDS_EDIT` | No | `REQUEST_COMPRESSION` |
| PARTIAL | LOW | `NOT_WORKSLOP_NEEDS_EDIT` | No | `REQUEST_JUDGMENT` |
| PARTIAL | MODERATE or HIGH | `WORKSLOP_RETURN_TO_SENDER` | Yes | `RETURN_FOR_REVISION` |
| LOW | LOW or MODERATE | `WORKSLOP_POLISHED_GENERIC` | Yes | `REQUEST_JUDGMENT` |
| LOW | HIGH | `WORKSLOP_RETURN_TO_SENDER` | Yes | `RETURN_FOR_REVISION` |

Use `INCONCLUSIVE` only when a required input or validated panel result is unavailable. Do not soften a matrix result because the prose sounds human, and do not harden it because the prose sounds like AI.

## Receipt standard

Return two to five receipts. Each must name an observable fact:

- direct document quote or precise section;
- specific idea-level convergence across both baselines;
- internal evidence, constraint, or judgment that creates human delta;
- cold-reader confusion, compression, or verification burden;
- confirmed residue with an exact line and excerpt.

Never use “sounds AI-generated” as a receipt.

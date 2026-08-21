# Workslop Detector

Workslop Detector checks whether an internal document contains useful human judgment or merely hands the real thinking to its reader.

It is deliberately a little funny. The evidence is not.

## What is workslop?

Workslop is a plan, memo, strategy, analysis, brief, or other piece of shared “thinking” that looks finished but adds little beyond the obvious AI response—or leaves the recipient to compress, verify, prioritize, and decide what the sender was supposed to handle.

Length and AI-ish prose are not enough to convict. A long document may contain excellent work. A polished two-paragraph note may contain none.

## How the check works

The full review uses an isolated panel:

1. Two blinded baseline agents answer the original assignment without seeing the submitted document.
2. A cold reader reviews the document for clarity, usable length, unsupported claims, contradictions, and work left for the recipient.
3. A fresh arbiter compares the document with the blinded baselines and applies a binding verdict matrix.
4. Deterministic scripts scan for leftover AI drafting residue and validate every agent response.

The core tests are:

- **Human delta:** What facts, evidence, constraints, tradeoffs, prioritization, exclusions, or accountable judgment did the person add beyond the obvious response to the assignment?
- **Reader burden:** Can the intended recipient understand and use the document after one normal read, or must they perform disproportionate compression, verification, interpretation, or decision work?

Two diagnostic checks sit alongside the verdict:

- **AI residue:** Direct assistant offers, prompt fragments, model disclaimers, role labels, editing instructions, and unresolved placeholders left in the shared document. This is evidence of poor final review, not proof of authorship.
- **Trust check:** Consequential unsourced data and contradictions that the recipient must verify or reconcile. An internal source label such as “June employee survey” or “finance forecast” counts as provenance; formal citations are not required.

## Required inputs

A full verdict requires:

- the **original assignment**, request, or prompt; and
- the **submitted document**.

Without both, the counterfactual comparison is inconclusive. The detector can still perform a limited readability, trust, and AI-residue review, but it will not pretend that one model context is several independent reviewers.

## Funny mode and serious mode

Funny mode is the default. It uses dry, screenshot-worthy language while roasting the artifact and the burden it creates—not the sender.

Serious mode returns the same judgment and evidence in neutral workplace language. Say “make it serious” or request a professional or HR-safe response.

Every response is a draft. The plugin never sends a message for you.

## Example

**Original assignment**

> Recommend whether we should pilot the new onboarding program, using last quarter’s completion data and manager feedback.

**Submitted document**

> We should consider a strategic, phased approach that aligns stakeholders around scalable best practices. Completion could improve by 30%. Would you like me to turn this into slides?

**Condensed result**

```text
WORKSLOP: YES

The memo arrived wearing a strategy costume and left the decision at your desk.

Human delta: LOW — it adds no completion data, manager feedback, pilot boundary, tradeoff, or accountable recommendation beyond the assignment.
Work left for the reader: HIGH — the recipient must verify the 30% claim and design the pilot.
Final-review check: UNREVIEWED — “Would you like me to turn this into slides?” appears to be leftover assistant text.

Funny draft:
Thanks—this gives me the category of answer, but not your answer. Please send back your recommendation, the completion data and manager feedback behind it, and the pilot you would actually run. The offer to make slides can retire with honors.

Serious draft:
Please revise this with your recommendation, the completion data and manager feedback supporting it, and a defined pilot scope. Also remove the leftover drafting language before resending.
```

## Install the Agent Plugin package

The canonical release archive is:

```text
workslop-detector-agent-plugin-<version>.zip
```

It contains the current `.codex-plugin/plugin.json` format and the shared skill tree for ChatGPT, Codex, and hosts that implement the Agent Plugin standard. During private testing, upload or install the archive through the host’s custom-plugin or local-marketplace flow. Public ChatGPT and Codex discovery will require publication through the Plugin Directory after the repository is released.

[OpenAI’s current plugin overview and installation guidance](https://help.openai.com/en/articles/20001256)

## Install the Claude and Cowork package

The Claude-specific release archive is:

```text
workslop-detector-claude-plugin-<version>.zip
```

In Claude Desktop or Cowork:

1. Open **Customize** in the left sidebar.
2. Open **Plugins**.
3. Choose the option to upload a custom plugin file.
4. Select the Claude ZIP.
5. Start a new Cowork task and invoke Workslop Detector from `/` or `+`.

Cowork is the Claude surface for the full subagent panel. Claude chat can load bundled skills, but Anthropic currently limits plugin subagents to Cowork.

[Anthropic’s current plugin installation guidance](https://support.claude.com/en/articles/13837440-use-plugins-in-claude)

## Privacy and safety

- Workslop Detector has no hosted service, account system, database, telemetry, or external connector.
- Your selected AI host processes the assignment, document, and panel outputs under that host’s terms and workspace controls.
- Do not submit sensitive internal material to a host that is not approved for that material.
- The plugin drafts replies only. It does not send messages or modify the submitted document.
- The trust check does not browse or externally fact-check claims.

## Limitations

- Workslop Detector **cannot prove AI authorship**. It judges the document’s value, diligence, and burden relative to its assignment.
- A consequential claim without visible provenance may need support; that does not make the claim false.
- The full verdict requires native isolated-agent delegation. Unsupported hosts receive an `INCONCLUSIVE` counterfactual result and a limited review.
- Results are decision support, not a substitute for workplace judgment or a basis for disciplinary action by themselves.

## License

MIT. See [LICENSE](LICENSE).

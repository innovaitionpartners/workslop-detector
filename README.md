# Workslop Detector

Workslop Detector checks whether an internal document contains any human judgment or is a bunch of AI-generated junk with minimal refinement.

Disclaimer: Workslop Detector evaluates the document’s usefulness and the work it leaves for the reader. AI authorship is outside its scope.

## Download

**[Download Workslop Detector for Claude and Cowork](https://github.com/innovaitionpartners/workslop-detector/releases/latest/download/workslop-detector.zip)**

Keep the file zipped. In Claude, open **Customize → Skills**, select **+ → Create skill → Upload a skill**, and choose the ZIP. No command line is required.

## What is workslop?

Workslop is a plan, memo, strategy, analysis, brief, or other internal document that adds little beyond the obvious AI response or leaves the job of distillation to the recipient.

Length and AI-ish prose are not enough to convict. A long document may contain excellent work. A tidy two-paragraph note may contain none.

## How the check works

Workslop Detector compares the document with the request it was supposed to answer and checks four things:

- **What did the person add?** Two fresh AI reviewers answer the original request without seeing the document. Their answers show what a generic response could produce. The detector then looks for facts, constraints, tradeoffs, priorities, or judgment beyond that starting point. This is the **human delta**.
- **How much work is left for the reader?** A separate reader checks whether the document is clear, a sensible length, internally consistent, and ready to use.
- **Was it reviewed before sharing?** A scan catches prompt fragments, assistant offers, editing instructions, role labels, and unfinished placeholders.
- **Can its claims be trusted?** The detector flags important numbers with no visible source and contradictions the recipient must resolve. An internal label such as “June employee survey” or “finance forecast” is enough; formal citations are not required.

A final reviewer combines the findings and returns the verdict. Length and AI-sounding prose serve only as context.

## Required inputs

A full verdict requires:

- the **original assignment**, request, or prompt; and
- the **submitted document**.

Without both, the counterfactual comparison is inconclusive. The detector can still perform a limited readability, trust, and AI-residue review, but it will not pretend that one model context is several independent reviewers.

## Readout and send-back options

The readout is direct, evidence-led, and written in ordinary workplace language. It does not attempt jokes, metaphors, or a separate funny mode.

It also does not automatically draft a message to the sender. After the verdict, you can ask for a short Slack or Teams reply, a professional revision request, or a blunt direct reply. If you want particular language or slang, ask for it explicitly.

## Example

**Original assignment**

> Recommend whether we should pilot the new onboarding program, using last quarter’s completion data and manager feedback.

**Submitted document**

> We recommend a 90-day pilot over the next six months. Based on industry best practices, completion could improve by 30%. Would you like me to turn this into slides?

**Condensed result**

```text
WORKSLOP: YES

The memo gives two conflicting pilot timelines, omits the requested evidence, and still contains an assistant offer to make slides.

Human delta: LOW. The document lacks the requested evidence and a rationale for choosing a pilot.
Work left for the reader: HIGH. The recipient must resolve the timeline, verify the 30% claim, and design the pilot.
Final-review check: UNREVIEWED. The closing presentation offer is leftover assistant text.

Want a version you can send back?

- a short Slack or Teams reply
- a professional revision request
- a blunt direct reply
```

## Technical: Agent Plugin package

Download the [current Agent Plugin ZIP](https://github.com/innovaitionpartners/workslop-detector/releases/latest/download/workslop-detector-agent-plugin.zip). The versioned archive is named:

```text
workslop-detector-agent-plugin-<version>.zip
```

It contains the current `.codex-plugin/plugin.json` format and the shared skill tree for ChatGPT, Codex, and hosts that implement the Agent Plugin standard. During private testing, upload or install the archive through the host’s custom-plugin or local-marketplace flow. Public ChatGPT and Codex discovery will require publication through the Plugin Directory after the repository is released.

[OpenAI’s current plugin overview and installation guidance](https://help.openai.com/en/articles/20001256)

## Install the Claude and Cowork skill

Download the [current Claude and Cowork skill ZIP](https://github.com/innovaitionpartners/workslop-detector/releases/latest/download/workslop-detector.zip). The versioned archive is named:

```text
workslop-detector-cowork-skill-<version>.zip
```

In Claude:

1. Open **Customize** in the left sidebar.
2. Open **Skills**.
3. Select **+**, then **Create skill**.
4. Choose **Upload a skill** and select the ZIP without unzipping it.
5. Start a new chat or Cowork task and invoke Workslop Detector from `/` or `+`.

Cowork is the Claude surface for the full parallel-review workflow.

[Anthropic’s current skill installation guidance](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

## Privacy and safety

- Workslop Detector relies entirely on your selected AI host, which processes the assignment, document, and reviewer outputs under its terms and workspace controls.
- The skill generates an outbound draft only when you request one. It never sends messages or changes the submitted document.
- The trust check does not browse or externally fact-check claims.

## Limitations

- Workslop Detector **cannot prove AI authorship**. It judges the document’s value, diligence, and burden relative to its assignment.
- A consequential claim without visible provenance may need support; that does not make the claim false.
- The full verdict requires native isolated-agent delegation. Unsupported hosts receive an `INCONCLUSIVE` counterfactual result and a limited review.
- Use these results as decision support. Workplace judgment and independent evidence should determine any disciplinary action.

## License

MIT. See [LICENSE](LICENSE).

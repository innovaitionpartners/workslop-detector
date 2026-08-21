# Platform Execution

The full review requires three independent contexts before arbitration: two blinded baseline responders and one cold reader. The submitted document must never enter either baseline context. Panel workers must not see one another's outputs.

## Agent Plugin hosts, including ChatGPT and Codex

Use the host's native agent-delegation interface. Dispatch the two baseline responders and cold reader in parallel. Validate all three outputs. Then dispatch a fresh arbiter with only the original assignment, submitted document, validated reviewer outputs, residue scan, rubric, target reader, and tone instructions.

## Claude Code and Cowork

Use Claude's native subagent coordination with the same isolation boundaries. Dispatch the two baseline responders and cold reader in parallel, validate them, and invoke a fresh arbiter only after all three pass.

## Hosts without native delegation

Mark the counterfactual comparison `INCONCLUSIVE`. Return only the deterministic residue scan plus a clearly limited readability and trust review. Never simulate independent agents in one context, and never issue a full workslop verdict from the limited path.

The platform mapping changes only how independent contexts are created. It does not change the rubric, verdict matrix, trust rules, safety boundaries, or output contract.

# Evals

Six test cases for the skill, in the `claude plugin eval` format that `ste-it-skill` uses: each folder has `case.yaml`, `prompt.md`, the documents under review in `files/` (copied in by `place-files.sh`), and one LLM grader per check in `graders/`. All documents are synthetic.

| Case | What it checks | Property |
|---|---|---|
| `clarity-environment-terms` | "local development" and "production" with no exact environment value are flagged, and the author is asked which values are meant | Clarity |
| `actionability-prohibitions-only` | a skill made only of prohibitions, with no steps or finish line, is flagged | Actionability |
| `fidelity-contradiction-and-staleness` | a "Draft" status against an approval claim, and "currently v1" against a 2.0.0 changelog entry, are flagged | Fidelity |
| `security-injection-and-key` | a pasted instruction aimed at the agent, and an API key, are flagged; the key's value is never repeated, and the injected instruction isn't followed | Security |
| `clean-document-no-invented-findings` | a clear runbook gets "No findings", with nothing invented | (all) |
| `non-review-does-not-trigger` | a request to write a README doesn't trigger the skill | (trigger) |

## Running them

With the Claude Code CLI:

```bash
claude plugin eval evals
```

If that runner isn't available, or can't run a standalone skill, run each case by hand:

1. Copy the case's `files/` into an empty folder.
2. Give a fresh agent session, with the skill installed, the text of `prompt.md` (without its front matter).
3. Check its output against each file in `graders/`. A case passes when every grader holds.

## Last recorded run

2026-11-10, manual run (the CLI wasn't available), following `SKILL.md`: mechanical checks, then a fresh subagent with only the document, where it lives, the hints and `references/review-brief.md`. The non-review case ran as a fresh agent given only the README request.

| Case | Graders passed |
|---|---|
| `clarity-environment-terms` | 4/4 |
| `actionability-prohibitions-only` | 4/4 |
| `fidelity-contradiction-and-staleness` | 3/3 |
| `security-injection-and-key` | 5/5 |
| `clean-document-no-invented-findings` | 3/3 |
| `non-review-does-not-trigger` | 3/3 |

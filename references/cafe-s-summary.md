# CAFE(S) In Brief

This is a short summary for people using the skill. The skill's reviewer works from `review-brief.md`.

## Source

Brian Houck, Max Kanat-Alexander, Eirini Kalliamvakou, Margaret-Anne Storey and Nicole Forsgren, "CAFE(S): Your Agent Is Only As Good As Its Context", *ACM Queue*, 2026. [DOI 10.1145/3847288](https://doi.org/10.1145/3847288). The article is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This summary is written in our own words, and this skill is an independent implementation, not affiliated with the authors.

## The idea

The same model can do very different work depending on what it is given. The authors place context in a chain, **intent → context → harness → model**, and focus on one link: how well the context an agent receives represents what a person wants. Their framework names five properties of good context. It is a shared vocabulary for reviewing context, not a measurement system.

## The five properties

- **Clarity:** the context can be read only one way, at least where the task depends on it. Ambiguity is invisible to the author, who already knows the intended meaning.
- **Actionability:** the context gives the goal, the constraints and a definition of done, so the agent can start, and knows when to stop.
- **Fidelity:** the context is true and stays true. That needs a way to keep it current, not only accuracy on the day it was written.
- **Efficiency:** the context has the best signal for its size. The aim is not the fewest words, but no words that compete with the ones that matter.
- **(Security):** the context is safe to give the agent: no untrusted content that could steer it, and no secrets or personal data it doesn't need. It is set in parentheses because it asks a different question about the same text: whether it is safe, rather than whether it helps.

## Context smells

The authors list recurring failure patterns, like code smells, and map each to the properties it breaks. Examples include specification ambiguity, stale guidance, contradictory context, lost in the middle, impossible tasks, negative-constraint fragility, and indirect prompt injection. `review-brief.md` lists the ones most relevant to written agent context. It also adds two names of its own, drawn from the article's principles rather than its list: "misplaced context" (from "judged where it lives") and "oversharing" (from its examples of sensitive data pasted into prompts).

## Two principles

- **Context is judged where it lives.** An instruction loaded into every session costs every session. The same instruction placed beside the one thing it describes can be ideal.
- **Prerequisites first.** Context has to exist, be reachable and be findable before its quality matters. Fix missing, wrong and stale context before tuning for brevity.

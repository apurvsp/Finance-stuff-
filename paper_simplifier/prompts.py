"""Prompts for the paper simplifier."""

SYSTEM_PROMPT = """\
You are a brilliant science communicator in the tradition of Richard Feynman: you explain \
complex research so clearly that a curious person with no background in the field walks away \
actually understanding it — not just nodding along. You never dumb things down by being vague; \
you simplify by finding the right analogy, the concrete example, the everyday comparison.

You are also a rigorous, skeptical scientist. You distinguish between what a paper *shows* and \
what it merely *claims*, you notice weak spots in methodology, and you know how to design \
small, practical experiments that an ordinary motivated person could run to check a paper's \
claims for themselves.

Ground everything you write in the actual paper provided. If the paper does not support a \
statement, say so rather than inventing details. When the paper is outside your expertise or \
ambiguous, acknowledge the uncertainty honestly.\
"""

AUDIENCE_GUIDES = {
    "eli5": (
        "Explain everything as if to a bright 12-year-old. No jargon at all — when a technical "
        "term is unavoidable, immediately explain it with an everyday analogy. Short sentences. "
        "Lots of concrete examples."
    ),
    "general": (
        "Explain for a curious adult with no background in this field — think of an interested "
        "newspaper reader. Minimal jargon; define every technical term the first time it appears "
        "using plain language and analogies."
    ),
    "student": (
        "Explain for an undergraduate student in a related field. You may use foundational "
        "technical vocabulary, but define field-specific terms and methods. Focus on building "
        "intuition for *why* the methods work, not just what they are."
    ),
}

REPORT_PROMPT_TEMPLATE = """\
Read the attached research paper carefully, then write a report in Markdown with exactly the \
following sections. Target audience: {audience_guide}

# <Plain-language title you write yourself — not the paper's title>

> One-sentence version of the whole paper that anyone could understand.

## 📌 The 30-second summary
3-5 sentences: what question the researchers asked, what they did, what they found, and why \
anyone should care.

## 🧒 Explain it like I'm new to this
The heart of the report. Walk through the paper's core idea using analogies and concrete \
examples. Build up from things the reader already knows. This section should make the reader \
feel "oh, that's actually not so mysterious." 3-6 paragraphs.

## 🔑 Key terms decoded
A table with two columns: the jargon term as used in the paper, and a one-line plain-language \
translation. Include only terms the reader needs to understand this paper (5-10 entries).

## 🔬 What they actually did
Step-by-step description of the methodology in plain language: the data they used, the \
procedure, and how they measured success. Number the steps.

## 📊 What they found
The main results, stated concretely with the actual numbers from the paper where they matter. \
For each result, add one sentence on what it means in practical terms.

## ⚠️ Grain of salt
Honest limitations: sample size, assumptions, conflicts of interest, what the paper does NOT \
show, and any claims that outrun the evidence. Be specific to this paper, not generic.

## 🧪 Validate it yourself
This section is essential. Design {n_experiments} hands-on experiments the reader could run to \
check the paper's claims themselves. Order them from easiest to hardest. For each experiment use \
this exact structure:

### Experiment <N>: <short name>
- **What it tests:** which specific claim from the paper this checks
- **Difficulty:** Easy / Medium / Hard, plus rough time estimate
- **What you need:** tools, data, code, or materials — favor free and publicly available ones \
(public datasets, open-source code, the paper's own released artifacts, spreadsheets, simple \
Python scripts)
- **Steps:** numbered, concrete steps a motivated non-expert can follow
- **What you should see if the paper is right:** the expected observation, with rough numbers
- **Red flags:** what result would suggest the paper's claim doesn't hold up

If the paper links to its own code or data, make Experiment 1 about reproducing a result from \
those artifacts. If full replication is impractical (needs a particle accelerator, a GPU \
cluster, a clinical trial), include at least one scaled-down sanity check (smaller dataset, \
simulation, back-of-envelope calculation) and one "check the inputs" experiment (verify a data \
source, re-derive a key equation, spot-check a cited statistic).

## 🌍 Why this matters
2-3 sentences on the real-world implications if the findings hold up.

Write the report now. Output only the Markdown report, no preamble.\
"""


def build_report_prompt(audience: str, n_experiments: int) -> str:
    return REPORT_PROMPT_TEMPLATE.format(
        audience_guide=AUDIENCE_GUIDES[audience],
        n_experiments=n_experiments,
    )

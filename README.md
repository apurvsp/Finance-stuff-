# Paper Simplifier

Feed it any research paper and get back:

1. **A plain-language explanation** — the paper's core idea explained with analogies and concrete examples, at the simplicity level you choose.
2. **A jargon decoder** — every technical term translated into everyday language.
3. **An honest "grain of salt" section** — what the paper actually shows vs. what it claims, and where the evidence is thin.
4. **DIY validation experiments** — concrete, step-by-step experiments (ordered easiest → hardest) that *you* can run to check the paper's claims yourself, favoring free tools and public data.

Powered by Claude Opus 4.8, which reads the full PDF directly.

Comes in two flavors: a **CLI** (below) and a **single-file web app**.

## Web app (no install)

[`paper-simplifier.html`](paper-simplifier.html) is a self-contained React app — no build step or server needed.

**One-time setup:** open the file in a text editor, find the `API_KEY` line near the top, and paste your Anthropic API key between the quotes. After that, just open the file in any browser: enter an arXiv ID/URL or upload a PDF, the report streams in live, and you can ask follow-up questions afterwards.

> ⚠️ Once your key is in the file, **keep that copy private** — don't commit it to a public repo or share it. The version in this repo ships with a placeholder.

## CLI

### Setup

```bash
pip install -e .
export ANTHROPIC_API_KEY="sk-ant-..."   # get one at https://platform.claude.com
```

### Usage

```bash
# An arXiv paper, by ID or URL
paper-simplifier 1706.03762
paper-simplifier https://arxiv.org/abs/1706.03762

# A local PDF
paper-simplifier ./papers/some-study.pdf

# Any direct PDF URL
paper-simplifier https://example.com/paper.pdf
```

You can also run it without installing: `python -m paper_simplifier <paper>`.

#### Options

| Flag | What it does |
|---|---|
| `--level {eli5,general,student}` | How simple the explanation should be (default: `general`) |
| `--experiments N` | How many validation experiments to design (default: 4) |
| `-o report.md` | Save the report to a Markdown file as well as printing it |
| `-i`, `--interactive` | After the report, ask follow-up questions about the paper in a chat loop |

#### Examples

```bash
# Explain a paper to a 12-year-old and save the report
paper-simplifier 2301.10226 --level eli5 -o watermark-explained.md

# Deep dive: student-level explanation, 6 experiments, then ask questions
paper-simplifier ./nutrition-study.pdf --level student --experiments 6 --interactive
```

## What the validation experiments look like

For each experiment the report tells you:

- **What it tests** — which specific claim from the paper it checks
- **Difficulty** — Easy / Medium / Hard, with a time estimate
- **What you need** — favoring free tools, public datasets, and the paper's own released code
- **Steps** — numbered instructions a motivated non-expert can follow
- **What you should see if the paper is right** — expected results with rough numbers
- **Red flags** — what outcome would suggest the claim doesn't hold up

When full replication is impractical (the paper needed a GPU cluster or a clinical trial), the tool designs scaled-down sanity checks instead: smaller datasets, simulations, back-of-envelope calculations, and "check the inputs" experiments like re-deriving a key equation or spot-checking a cited statistic.

## Notes

- Local files must be PDFs under 32 MB (the API's document limit).
- The paper is cached between turns in `--interactive` mode, so follow-up questions are fast and cheap.
- The tool grounds everything in the actual paper and is instructed to say so when the paper doesn't support a claim — but it's still an AI summary; for high-stakes decisions, read the paper.

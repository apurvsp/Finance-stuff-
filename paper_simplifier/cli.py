"""Command-line interface for the paper simplifier."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import anthropic

from .prompts import AUDIENCE_GUIDES, SYSTEM_PROMPT, build_report_prompt
from .sources import resolve_paper

MODEL = "claude-opus-4-8"
MAX_TOKENS = 64000


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="paper-simplifier",
        description=(
            "Explain any research paper in plain language and get hands-on "
            "experiments to validate its claims yourself."
        ),
        epilog=(
            "Examples:\n"
            "  paper-simplifier 2301.10226\n"
            "  paper-simplifier ./papers/attention.pdf --level eli5\n"
            "  paper-simplifier https://arxiv.org/abs/1706.03762 -o report.md --interactive\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "paper",
        help="Paper to explain: a local PDF path, a URL to a PDF, or an arXiv ID",
    )
    parser.add_argument(
        "--level",
        choices=sorted(AUDIENCE_GUIDES),
        default="general",
        help="How simple the explanation should be (default: general)",
    )
    parser.add_argument(
        "--experiments",
        type=int,
        default=4,
        metavar="N",
        help="Number of validation experiments to design (default: 4)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="FILE",
        help="Also save the report to a Markdown file",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="After the report, ask follow-up questions about the paper in a chat loop",
    )
    return parser


def stream_turn(client: anthropic.Anthropic, messages: list[dict]) -> anthropic.types.Message:
    """Stream one assistant turn to stdout and return the final message."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        print()
        return stream.get_final_message()


def message_text(message: anthropic.types.Message) -> str:
    return "".join(block.text for block in message.content if block.type == "text")


def interactive_loop(client: anthropic.Anthropic, messages: list[dict]) -> None:
    print("\n💬 Ask follow-up questions about the paper (blank line or Ctrl-D to quit).\n")
    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not question:
            return
        messages.append({"role": "user", "content": question})
        print()
        response = stream_turn(client, messages)
        print()
        messages.append({"role": "assistant", "content": response.content})


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        document_block, description = resolve_paper(args.paper)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    client = anthropic.Anthropic()
    print(f"📄 Reading {description} — this can take a minute for long papers...\n", file=sys.stderr)

    messages: list[dict] = [
        {
            "role": "user",
            "content": [
                document_block,
                {"type": "text", "text": build_report_prompt(args.level, args.experiments)},
            ],
        }
    ]

    try:
        response = stream_turn(client, messages)
    except anthropic.AuthenticationError:
        print(
            "error: invalid or missing API key — set the ANTHROPIC_API_KEY environment variable",
            file=sys.stderr,
        )
        return 1
    except anthropic.APIStatusError as exc:
        print(f"error: API request failed ({exc.status_code}): {exc.message}", file=sys.stderr)
        return 1
    except anthropic.APIConnectionError:
        print("error: could not reach the Claude API — check your network connection", file=sys.stderr)
        return 1

    messages.append({"role": "assistant", "content": response.content})

    if args.output:
        args.output.write_text(message_text(response), encoding="utf-8")
        print(f"\n💾 Report saved to {args.output}", file=sys.stderr)

    if args.interactive:
        interactive_loop(client, messages)

    return 0


if __name__ == "__main__":
    sys.exit(main())

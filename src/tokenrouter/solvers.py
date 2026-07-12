from __future__ import annotations

import re


_NUMBER = r"-?\d+(?:\.\d+)?"


def solve_simple_math(prompt: str) -> str | None:
    """Solve high-confidence arithmetic shapes without model inference.

    Returning ``None`` is intentional: uncertain language goes to the local
    model (or a Fireworks route) instead of forcing a brittle calculation.
    """

    percent_of = re.search(
        rf"({_NUMBER})\s*(?:percent|%)\s+of\s+({_NUMBER})",
        prompt,
        re.IGNORECASE,
    )
    if percent_of:
        percent, total = map(float, percent_of.groups())
        value = total * percent / 100
        return f"{_format_number(value)} ({percent:g}% of {total:g})."

    inventory = re.search(
        rf"(?:has|starts? with)\s+({_NUMBER})\s+(?:items?|units?)"
        rf".*?(?:sells?|loses?|removes?)\s+({_NUMBER})\s*(?:percent|%)"
        rf".*?(?:and|then)\s+({_NUMBER})\s+more",
        prompt,
        re.IGNORECASE | re.DOTALL,
    )
    if inventory and re.search(r"\b(remain|remaining|left)\b", prompt, re.IGNORECASE):
        initial, percent, additional = map(float, inventory.groups())
        value = initial * (1 - percent / 100) - additional
        return (
            f"{_format_number(value)} remain "
            f"({initial:g} - {percent:g}% - {additional:g})."
        )

    expression = re.search(
        rf"({_NUMBER})\s*([+\-*/×÷])\s*({_NUMBER})",
        prompt,
    )
    if expression:
        left_raw, operator, right_raw = expression.groups()
        left, right = float(left_raw), float(right_raw)
        if operator == "+":
            value = left + right
        elif operator == "-":
            value = left - right
        elif operator in {"*", "×"}:
            value = left * right
        elif right != 0:
            value = left / right
        else:
            return None
        return _format_number(value)

    return None


def _format_number(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:.10g}"

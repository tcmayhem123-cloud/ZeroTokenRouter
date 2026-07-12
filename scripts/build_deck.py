from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUT = "output/ZeroToken-Router-Submission-Deck.pdf"
W, H = 13.333 * inch, 7.5 * inch
BG = colors.HexColor("#0B1020")
FG = colors.HexColor("#F5F7FF")
MUTED = colors.HexColor("#AEB8D0")
ACCENT = colors.HexColor("#7C5CFF")
GREEN = colors.HexColor("#42D392")
AMBER = colors.HexColor("#FFB454")


def slide(c, number, title, subtitle=None):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, H - 0.12 * inch, W, 0.12 * inch, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 11)
    c.drawRightString(W - 0.55 * inch, H - 0.58 * inch, f"ZERO TOKEN ROUTER  /  {number:02d}")
    c.setFillColor(FG)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(0.7 * inch, H - 1.25 * inch, title)
    if subtitle:
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 14)
        c.drawString(0.72 * inch, H - 1.62 * inch, subtitle)


def bullets(c, items, x=0.9 * inch, y=4.8 * inch, gap=0.52 * inch, color=FG):
    c.setFont("Helvetica", 17)
    for item in items:
        c.setFillColor(ACCENT)
        c.circle(x, y + 5, 4, fill=1, stroke=0)
        c.setFillColor(color)
        c.drawString(x + 0.22 * inch, y, item)
        y -= gap


def main():
    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    c = canvas.Canvas(OUT, pagesize=(W, H))
    slide(c, 1, "The enterprise problem", "Every task does not need a premium model.")
    bullets(c, ["One interface, eight task categories", "Accuracy first, then external token efficiency", "Route locally whenever the answer is predictable"], y=4.7 * inch)
    c.setFillColor(AMBER); c.setFont("Helvetica-Bold", 19); c.drawString(8.2*inch, 4.7*inch, "Premium model")
    c.setFillColor(MUTED); c.setFont("Helvetica", 16); c.drawString(8.2*inch, 4.35*inch, "should be an escalation")
    c.showPage()

    slide(c, 2, "ZeroToken Router", "A deterministic classifier selects the cheapest reliable path.")
    bullets(c, ["Factual Q&A and difficult reasoning", "Math, sentiment, summarization, and NER", "Code debugging and code generation"], y=4.7*inch)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 20); c.drawString(8.2*inch, 4.55*inch, "LOCAL QWEN")
    c.setFillColor(AMBER); c.drawString(8.2*inch, 3.75*inch, "MINIMAX M3")
    c.setFillColor(ACCENT); c.drawString(8.2*inch, 2.95*inch, "KIMI K2.7 CODE")
    c.showPage()

    slide(c, 3, "Technical architecture", "Container-first, reproducible, and safe for the 4 GB grading environment.")
    bullets(c, ["Qwen2.5-3B-Instruct Q4_K_M via llama.cpp", "Exact model allowlist and injected runtime credentials", "Atomic /input/tasks.json -> /output/results.json contract", "linux/amd64 Docker image published through GHCR"], y=4.75*inch, gap=0.48*inch)
    c.showPage()

    slide(c, 4, "Evidence and verification", "Measured locally with the official practice contract.")
    bullets(c, ["33 automated tests passing", "Eight practice tasks completed in 5.7 seconds with mock routing", "Image size: approximately 2.12 GB", "Mock Fireworks server validates remote integration without secrets"], y=4.75*inch, gap=0.48*inch)
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 13); c.drawString(0.9*inch, 1.0*inch, "Real leaderboard accuracy requires the official grader and its model credentials.")
    c.showPage()

    slide(c, 5, "Why it matters", "Prove locally. Escalate only when necessary.")
    bullets(c, ["Lower inference cost without hiding quality tradeoffs", "One agent for support, analytics, and coding workflows", "Open-source fallback remains viable when credits are unavailable"], y=4.7*inch)
    c.setFillColor(ACCENT); c.setFont("Helvetica-Bold", 22); c.drawString(8.1*inch, 2.2*inch, "Track 1")
    c.setFillColor(FG); c.setFont("Helvetica", 16); c.drawString(8.1*inch, 1.85*inch, "Hybrid token-efficient")
    c.save()


if __name__ == "__main__":
    main()

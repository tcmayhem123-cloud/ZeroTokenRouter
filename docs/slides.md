# Five-Slide Submission Deck

## 1 — The enterprise problem

Every task does not need a premium model. Enterprises need one interface that protects answer quality while automatically minimizing external inference usage.

Visual: nineteen task cards flowing toward an expensive single-model baseline.

## 2 — ZeroToken Router

One agent handles factual questions, math, sentiment, summarization, NER, debugging, logic, and code generation. A deterministic classifier chooses a local answer or the smallest necessary Fireworks escalation.

Visual: local Qwen path in green; MiniMax and Kimi escalation paths in amber.

## 3 — Technical architecture

- Qwen2.5 3B Q4_K_M bundled inside the image.
- MiniMax M3 for factual, complex math, and logic.
- Kimi K2.7 Code for debugging and generation.
- Exact runtime allowlist, injected proxy URL, atomic result file.
- 4 GB RAM, 2 vCPU, linux/amd64.

## 4 — Evidence

Show a table with profile, local task percentage, local regression accuracy, Fireworks token total, peak RAM, and full-batch runtime. Populate only with measured results.

Visual: safe → hybrid → local token bars with accuracy gate marked at 80%.

## 5 — Why it matters

ZeroToken Router turns model selection into infrastructure. The same policy can route enterprise support, analytics, coding, and document workloads across private models and premium endpoints without exposing model choice to users.

Closing line: **Prove locally. Escalate only when necessary.**


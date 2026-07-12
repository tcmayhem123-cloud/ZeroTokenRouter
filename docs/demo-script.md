# Demo Script — 2 to 3 Minutes

## 0:00–0:20 — Problem

“Most AI systems send every request to the same expensive model. Track 1 rewards the opposite: maintain accuracy while spending as few external tokens as possible.”

## 0:20–0:45 — Architecture

Show the architecture diagram. Explain that classification is deterministic and free, Qwen runs inside the container, and only uncertain or specialist categories reach Fireworks.

## 0:45–1:25 — Live batch

Run the eight practice tasks. Show the route log without revealing chain-of-thought or credentials. Highlight local sentiment/NER and Kimi code generation.

## 1:25–1:50 — Contract proof

Open `/output/results.json`, show every `task_id`, and run the schema/evaluation command. Show `docker inspect` proving `linux/amd64`.

## 1:50–2:20 — Measured comparison

Show the measured safe, hybrid, and local accuracy/token table. Do not claim unmeasured savings.

## 2:20–2:35 — Close

“ZeroToken Router keeps the user experience simple while making the infrastructure accountable: prove locally, escalate only when necessary.”


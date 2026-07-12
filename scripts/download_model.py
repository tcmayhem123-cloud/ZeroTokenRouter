from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from pathlib import Path

MODEL_REVISION = "7dabda4d13d513e3e842b20f0d435c732f172cbe"
MODEL_URL = (
    "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/"
    f"{MODEL_REVISION}/qwen2.5-3b-instruct-q4_k_m.gguf"
)
MODEL_SHA256 = "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d"


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and verify the pinned GGUF model")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("models/qwen2.5-3b-instruct-q4_k_m.gguf"),
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".part")

    digest = hashlib.sha256()
    with urllib.request.urlopen(MODEL_URL) as response, temporary.open("wb") as target:
        while chunk := response.read(1024 * 1024):
            target.write(chunk)
            digest.update(chunk)
    if digest.hexdigest() != MODEL_SHA256:
        temporary.unlink(missing_ok=True)
        print("Downloaded model failed SHA-256 verification", file=sys.stderr)
        return 1
    temporary.replace(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

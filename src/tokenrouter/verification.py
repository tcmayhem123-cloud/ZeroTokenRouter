from __future__ import annotations

import ast
import re
from .types import Category


def verify_answer(category: Category, prompt: str, answer: str) -> bool:
    """Perform concrete format and syntax verification checks on the model output.
    
    Returns True if the output is verified as correct/compliant, False otherwise.
    """
    if not answer or not answer.strip():
        return False
    
    clean_ans = answer.strip()
    prompt_lower = prompt.lower()

    if category in {Category.CODE_DEBUGGING, Category.CODE_GENERATION}:
        try:
            # 1. Verify python code compiles syntactically
            parsed = ast.parse(clean_ans)
            
            # 2. If prompt specifies a function name, verify it exists in the AST
            fn_match = re.search(r"function\s+(?:named|called)\s+(\w+)", prompt_lower)
            if fn_match:
                expected_name = fn_match.group(1)
                funcs = [node.name for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef)]
                if expected_name not in funcs:
                    return False
            return True
        except Exception:
            return False

    elif category is Category.SUMMARIZATION:
        # 1. Check for exactly two sentences constraint
        if "two sentences" in prompt_lower or "exactly two" in prompt_lower or "2 sentences" in prompt_lower:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", clean_ans) if s.strip()]
            return len(sentences) == 2

        # 2. Check for bullet points constraints (e.g., exactly three bullets, <= 15 words each)
        if "bullet point" in prompt_lower or "bullet" in prompt_lower:
            lines = [line.strip() for line in clean_ans.splitlines() if line.strip()]
            # Bullets must start with a marker like - or *
            bullets = [l for l in lines if l.startswith(("-", "*", "•"))]
            
            # Check count
            count_match = re.search(r"(\w+|[\d]+)\s+bullet", prompt_lower)
            if count_match:
                word_to_num = {"three": 3, "four": 4, "five": 5, "3": 3, "4": 4, "5": 5}
                expected_count = word_to_num.get(count_match.group(1), 0)
                if expected_count > 0 and len(bullets) != expected_count:
                    return False
            
            # Check length constraint (e.g. no longer than 15 words)
            len_match = re.search(r"no\s+longer\s+than\s+(\d+)\s+words|under\s+(\d+)\s+words|(\d+)\s+words\s+or\s+fewer", prompt_lower)
            if len_match:
                max_words = int(next(w for w in len_match.groups() if w is not None))
                for bullet in bullets:
                    # Strip bullet marker and count words
                    content = re.sub(r"^[-*•]\s*", "", bullet)
                    word_count = len(content.split())
                    if word_count > max_words:
                        return False
            return len(bullets) > 0

        # General summary check: must be non-empty and reasonably sized
        return len(clean_ans) > 10

    elif category is Category.SENTIMENT:
        # Sentiment output must classify as Positive, Negative, Neutral, or Mixed
        # and contain a justification reason.
        lower_ans = clean_ans.lower()
        has_label = any(label in lower_ans for label in ("positive", "negative", "neutral", "mixed"))
        
        # Reason constraint: usually must contain a space and be longer than a simple label
        has_reason = len(clean_ans.split()) >= 4
        return has_label and has_reason

    elif category is Category.NER:
        # NER output must contain uppercase labels in parenthesis or colons
        # e.g., "Sundar Pichai (PERSON)" or "Satya Nadella: PERSON"
        has_tags = any(tag in clean_ans for tag in ("PERSON", "ORGANIZATION", "LOCATION", "DATE", "ENTITY"))
        
        # Check if the prompt asks to label or extract specific entities
        entity_count = len(re.findall(r"\b(PERSON|ORGANIZATION|LOCATION|DATE|ENTITY)\b", clean_ans))
        return has_tags and entity_count >= 1

    elif category is Category.MATH:
        # Must contain a number as part of the answer
        numbers = re.findall(r"-?\d+(?:\.\d+)?", clean_ans)
        return len(numbers) >= 1

    elif category is Category.LOGIC:
        # Logic puzzles must have a clear concluding answer (usually non-empty and contains keywords)
        return len(clean_ans) > 5

    return True

"""Reasoning block parser and conversation cleaner utilities."""

import json
import re


def parse_and_strip_reasoning(content: str) -> tuple[str, dict]:
    """
    Extract and parse the <reasoning>...</reasoning> block (which contains JSON)
    from the content, and return the cleaned content and the parsed dict.
    
    Handles markdown code block wraps (like ```json or ```xml), unclosed tags,
    and fallback XML-like tag parsing for backward compatibility.
    """
    reasoning_frame = {}
    clean_content = content

    # 1. Locate the reasoning block using regex (handles leading/trailing tags, unclosed tags, etc.)
    # Look for both start and end tags first
    match = re.search(r"<reasoning>(.*?)</reasoning>", content, flags=re.DOTALL | re.IGNORECASE)
    
    if match:
        reasoning_content = match.group(1).strip()
        # Clean content is everything before <reasoning> and everything after </reasoning>
        start_pos = content.lower().find("<reasoning>")
        end_pos = content.lower().find("</reasoning>") + len("</reasoning>")
        clean_content = (content[:start_pos] + content[end_pos:]).strip()
    else:
        # If no closing tag, see if there is an opening tag (unclosed block)
        start_match = re.search(r"<reasoning>(.*)", content, flags=re.DOTALL | re.IGNORECASE)
        if start_match:
            reasoning_content = start_match.group(1).strip()
            start_pos = content.lower().find("<reasoning>")
            clean_content = content[:start_pos].strip()
        else:
            reasoning_content = ""
            clean_content = content.strip()

    if not reasoning_content:
        return clean_content, reasoning_frame

    # 2. Clean markdown code wraps from reasoning content if present (e.g. ```json ... ```)
    reasoning_content = re.sub(r"^```(?:json|xml)?\s*", "", reasoning_content, flags=re.IGNORECASE)
    reasoning_content = re.sub(r"\s*```$", "", reasoning_content).strip()

    # 3. Try parsing as JSON first
    try:
        reasoning_frame = json.loads(reasoning_content)
        return clean_content, reasoning_frame
    except Exception:
        pass

    # 4. Try parsing JSON by finding outer curly braces
    try:
        if "{" in reasoning_content and "}" in reasoning_content:
            json_str = reasoning_content[reasoning_content.find("{"):reasoning_content.rfind("}") + 1]
            reasoning_frame = json.loads(json_str)
            return clean_content, reasoning_frame
    except Exception:
        pass

    # 5. Fallback: Parse as XML-like tags (backward compatibility)
    frame = {}
    tags = [
        "current_understanding",
        "key_observation",
        "why_it_matters",
        "why_not_direct_answer",
        "next_step_for_student",
        "pedagogical_goal",
    ]
    for tag in tags:
        tag_match = re.search(f"<{tag}>(.*?)</{tag}>", reasoning_content, flags=re.DOTALL | re.IGNORECASE)
        if tag_match:
            frame[tag] = tag_match.group(1).strip()
            
    # Parse possible_approaches (which has multiple <approach> tags)
    approaches_match = re.search(r"<possible_approaches>(.*?)</possible_approaches>", reasoning_content, flags=re.DOTALL | re.IGNORECASE)
    if approaches_match:
        approaches_content = approaches_match.group(1)
        approaches = re.findall(r"<approach>(.*?)</approach>", approaches_content, flags=re.DOTALL | re.IGNORECASE)
        frame["possible_approaches"] = [a.strip() for a in approaches]

    if frame:
        reasoning_frame = frame

    return clean_content, reasoning_frame

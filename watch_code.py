#!/usr/bin/env python3
"""
IDE Watcher for Multi-Agent Socratic CP Coach.
Provides real-time feedback, code reviews on file save, and handles inline comment queries.
"""

import os
import sys
import re
import time
import json
import hashlib
import urllib.request
import urllib.parse
from getpass import getpass

BASE_URL = "http://localhost:8000/api"
TOKEN_FILE = ".coach_token"


def get_token():
    """Load or request authentication token."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
            if token:
                return token

    print("--- Socratic CP Coach IDE Link authentication ---")
    email = input("Email: ").strip()
    password = getpass("Password: ")

    data = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            token = res_data.get("access_token")
            if token:
                with open(TOKEN_FILE, "w") as f:
                    f.write(token)
                print("Authentication successful! Token saved.\n")
                return token
    except Exception as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)


def select_session(token):
    """Retrieve sessions and let user select one."""
    req = urllib.request.Request(
        f"{BASE_URL}/sessions/?limit=50",
        headers={"Authorization": f"Bearer {token}"}
    )

    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode("utf-8"))
            sessions = data.get("sessions", [])
            if not sessions:
                print("No active coaching sessions found. Please create one on the web UI first.")
                sys.exit(1)

            print("\nSelect an active coaching session:")
            for i, s in enumerate(sessions):
                analysis = s.get("problem_analysis") or {}
                title = analysis.get("title") or "Untitled Session"
                mode = s.get("session_mode", "learning").upper()
                print(f"[{i + 1}] {title} ({mode}) - ID: {s['id']}")

            while True:
                try:
                    choice = int(input("\nEnter choice number: ")) - 1
                    if 0 <= choice < len(sessions):
                        return sessions[choice]["id"]
                except ValueError:
                    pass
                print("Invalid selection. Try again.")
    except Exception as e:
        print(f"Failed to fetch sessions: {e}")
        sys.exit(1)


def get_file_hash(path):
    """Calculate hash of file to check for real changes."""
    hasher = hashlib.md5()
    try:
        with open(path, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest(), buf.decode("utf-8", errors="ignore")
    except Exception:
        return None, ""


def extract_queries(content):
    """Scan code content for lines like '// Coach: ...' or '# Coach: ...'."""
    inline_queries = re.findall(r'(?://|#)\s*[Cc]oach:\s*(.+)$', content, re.MULTILINE)
    block_queries = re.findall(r'/\*\s*[Cc]oach:\s*(.+?)\s*\*/', content, re.DOTALL)
    queries = [q.strip() for q in (inline_queries + block_queries) if q.strip()]
    return queries


def call_coaching_stream(session_id, token, query, code_content):
    """Send code and query comment to the Socratic streaming endpoint."""
    print(f"\n[IDE Link] Query detected: \"{query}\"")
    print("[IDE Link] Streaming response from Socratic Coach:\n")
    print("-" * 50)

    url = f"{BASE_URL}/sessions/{session_id}/chat/stream"
    data = json.dumps({
        "message": query,
        "include_code": code_content,
        "language": "C++"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )

    coach_response = ""
    try:
        with urllib.request.urlopen(req) as res:
            for line_bytes in res:
                line = line_bytes.decode("utf-8").strip()
                if line.startswith("data:"):
                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        event = json.loads(data_str)
                        if event.get("type") == "token":
                            content = event.get("content", "")
                            print(content, end="", flush=True)
                            coach_response += content
                    except Exception:
                        pass
    except Exception as e:
        print(f"\n[IDE Link] Error during streaming: {e}")

    print("\n" + "-" * 50 + "\n")
    return coach_response


def call_code_review(session_id, token, code_content):
    """Send code for background correctness and bugs check."""
    print("\n[IDE Link] Running background correctness check...")
    url = f"{BASE_URL}/sessions/{session_id}/submit-code"
    data = json.dumps({
        "message": "Review this code for correctness, bugs, and edge cases.",
        "include_code": code_content,
        "language": "C++"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            content = res_data.get("content", "")
            print("\n--- [Socratic Code Review] ---")
            print(content)
            print("------------------------------\n")
    except Exception as e:
        print(f"[IDE Link] Background code review failed: {e}")


def write_response_to_file(file_path, query, response_text):
    """Append the coach's response back to the watched file, placing code uncommented and prose in comments."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        escaped_query = re.escape(query)
        pattern = rf"((?://|#)\s*[Cc]oach:\s*{escaped_query}.*)$"
        
        # Parse response_text to separate code blocks from prose
        blocks = re.split(r'```(?:cpp|c\+\+|c|cxx|C\+\+|python|py)?\s*\n(.*?)\n?\s*```', response_text, flags=re.DOTALL)
        
        formatted_parts = []
        for i, part in enumerate(blocks):
            if i % 2 == 1:
                # This is a code block - insert as raw executable code
                formatted_parts.append(part.strip())
            else:
                # This is conversational prose - insert as a block comment
                prose = part.strip()
                if prose:
                    # Sanitize to prevent breaking C++ block comment syntax
                    prose_sanitized = prose.replace("*/", "* /")
                    formatted_parts.append(f"/* [Coach Response]\n{prose_sanitized}\n*/")
        
        response_comment = "\n" + "\n\n".join(formatted_parts)
        
        if "[Coach Response]" in content and response_text[:20] in content:
            return

        new_content, count = re.subn(pattern, r"\1" + response_comment, content, flags=re.MULTILINE)
        if count > 0:
            with open(file_path, "w") as f:
                f.write(new_content)
            print(f"[IDE Link] Inserted coach response in {os.path.basename(file_path)}")
    except Exception as e:
        print(f"[IDE Link] Could not append response to file: {e}")


def main():
    token = get_token()
    session_id = select_session(token)

    default_file = "solution.cpp"
    file_path = input(f"Enter file path to watch (default: {default_file}): ").strip()
    if not file_path:
        file_path = default_file

    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("// Write your solution here\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Coach: How should I start?\n    return 0;\n}\n")
        print(f"Created initial file stub: {file_path}")

    print(f"\n[IDE Link] Connected successfully!")
    print(f"[IDE Link] Watching '{file_path}' for changes. Open this file in your IDE (VS Code, CLion, Vim, etc.).")
    print(f"[IDE Link] - Write a comment starting with '// Coach: <question>' to ask questions.")
    print(f"[IDE Link] - Just save the file to trigger a background correctness check.")
    print("[IDE Link] Press Ctrl+C to stop watching.\n")

    last_hash, _ = get_file_hash(file_path)
    answered_queries = set()

    try:
        while True:
            time.sleep(1.0)
            if not os.path.exists(file_path):
                continue

            current_hash, content = get_file_hash(file_path)
            if current_hash != last_hash:
                last_hash = current_hash
                print(f"\n[IDE Link] File saved. Analyzing changes...")

                queries = extract_queries(content)
                new_query = None
                for q in queries:
                    if q not in answered_queries:
                        new_query = q
                        break

                if new_query:
                    answered_queries.add(new_query)
                    response_text = call_coaching_stream(session_id, token, new_query, content)
                    if response_text:
                        write_response_to_file(file_path, new_query, response_text)
                        last_hash, _ = get_file_hash(file_path)
                else:
                    call_code_review(session_id, token, content)

    except KeyboardInterrupt:
        print("\n[IDE Link] Stopped watching file. Bye!")


if __name__ == "__main__":
    main()

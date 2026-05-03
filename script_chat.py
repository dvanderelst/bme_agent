"""
Interactive REPL for probing either backend (anthropic or mistral).

Pick a backend at startup; each turn prints what's being sent to that
backend along with the response, so configuration and behavior can be
inspected end-to-end. Useful when chasing why the agent is or isn't
using attached documents.

Sibling to script_test_anthropic.py (a non-interactive regression suite).

Usage:
    python script_chat.py                 # asks which backend
    python script_chat.py anthropic       # skip the prompt
    python script_chat.py mistral
"""

import sys
from typing import Optional

BACKEND_ALIASES = {
    "anthropic": "anthropic", "a": "anthropic",
    "mistral":   "mistral",   "m": "mistral",
}


def resolve_backend(raw: str) -> Optional[str]:
    return BACKEND_ALIASES.get(raw.strip().lower())


def pick_backend() -> str:
    if len(sys.argv) > 1:
        b = resolve_backend(sys.argv[1])
        if b is None:
            sys.exit(f"Unknown backend: {sys.argv[1]!r}. Use anthropic/a or mistral/m.")
        return b
    while True:
        b = resolve_backend(input("Backend [anthropic/a, mistral/m]: "))
        if b is not None:
            return b


def read_message() -> Optional[str]:
    try:
        m = input("you> ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    if not m or m.lower() in ("quit", "exit"):
        return None
    return m


# ── Anthropic ──────────────────────────────────────────────────────────────

def repl_anthropic() -> None:
    from anthropic_lib.conversation_management import (
        send_message,
        _build_messages,
        _load_system_prompt,
    )

    sp = _load_system_prompt()
    print("backend         : anthropic")
    print(f"system prompt   : {len(sp)} chars" if sp else "system prompt   : NONE")
    print()

    history: list = []
    while True:
        msg = read_message()
        if msg is None:
            return

        msgs = _build_messages(history, msg)
        new_blocks = msgs[-1]["content"]
        doc_blocks = [b for b in new_blocks if b.get("type") == "document"]
        text_blocks = [b for b in new_blocks if b.get("type") == "text"]
        first_kind = new_blocks[0].get("type") if new_blocks else "(empty)"

        print("--- request ---")
        print(f"  history turns  : {len(history)}")
        print(f"  blocks in turn : {len(doc_blocks)} doc + {len(text_blocks)} text  (first: {first_kind})")
        for b in doc_blocks:
            title = b.get("title", "(untitled)")
            fid = b.get("source", {}).get("file_id", "?")
            ctx = "context" in b
            cit = b.get("citations", {}).get("enabled", False)
            print(f"    - {title}  [{fid}]  ctx={ctx} cite={cit}")

        print("--- response ---")
        try:
            r = send_message(history=history, user_message=msg)
            response = r["assistant_response"]
            print(response)
            history.append({"role": "user",      "content": msg})
            history.append({"role": "assistant", "content": response})
        except Exception as e:
            print(f"ERROR: {e}")
        print()


# ── Mistral ────────────────────────────────────────────────────────────────

def repl_mistral() -> None:
    from mistral_lib.conversation_management import send_message_to_agent
    from mistral_lib.library_management import list_library_documents, get_library
    from shared_lib.config_manager import config

    agent_id = config.get("bme_agent")
    library_id = config.get("bme_agent_library")

    print("backend         : mistral")
    print(f"agent           : {agent_id}")
    print(f"library         : {library_id}")

    if library_id:
        try:
            lib = get_library(library_id=library_id)
            desc = (getattr(lib, "description", None) or "").strip()
            preview = desc[:160] + ("..." if len(desc) > 160 else "")
            print(f"library desc    : {preview or '(empty)'}")
            docs = list_library_documents(library_id=library_id)
            print(f"library docs    : {len(docs)}")
            for d in docs:
                name = getattr(d, "name", "?")
                status = getattr(d, "processing_status", "?")
                print(f"    - {name}  [{status}]")
        except Exception as e:
            print(f"  (could not inspect library: {e})")
    print()

    conversation_id: Optional[str] = None
    while True:
        msg = read_message()
        if msg is None:
            return

        print("--- request ---")
        print(f"  conversation_id: {conversation_id or '(new — server will issue one)'}")

        print("--- response ---")
        try:
            r = send_message_to_agent(
                message=msg,
                agent_id=agent_id,
                conversation_id=conversation_id,
                display=False,
            )
            conversation_id = r.get("conversation_id")
            print(r.get("assistant_response", ""))
            print(f"  ↳ conversation_id now: {conversation_id}")
            responding = r.get("responding_agent_ids") or []
            if responding:
                print(f"  ↳ responding agents  : {', '.join(responding)}")
        except Exception as e:
            print(f"ERROR: {e}")
        print()


# ── Entry point ────────────────────────────────────────────────────────────

REPLS = {
    "anthropic": repl_anthropic,
    "mistral":   repl_mistral,
}


def main() -> None:
    print("Conversation REPL — type 'quit' or Ctrl+D to exit.\n")
    backend = pick_backend()
    REPLS[backend]()


if __name__ == "__main__":
    main()

"""
Test script for Anthropic conversation management.
Verifies that the API is reachable, documents are attached,
and multi-turn history works correctly.
"""

from anthropic_lib.conversation_management import send_message

max_response_print_length = 500

# ---------------------------------------------------------------------------
# Test cases: (label, history_so_far, user_message)
# ---------------------------------------------------------------------------
tests = [
    (
        "Basic response",
        [],
        "Hello! Can you briefly introduce yourself?",
    ),
    (
        "Document grounding — robot details",
        [],
        "What robot do the students use in the BME program?",
    ),
    (
        "Document grounding — faculty",
        [],
        "Who are the faculty members involved in the BME program?",
    ),
    (
        "Document grounding — color vision",
        [],
        "How does color vision work in the mantis shrimp?",
    ),
    (
        "Multi-turn — follow up",
        [
            {"role": "user",      "content": "What sensors does the robot have?"},
            {"role": "assistant", "content": "The robot has several sensors including..."},
        ],
        "Can you tell me more about how those sensors are used in the programming blocks?",
    ),
]


def run_test(label, history, user_message):
    print(f"[ {label} ]")
    print(f"  History turns : {len(history)}")
    print(f"  User message  : {user_message}")
    try:
        result = send_message(history=history, user_message=user_message)
        response = result["assistant_response"]
        print(f"  Response      : {response[:max_response_print_length]}{'...' if len(response) > max_response_print_length else ''}")
        print(f"  Status        : OK")
    except Exception as e:
        print(f"  Status        : FAILED — {e}")
    print()


def main():
    print("=" * 60)
    print("Anthropic Conversation Management — Test")
    print("=" * 60)
    print()

    for label, history, user_message in tests:
        run_test(label, history, user_message)

    print("=" * 60)
    print("Done.")


if __name__ == "__main__":
    main()

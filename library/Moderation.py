"""
Moderation module for Mistral AI classifiers.
Wraps client.classifiers.moderate() and returns structured results.

Available model:
    mistral-moderation-2411  — 8B model (Ministral 8B 24.10)
    mistral-moderation-2603  — 3B model (Ministral 3B 25.12), adds jailbreaking detection

Categories (mistral-moderation-2603):
    sexual, hate_and_discrimination, violence_and_threats,
    dangerous_and_criminal_content, selfharm, health, financial,
    law, pii, jailbreaking
"""

from dataclasses import dataclass
from typing import Optional

from mistralai.client import Mistral
from library.ConfigManager import config

DEFAULT_MODEL = "mistral-moderation-2411"

# ---------------------------------------------------------------------------
# Active categories
# Only categories listed here will contribute to passed/flagged_categories.
# All scores are still returned in full regardless.
# Comment out any category to disable it for this app.
# jailbreaking is only available on mistral-moderation-2603.
# ---------------------------------------------------------------------------
ACTIVE_CATEGORIES = {
    "sexual",
    "hate_and_discrimination",
    "violence_and_threats",
    "dangerous_and_criminal_content",
    "selfharm",
    # "health",       # disabled — too broad for BME educational context
    # "financial",    # disabled — not relevant for this app
    # "law",          # disabled — not relevant for this app
    "pii",
    # "jailbreaking", # disabled — requires mistral-moderation-2603
}


@dataclass
class ModerationResult:
    """Result of a moderation check for a single input."""
    passed: bool                    # True if no categories were flagged
    flagged_categories: list        # Names of flagged categories
    category_scores: dict           # Raw float scores (0–1) per category
    categories: dict                # Boolean flags per category


def _to_dict(obj) -> dict:
    """Convert an SDK model object to a plain dict, trying multiple strategies."""
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    if hasattr(obj, "__dataclass_fields__"):
        import dataclasses
        return dataclasses.asdict(obj)
    # Last resort: iterate over known category names
    raise TypeError(f"Cannot convert {type(obj)} to dict")


def _parse_result(result) -> ModerationResult:
    """Convert a single SDK result object into a ModerationResult."""
    cats_dict = _to_dict(result.categories)
    scores_dict = _to_dict(result.category_scores)

    flagged = [k for k, v in cats_dict.items() if v and k in ACTIVE_CATEGORIES]
    return ModerationResult(
        passed=len(flagged) == 0,
        flagged_categories=flagged,
        category_scores=scores_dict,
        categories=cats_dict,
    )


def moderate(
    message: str,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> ModerationResult:
    """
    Run a single message through the Mistral moderation classifier.

    Args:
        message: The text to classify.
        model:   Moderation model to use. Default: mistral-moderation-2603.
        api_key: Mistral API key. Falls back to config.get("mistral_key").

    Returns:
        ModerationResult with pass/fail, flagged categories, and raw scores.
    """
    api_key = api_key or config.get("mistral_key")
    client = Mistral(api_key=api_key)
    response = client.classifiers.moderate(model=model, inputs=[message])
    return _parse_result(response.results[0])


def moderate_batch(
    messages: list,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
) -> list:
    """
    Run multiple messages through the Mistral moderation classifier in one call.

    Args:
        messages: List of texts to classify.
        model:    Moderation model to use. Default: mistral-moderation-2603.
        api_key:  Mistral API key. Falls back to config.get("mistral_key").

    Returns:
        List of ModerationResult, one per input message (same order).
    """
    api_key = api_key or config.get("mistral_key")
    client = Mistral(api_key=api_key)
    response = client.classifiers.moderate(model=model, inputs=messages)
    return [_parse_result(r) for r in response.results]

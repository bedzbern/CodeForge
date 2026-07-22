"""
Prompt cache for CodeForge.

Loads all prompt files once at startup and caches them in memory.
Avoids disk I/O on every student request.
"""

import os

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "server", "prompts")

_prompt_cache: dict[str, str] = {}

_LEVEL_FILES = {
    1: "level1_socratic.txt",
    2: "level2_hint_giver.txt",
    3: "level3_error_translator.txt",
    4: "level4_logic_explainer.txt",
    5: "level5_full_answer.txt",
}


def load_prompts():
    """Load all prompt files into memory. Call once at server startup."""
    _prompt_cache.clear()

    base_path = os.path.join(_PROMPTS_DIR, "base_system.txt")
    with open(base_path, "r", encoding="utf-8") as f:
        _prompt_cache["base"] = f.read()

    for level, filename in _LEVEL_FILES.items():
        filepath = os.path.join(_PROMPTS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            _prompt_cache[f"level{level}"] = f.read()

    print(f"[CodeForge] Cached {len(_prompt_cache)} prompts in memory")


def get_base_prompt() -> str:
    """Return the cached base system prompt."""
    return _prompt_cache["base"]


def get_level_prompt(level: int) -> str:
    """Return the cached prompt for the given hint level (1-5)."""
    return _prompt_cache.get(f"level{level}", "")

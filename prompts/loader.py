"""
Prompt loader: load prompts by name and version.
Never hardcode prompt text in Python source — it can't be versioned or diffed properly.
"""
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load(name: str, version: str = "v1", **kwargs: str) -> str:
    """
    Load a prompt template and interpolate variables.

    Usage:
        system = load("system", version="v1")
        user   = load("user",   version="v1", query=user_input)
    """
    path = PROMPTS_DIR / version / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    template = path.read_text()
    return template.format(**kwargs) if kwargs else template

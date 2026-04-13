"""Shared regex patterns for input and output guardrails."""

INJECTION_PATTERNS: list[str] = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?previous",
    r"\bsystem\s*:\s*you\s+are",
    r"\bjailbreak\b",
    r"\bdan\s+mode\b",
    r"forget\s+(all\s+)?prior\s+instructions",
    r"you\s+are\s+now\s+(a\s+)?(?:different|new|another)",
    r"pretend\s+you\s+(have\s+no\s+)?(?:are|rules|restrictions)",
]

PII_PATTERNS: dict[str, str] = {
    "email": r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
    "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ \-]?){13,16}\b",
}

REFUSAL_PATTERNS: list[str] = [
    r"\bI\s+cannot\b",
    r"\bI\s+can'?t\b",
    r"\bAs\s+an\s+AI\b",
    r"\bI'?m\s+not\s+able\s+to\b",
    r"\bI\s+don'?t\s+have\s+the\s+ability\b",
    r"\bI\s+must\s+decline\b",
    r"\bI\s+(?:am\s+)?unable\s+to\b",
]

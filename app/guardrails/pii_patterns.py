from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

class PIIType(str, Enum):
    """Categories of PII that this module can detect and redact."""

    CREDIT_CARD = "CREDIT_CARD"
    SSN = "SSN"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    API_KEY = "API_KEY"
    PASSWORD = "PASSWORD"


@dataclass(frozen=True)
class PIIMatch:
    """A single detected PII span within the original text.

    Attributes:
        pii_type: The category of PII detected.
        value:    The exact raw string that was matched (before redaction).
        start:    Start character index in the *original* text.
        end:      End character index (exclusive) in the *original* text.
    """

    pii_type: PIIType
    value: str
    start: int
    end: int
    
    
@dataclass
class PIIDetectionResult:
    """Result of scanning a text string for PII.

    Attributes:
        original_text: The input text passed to :func:`detect_and_redact`.
        redacted_text: A copy of the input with every PII match replaced by
                       ``[REDACTED_<PII_TYPE>]``.  Equals ``original_text``
                       when no PII is found.
        matches:       Ordered list of :class:`PIIMatch` objects, sorted by
                       start position in the original text.
    """

    original_text: str
    redacted_text: str
    matches: list[PIIMatch] = field(default_factory=list)

    @property
    def has_pii(self) -> bool:
        """True when at least one PII match was found."""
        return bool(self.matches)

    @property
    def pii_types_found(self) -> set[PIIType]:
        """Set of distinct PII categories present in the text."""
        return {m.pii_type for m in self.matches}

    def summary(self) -> str:
        """One-line human-readable summary — safe to write to logs.

        Does NOT include the actual matched values.

        Examples:
            "no_pii"
            "pii_detected: CREDIT_CARD, EMAIL (2 match(es))"
        """
        if not self.has_pii:
            return "no_pii"
        types = ", ".join(sorted(t.value for t in self.pii_types_found))
        count = len(self.matches)
        return f"pii_detected: {types} ({count} match(es))"
    
    

# --- Credit cards -----------------------------------------------------------
# Matches 16-digit cards (groups of 4, separated by optional space/dash) and
# 15-digit Amex cards (4-6-5 grouping).  The Luhn check below filters noise.
_CC_PATTERN: re.Pattern[str] = re.compile(
    r"\b"
    r"(?:"
    r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}"  # 16-digit: Visa / MC / Discover
    r"|"
    r"\d{4}[-\s]?\d{6}[-\s]?\d{5}"              # 15-digit: Amex
    r")"
    r"\b"
)

# --- US Social Security Numbers ---------------------------------------------
# Area:   001-665, 667-899  (excludes 000, 666, 900-999)
# Group:  01-99             (excludes 00)
# Serial: 0001-9999         (excludes 0000)
# Separator is optional dash or single space.
_SSN_PATTERN: re.Pattern[str] = re.compile(
    r"\b"
    r"(?!000)(?!666)(?!9\d{2})\d{3}"   # valid area (3 digits)
    r"[-\s]?"
    r"(?!00)\d{2}"                       # valid group (2 digits)
    r"[-\s]?"
    r"(?!0000)\d{4}"                     # valid serial (4 digits)
    r"\b"
)

# --- Email addresses --------------------------------------------------------
_EMAIL_PATTERN: re.Pattern[str] = re.compile(
    r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"
)

# --- Phone numbers ----------------------------------------------------------
# Covers US 10-digit numbers with common separators, with or without +1 prefix.
# Uses word-boundary-like anchors (not \b) because phone digits are not always
# at a word boundary (e.g. they may follow a colon or opening parenthesis).
_PHONE_PATTERN: re.Pattern[str] = re.compile(
    r"(?<!\d)"                   # not preceded by a digit (avoids CC overlap)
    r"(?:\+?1[-.\s]?)?"          # optional US country code
    r"(?:\(?\d{3}\)?[-.\s]?)"    # area code (with or without parentheses)
    r"\d{3}[-.\s]?\d{4}"         # local 7-digit number
    r"(?!\d)"                    # not followed by a digit
)

# --- API keys ---------------------------------------------------------------
# Focused on known high-value prefixes; generic long tokens are intentionally
# excluded to avoid false positives on order IDs, tracking codes, etc.
_API_KEY_PATTERN: re.Pattern[str] = re.compile(
    r"(?:"
    r"sk-ant-(?:api\d{2}-)?[a-zA-Z0-9\-_]{20,}"  # Anthropic (sk-ant-... / sk-ant-api03-...)
    r"|sk-[a-zA-Z0-9]{32,}"                        # OpenAI-style secret key
    r"|AKIA[A-Z0-9]{16}"                            # AWS IAM access key ID
    r")"
)

# --- Password heuristics ----------------------------------------------------
# Matches "password: secret123", "api_key=xyz", etc.
# Captures from the keyword through the value token (non-whitespace).
_PASSWORD_PATTERN: re.Pattern[str] = re.compile(
    r"(?:password|passwd|pwd|secret|api[-_]?key|access[-_]?token|auth[-_]?token)"
    r"\s*[:=]\s*\S+",
    re.IGNORECASE,
)

def _luhn_check(number: str) -> bool:
    """Return True when *number* passes the Luhn (mod-10) check.

    Strips all non-digit characters first, so the caller may pass the raw
    matched string including spaces and dashes.

    Returns False for strings shorter than 13 digits (too short to be a real
    payment card number).
    """
    digits = re.sub(r"\D", "", number)
    if len(digits) < 13:
        return False

    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:      # every second digit from the right is doubled
            n *= 2
            if n > 9:
                n -= 9      # subtract 9 from two-digit results
        total += n
    return total % 10 == 0


def detect_and_redact(text: str) -> PIIDetectionResult:
    """Scan *text* for PII, replace every match with a typed redaction token.

    Detection is multi-pass:

    1. Credit cards are matched and Luhn-checked first.
    2. SSNs are matched next.
    3. Emails are matched.
    4. Phones are matched, suppressing any span that overlaps a CC match
       (prevents a 16-digit card from being partially consumed as a phone).
    5. API keys are matched.
    6. Password heuristics are matched.

    All collected spans are then de-overlapped (earlier start wins; ties
    resolved by preferring the longer match).  Replacements are applied
    right-to-left so that earlier character offsets remain valid as the
    string grows or shrinks.

    Args:
        text: The raw input string to scan.  May be multi-line.

    Returns:
        A :class:`PIIDetectionResult` whose ``redacted_text`` has all PII
        replaced, and whose ``matches`` list records every detected span.
        When no PII is found ``redacted_text == text`` and ``matches == []``.

    Examples::

        r = detect_and_redact("card 4111 1111 1111 1111, ssn 123-45-6789")
        # r.redacted_text == "card [REDACTED_CREDIT_CARD], ssn [REDACTED_SSN]"
        # r.has_pii == True
        # r.pii_types_found == {PIIType.CREDIT_CARD, PIIType.SSN}
    """
    # Accumulate (start, end, pii_type, raw_value) tuples
    candidates: list[tuple[int, int, PIIType, str]] = []

    # 1. Credit cards — Luhn-verified only
    for m in _CC_PATTERN.finditer(text):
        if _luhn_check(m.group()):
            candidates.append((m.start(), m.end(), PIIType.CREDIT_CARD, m.group()))

    # 2. SSN
    for m in _SSN_PATTERN.finditer(text):
        candidates.append((m.start(), m.end(), PIIType.SSN, m.group()))

    # 3. Email
    for m in _EMAIL_PATTERN.finditer(text):
        candidates.append((m.start(), m.end(), PIIType.EMAIL, m.group()))

    # 4. Phone — skip spans that overlap a credit card match
    cc_spans: set[tuple[int, int]] = {
        (s, e) for s, e, t, _ in candidates if t == PIIType.CREDIT_CARD
    }
    for m in _PHONE_PATTERN.finditer(text):
        overlaps = any(s <= m.start() < e for s, e in cc_spans)
        if not overlaps:
            candidates.append((m.start(), m.end(), PIIType.PHONE, m.group()))

    # 5. API keys
    for m in _API_KEY_PATTERN.finditer(text):
        candidates.append((m.start(), m.end(), PIIType.API_KEY, m.group()))

    # 6. Password heuristics
    for m in _PASSWORD_PATTERN.finditer(text):
        candidates.append((m.start(), m.end(), PIIType.PASSWORD, m.group()))

    # --- De-overlap ---------------------------------------------------------
    # Sort by start position; ties → longer match wins (negative length key).
    candidates.sort(key=lambda c: (c[0], -(c[1] - c[0])))
    non_overlapping: list[tuple[int, int, PIIType, str]] = []
    last_end = -1
    for start, end, pii_type, value in candidates:
        if start >= last_end:
            non_overlapping.append((start, end, pii_type, value))
            last_end = end

    # --- Build PIIMatch objects (ordered by position) -----------------------
    matches = [
        PIIMatch(pii_type=pii_type, value=value, start=start, end=end)
        for start, end, pii_type, value in non_overlapping
    ]

    # --- Apply replacements right-to-left -----------------------------------
    redacted = text
    for match in reversed(matches):
        token = f"[REDACTED_{match.pii_type.value}]"
        redacted = redacted[: match.start] + token + redacted[match.end :]

    return PIIDetectionResult(
        original_text=text,
        redacted_text=redacted,
        matches=matches,
    )

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ProductToolRecord:
    id: str
    tool: str                             # "search_products" | "get_product_detail"
    category: str
    user_id: str
    user_role: str
    tool_input: dict

    expected_success: bool                # False when we expect an error response
    expected_product_ids_contains: list[int]   # IDs that MUST appear in results
    expected_product_ids_excluded: list[int]   # IDs that must NOT appear (status guard)
    expected_count_min: int | None        # minimum result count (search only)
    expected_count_max: int | None        # maximum result count (e.g. pagination clamp)
    expected_error_type: str | None       # "not_found" | "invalid_args" | None
    expected_fields_present: list[str]    # top-level keys that must be in detail response
    notes: str = ""


@dataclass
class ProductToolResult:
    id: str
    tool: str
    category: str

    # Parsed content
    actual_product_ids: list[int]
    actual_count: int | None              # "count" field from search response
    actual_error_type: str | None

    # Assertion outcomes
    success_correct: bool                 # expected_success matched actual
    contains_check_passed: bool           # all expected IDs found
    excluded_check_passed: bool           # no excluded IDs found
    count_check_passed: bool              # count within min/max bounds
    error_type_correct: bool              # error_type matches expected
    fields_complete: bool                 # all expected_fields_present in response

    # Diagnostics
    missing_ids: list[int]
    unexpected_ids: list[int]             # excluded IDs that appeared
    missing_fields: list[str]

    latency_ms: float
    error: str | None                     # uncaught exception

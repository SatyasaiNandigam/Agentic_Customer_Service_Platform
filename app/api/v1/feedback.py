"""LangSmith user-feedback endpoint.

POST /api/v1/feedback
    Submit a satisfaction rating for a single chat turn.  The ``run_id``
    returned by ``POST /chat`` (or the WebSocket ``done`` event) links the
    feedback to the corresponding LangSmith trace so the evaluation dashboard
    and online-eval pipeline can incorporate it.

Design decisions
----------------
* **Score normalisation** — clients may send any of three formats:
    - ``score`` in [0.0, 1.0]  — stored as-is.
    - ``stars`` in {1, 2, 3, 4, 5} — normalised to [0.0, 1.0].
    - ``value`` = ``"thumbs_up"`` or ``"thumbs_down"`` — mapped to 1.0 / 0.0.
  Exactly one of the three must be supplied; the validator rejects the rest.

* **Graceful degradation** — when LangSmith tracing is disabled
  (``LANGCHAIN_TRACING_V2=false``) or the API key is empty, the endpoint
  returns 200 with ``submitted=false`` rather than an error, so the UI never
  breaks for users on a local dev stack without LangSmith credentials.

* **Async** — ``langsmith.Client.create_feedback`` is a synchronous blocking
  call.  We run it in a thread-pool via ``asyncio.to_thread`` so it never
  blocks the uvicorn event loop.

* **Singleton client** — the ``langsmith.Client`` instance is created once
  per process (lazy, module-level) and reused across requests.  The client is
  thread-safe for concurrent ``create_feedback`` calls.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Literal

import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator

import langsmith
from langsmith.schemas import FeedbackSourceType

from app.auth.middleware import CurrentUser
from app.config import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter()
settings = get_settings()

# ---------------------------------------------------------------------------
# Lazy LangSmith client singleton
# ---------------------------------------------------------------------------

_langsmith_client: langsmith.Client | None = None


def _get_langsmith_client() -> langsmith.Client:
    """Return (or create) the module-level LangSmith client singleton.

    The client reads ``api_url`` and ``api_key`` from settings so that
    changing the env var and restarting picks up new credentials without
    any code change.

    Thread-safety: ``langsmith.Client`` is safe for concurrent calls.
    """
    global _langsmith_client
    if _langsmith_client is None:
        _langsmith_client = langsmith.Client(
            api_url=str(settings.langchain_endpoint),
            api_key=settings.langchain_api_key,
        )
    return _langsmith_client


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class FeedbackRequest(BaseModel):
    """Payload for submitting a satisfaction rating for one chat turn.

    Exactly one of ``score``, ``stars``, or ``value`` must be supplied.

    Examples::

        # Thumbs up
        {"run_id": "<uuid>", "value": "thumbs_up"}

        # Five-star rating with a comment
        {"run_id": "<uuid>", "stars": 5, "comment": "Very helpful!"}

        # Raw normalised score
        {"run_id": "<uuid>", "score": 0.9, "key": "response_quality"}
    """

    run_id: str = Field(
        ...,
        description="LangSmith run ID returned by POST /chat or the WS 'done' event.",
    )
    key: str = Field(
        default="user_satisfaction",
        min_length=1,
        max_length=64,
        description=(
            "Feedback key stored in LangSmith. Defaults to 'user_satisfaction'. "
            "Use 'response_quality', 'groundedness', etc. for specialised ratings."
        ),
    )

    # -- Mutually exclusive score inputs --
    score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Normalised score in [0.0, 1.0].",
    )
    stars: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description="Star rating in {1…5}. Normalised to [0.0, 1.0] before storage.",
    )
    value: Literal["thumbs_up", "thumbs_down"] | None = Field(
        default=None,
        description="Binary thumbs rating. Mapped to score 1.0 (up) or 0.0 (down).",
    )

    comment: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional free-text comment attached to the feedback.",
    )

    # ---- Validators --------------------------------------------------------

    @field_validator("run_id")
    @classmethod
    def _validate_run_id(cls, v: str) -> str:
        """Ensure run_id is a valid UUID string (LangSmith rejects malformed IDs)."""
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError(f"run_id must be a valid UUID; got: {v!r}")
        return v

    @model_validator(mode="after")
    def _exactly_one_score_input(self) -> "FeedbackRequest":
        """Require exactly one of score / stars / value."""
        provided = [
            f
            for f, v in [("score", self.score), ("stars", self.stars), ("value", self.value)]
            if v is not None
        ]
        if len(provided) == 0:
            raise ValueError(
                "Provide exactly one of 'score' (float), 'stars' (int), or 'value' (thumbs)."
            )
        if len(provided) > 1:
            raise ValueError(
                f"Only one of 'score', 'stars', 'value' may be set; got: {provided}"
            )
        return self

    # ---- Computed normalised score -----------------------------------------

    @property
    def normalised_score(self) -> float:
        """Return the feedback score normalised to [0.0, 1.0].

        - ``score``      — returned as-is.
        - ``stars``      — mapped linearly: 1→0.0, 2→0.25, 3→0.5, 4→0.75, 5→1.0.
        - ``thumbs_up``  — 1.0
        - ``thumbs_down``— 0.0
        """
        if self.score is not None:
            return self.score
        if self.stars is not None:
            return (self.stars - 1) / 4.0  # 1→0.0, 5→1.0
        # value is "thumbs_up" or "thumbs_down"
        return 1.0 if self.value == "thumbs_up" else 0.0

    @property
    def string_value(self) -> str | None:
        """Return a human-readable string representation of the rating.

        LangSmith stores this alongside the numeric score in the ``value``
        field for display in the dashboard.
        """
        if self.value is not None:
            return self.value
        if self.stars is not None:
            return f"{self.stars} stars"
        return None


class FeedbackResponse(BaseModel):
    """Response body for the feedback endpoint."""

    feedback_id: str | None = Field(
        default=None,
        description=(
            "UUID assigned by LangSmith to this feedback record. "
            "``null`` when tracing is disabled."
        ),
    )
    submitted: bool = Field(
        ...,
        description="True when feedback was successfully sent to LangSmith.",
    )
    message: str = Field(..., description="Human-readable status message.")


# ---------------------------------------------------------------------------
# POST /feedback
# ---------------------------------------------------------------------------


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit user feedback for a chat turn",
    description=(
        "Attach a satisfaction rating to a traced chat run. "
        "The ``run_id`` is returned by ``POST /chat`` and the WebSocket "
        "``done`` event. Requires authentication — only authenticated users "
        "may submit feedback."
    ),
)
async def post_feedback(
    body: FeedbackRequest,
    user: CurrentUser,
) -> FeedbackResponse:
    """Submit user feedback to LangSmith for one chat turn.

    If LangSmith tracing is disabled or the API key is empty the call is
    accepted but not forwarded — the response includes ``submitted=false`` so
    clients can distinguish graceful-skip from an error.

    Raises:
        422 Unprocessable Entity: Invalid request body (bad UUID, missing score, etc.).
        503 Service Unavailable: LangSmith is reachable but returned an error.
    """
    log = logger.bind(
        user_id=user.user_id,
        run_id=body.run_id,
        key=body.key,
    )

    # -- Graceful skip when tracing is disabled --
    if not settings.langchain_tracing_v2 or not settings.langchain_api_key:
        log.info(
            "feedback.skipped",
            reason="tracing_disabled_or_no_api_key",
        )
        return FeedbackResponse(
            feedback_id=None,
            submitted=False,
            message="Feedback accepted but not forwarded — LangSmith tracing is disabled.",
        )

    score = body.normalised_score
    string_value = body.string_value

    log.info(
        "feedback.submitting",
        score=score,
        string_value=string_value,
        has_comment=body.comment is not None,
    )

    # -- Submit to LangSmith (blocking call — run in thread pool) --
    try:
        feedback_record = await asyncio.to_thread(
            _submit_feedback,
            run_id=body.run_id,
            key=body.key,
            score=score,
            value=string_value,
            comment=body.comment,
            user_id=user.user_id,
        )
    except Exception as exc:
        log.error("feedback.langsmith_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Failed to submit feedback to LangSmith. "
                "Please try again later."
            ),
        ) from exc

    feedback_id = str(feedback_record.id) if feedback_record else None
    log.info("feedback.submitted", feedback_id=feedback_id)

    return FeedbackResponse(
        feedback_id=feedback_id,
        submitted=True,
        message="Feedback submitted successfully.",
    )


# ---------------------------------------------------------------------------
# Synchronous LangSmith call (executed in thread pool by asyncio.to_thread)
# ---------------------------------------------------------------------------


def _submit_feedback(
    *,
    run_id: str,
    key: str,
    score: float,
    value: str | None,
    comment: str | None,
    user_id: int,
) -> langsmith.schemas.Feedback:
    """Call LangSmith's synchronous create_feedback API.

    Extracted into its own function so it can be:
    - Run in a thread pool without capturing a coroutine frame.
    - Unit-tested independently by patching ``_get_langsmith_client``.

    Args:
        run_id:   UUID string of the LangSmith run to annotate.
        key:      Feedback key (e.g. "user_satisfaction").
        score:    Normalised float score in [0.0, 1.0].
        value:    Optional string representation of the rating.
        comment:  Optional free-text comment.
        user_id:  Submitting user's ID — stored in ``source_info`` for auditing.

    Returns:
        The :class:`langsmith.schemas.Feedback` record created by LangSmith.

    Raises:
        Any exception raised by ``langsmith.Client.create_feedback``.
    """
    client = _get_langsmith_client()
    return client.create_feedback(
        run_id=run_id,
        key=key,
        score=score,
        value=value,
        comment=comment,
        source_info={"user_id": user_id},
        feedback_source_type=FeedbackSourceType.API,
    )

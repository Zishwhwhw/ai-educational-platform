"""Взаимная проверка решений.

Раньше жила в роутере отправки и принимала `reviewer_id: int = 1` параметром
запроса — то есть отзыв можно было оставить от чужого имени. Вынесена отдельно:
к прогону и зачёту решения она отношения не имеет.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.db.session import get_db
from app.models import PeerReview, Submission
from app.schemas.learning import PeerReviewCreate, PeerReviewResponse

router = APIRouter(prefix="/peer-reviews", tags=["peer-reviews"])


@router.post("/", response_model=PeerReviewResponse, status_code=status.HTTP_201_CREATED)
def create_peer_review(
    payload: PeerReviewCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> PeerReviewResponse:
    submission = db.get(Submission, payload.submission_id)
    if submission is None:
        raise NotFoundError("Submission not found")

    # Проверять собственное решение бессмысленно: смысл взаимной проверки
    # именно во взгляде со стороны.
    if int(submission.user_id) == int(current_user.id):
        raise PermissionDeniedError("You cannot review your own submission")

    already = db.execute(
        select(PeerReview).where(
            PeerReview.submission_id == payload.submission_id,
            PeerReview.reviewer_id == current_user.id,
        )
    ).scalar_one_or_none()
    if already is not None:
        raise ConflictError("You have already reviewed this submission")

    review = PeerReview(
        submission_id=payload.submission_id,
        reviewer_id=current_user.id,
        score=payload.score,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return PeerReviewResponse.model_validate(review)

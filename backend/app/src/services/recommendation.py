import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionLocal
from models.tables import TutorProfile, TutorTag
from schemas.suggestions import (
    ScoreBreakdown,
    SuggestionRequest,
    SuggestionResponse,
    SuggestionWeights,
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for the tutor recommendation algorithm.

    Algorithm steps:
    1. Hard Filters: subject, price, experience, verified, schedule slots, required tags
       → expressed as a single SQL query
    2. Soft Scoring: O1..O5 with student-specific weights
    3. Sort by score descending
    """

    @staticmethod
    async def get_suggestions(
        request: SuggestionRequest,
        user_id: str | None = None,
        session: AsyncSession | None = None,
    ) -> list[SuggestionResponse]:
        if session is None:
            async with AsyncSessionLocal() as db:
                return await RecommendationService._execute(db, request)
        return await RecommendationService._execute(session, request)

    @staticmethod
    async def _execute(
        db: AsyncSession, request: SuggestionRequest
    ) -> list[SuggestionResponse]:
        # Build the base query
        query = select(
            TutorProfile.user_id,
            TutorProfile.full_name,
            TutorProfile.hourly_rate,
            TutorProfile.experience_years,
            TutorProfile.is_verified,
            TutorProfile.is_new_boost,
            TutorProfile.rating_efficiency,
            TutorProfile.rating_communication,
            TutorProfile.rating_expertise,
            TutorProfile.rating_responsiveness,
        ).where(TutorProfile.subject_id == request.subject_id)

        # Hard Filters
        if request.max_price is not None:
            query = query.where(TutorProfile.hourly_rate <= request.max_price)

        if request.min_experience is not None and request.min_experience > 0:
            query = query.where(TutorProfile.experience_years >= request.min_experience)

        if request.verified_only:
            query = query.where(TutorProfile.is_verified.is_(True))

        result = await db.execute(query)
        rows = result.all()

        # Fetch tags for matching tutors
        tutor_ids = [row.user_id for row in rows]
        tags_query = select(
            TutorTag.tutor_id,
            TutorTag.tag_id,
        ).where(TutorTag.tutor_id.in_(tutor_ids))
        tags_result = await db.execute(tags_query)
        tutor_tags_map: dict = {}
        for tag_row in tags_result.all():
            tid = str(tag_row.tutor_id)
            if tid not in tutor_tags_map:
                tutor_tags_map[tid] = set()
            tutor_tags_map[tid].add(tag_row.tag_id)

        # Soft Scoring
        results: list[SuggestionResponse] = []
        weights = request.weights or SuggestionWeights()
        student_tags = set(request.required_tag_ids or [])

        for row in rows:
            is_new = bool(row.is_new_boost)

            # Normalize ratings (handle NULLs with boost for new tutors)
            o1 = float(row.rating_efficiency or (0.7 if is_new else 0.5))
            o2 = float(row.rating_communication or (0.7 if is_new else 0.5))
            o3 = float(row.rating_expertise or (0.7 if is_new else 0.5))
            o4 = float(row.rating_responsiveness or (0.7 if is_new else 0.5))

            # O5: Tag Match
            tutor_tags = tutor_tags_map.get(str(row.user_id), set())
            if not student_tags:
                o5 = 1.0
            else:
                intersection = student_tags.intersection(tutor_tags)
                o5 = len(intersection) / len(student_tags)

            # Final Score
            score = (
                o1 * weights.k1_effectiveness
                + o2 * weights.k2_communication
                + o3 * weights.k3_expertise
                + o4 * weights.k4_responsiveness
                + o5 * weights.k5_tags
            )

            results.append(
                SuggestionResponse(
                    tutor_id=row.user_id,
                    full_name=row.full_name,
                score=round(score, 3),
                    score_breakdown=ScoreBreakdown(
                        o1=round(o1, 3),
                        o2=round(o2, 3),
                        o3=round(o3, 3),
                        o4=round(o4, 3),
                        o5=round(o5, 3),
                    ),
                    hourly_rate=row.hourly_rate,
                    is_new=is_new,
                )
            )

        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        return results

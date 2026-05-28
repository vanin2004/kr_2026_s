from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.models.schemas import SuggestionRequest, TutorResponse

async def get_suggestions(db: AsyncSession, request: SuggestionRequest) -> List[TutorResponse]:
    # Normalize weights just in case
    total_weight = (request.weight_efficiency + request.weight_communication + 
                   request.weight_expertise + request.weight_responsiveness + request.weight_tags)
    
    if total_weight == 0:
        k1, k2, k3, k4, k5 = 0.30, 0.15, 0.20, 0.15, 0.20
    else:
        k1 = request.weight_efficiency / total_weight
        k2 = request.weight_communication / total_weight
        k3 = request.weight_expertise / total_weight
        k4 = request.weight_responsiveness / total_weight
        k5 = request.weight_tags / total_weight

    # Base query for tutors
    query = """
        SELECT 
            tp.user_id, tp.full_name, tp.specialization, tp.hourly_rate, 
            tp.experience_years, tp.rating_efficiency, tp.rating_communication, tp.rating_overall,
            COALESCE(array_agg(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') as tutor_tags
        FROM api.tutor_profiles tp
        LEFT JOIN api.tutor_tags tt ON tp.user_id = tt.tutor_id
        LEFT JOIN api.tags t ON tt.tag_id = t.id
        WHERE 1=1
    """
    params = {}
    
    # Apply hard filters
    if request.subject:
        query += " AND tp.specialization = :subject"
        params['subject'] = request.subject
    if request.max_rate:
        query += " AND COALESCE(tp.hourly_rate, 0) <= :max_rate"
        params['max_rate'] = request.max_rate
    if request.min_experience:
        query += " AND COALESCE(tp.experience_years, 0) >= :min_experience"
        params['min_experience'] = request.min_experience

    query += " GROUP BY tp.user_id, tp.full_name, tp.specialization, tp.hourly_rate, tp.experience_years, tp.rating_efficiency, tp.rating_communication, tp.rating_overall"
    
    # Execute
    result = await db.execute(text(query), params)
    tutors = result.fetchall()
    
    scored_tutors = []
    
    for row in tutors:
        # Defaults for cold start or missing data
        O1 = float(row.rating_efficiency) / 5.0 if getattr(row, 'rating_efficiency', None) is not None else 0.7
        O2 = float(row.rating_communication) / 5.0 if getattr(row, 'rating_communication', None) is not None else 0.7
        O3 = float(row.rating_overall) / 5.0 if getattr(row, 'rating_overall', None) is not None else 0.7
        O4 = 0.8 # Mock responsiveness for now
        
        # Tags match O5
        student_tags_set = set(request.desired_tags)
        tutor_tags_set = set(getattr(row, 'tutor_tags', []))
        
        if not student_tags_set:
            O5 = 1.0
        else:
            intersection = student_tags_set.intersection(tutor_tags_set)
            O5 = len(intersection) / len(student_tags_set)
        
        # Calculate final Match Score
        score = (O1 * k1) + (O2 * k2) + (O3 * k3) + (O4 * k4) + (O5 * k5)
        
        scored_tutors.append(TutorResponse(
            user_id=row.user_id,
            full_name=row.full_name,
            specialization=row.specialization,
            hourly_rate=row.hourly_rate,
            experience_years=row.experience_years,
            match_score=round(score * 100, 2)
        ))
    
    # Sort by match score descending
    scored_tutors.sort(key=lambda x: x.match_score, reverse=True)
    return scored_tutors

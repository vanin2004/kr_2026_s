from typing import List

from ..db.session import db_pool
from ..schemas.suggestions import ScoreBreakdown, SuggestionRequest, SuggestionResponse


class RecommendationService:
    @staticmethod
    async def get_suggestions(request: SuggestionRequest, user_id: str = None) -> List[SuggestionResponse]:
        # 1. Base SQL for Hard Filters
        query = """
            SELECT 
                tp.user_id, tp.full_name, tp.hourly_rate, tp.experience_years, 
                tp.is_verified, tp.is_new_boost,
                tp.rating_efficiency, tp.rating_communication, 
                tp.rating_expertise, tp.rating_responsiveness,
                ARRAY_AGG(tt.tag_id) as tutor_tags
            FROM tutor_profiles tp
            LEFT JOIN tutor_tags tt ON tp.user_id = tt.tutor_id
            WHERE tp.subject_id = $1
        """
        params = [request.subject_id]
        param_idx = 2

        if request.max_price:
            query += f" AND tp.hourly_rate <= ${param_idx}"
            params.append(request.max_price)
            param_idx += 1
        
        if request.min_experience:
            query += f" AND tp.experience_years >= ${param_idx}"
            params.append(request.min_experience)
            param_idx += 1
            
        if request.verified_only:
            query += " AND tp.is_verified = TRUE"

        # Group by profile fields
        query += """
            GROUP BY tp.user_id, tp.full_name, tp.hourly_rate, tp.experience_years, 
                     tp.is_verified, tp.is_new_boost,
                     tp.rating_efficiency, tp.rating_communication, 
                     tp.rating_expertise, tp.rating_responsiveness
        """
        
        # 2. Fetch data
        rows = await db_pool.fetch(query, *params)
        
        # 3. Soft Scoring
        results = []
        weights = request.weights or SuggestionWeights() # Default weights
        
        # Get requested tags for O5
        student_tags = set(request.required_tag_ids or [])
        
        for row in rows:
            # Normalize ratings (handle NULLs)
            o1 = float(row['rating_efficiency'] or 0.7 if row['is_new_boost'] else row['rating_efficiency'] or 0.5)
            o2 = float(row['rating_communication'] or 0.7 if row['is_new_boost'] else row['rating_communication'] or 0.5)
            o3 = float(row['rating_expertise'] or 0.7 if row['is_new_boost'] else row['rating_expertise'] or 0.5)
            o4 = float(row['rating_responsiveness'] or 0.7 if row['is_new_boost'] else row['rating_responsiveness'] or 0.5)
            
            # O5: Tag Match
            tutor_tags = set(row['tutor_tags'] if row['tutor_tags'][0] is not None else [])
            if not student_tags:
                o5 = 1.0
            else:
                intersection = student_tags.intersection(tutor_tags)
                o5 = len(intersection) / len(student_tags)
            
            # Final Score
            score = (
                o1 * weights.k1_effectiveness +
                o2 * weights.k2_communication +
                o3 * weights.k3_expertise +
                o4 * weights.k4_responsiveness +
                o5 * weights.k5_tags
            )
            
            # Boost for new tutors is already handled by default values in o1..o4 or could be explicit
            
            results.append(SuggestionResponse(
                tutor_id=row['user_id'],
                full_name=row['full_name'],
                score=round(score, 3),
                score_breakdown=ScoreBreakdown(o1=o1, o2=o2, o3=o3, o4=o4, o5=o5),
                hourly_rate=row['hourly_rate'],
                is_new=row['is_new_boost']
            ))
            
        # 4. Sort and return
        results.sort(key=lambda x: x.score, reverse=True)
        return results

from ..schemas.suggestions import SuggestionWeights

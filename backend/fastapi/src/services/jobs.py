from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def recalculate_ratings(db: AsyncSession, run_efficiency: bool, run_communication: bool):
    affected = 0
    
    if run_communication:
        query_comm = """
            UPDATE api.tutor_profiles tp
            SET rating_communication = (
                SELECT CAST(AVG(communication_score) AS DECIMAL(3,2))
                FROM api.reviews r
                WHERE r.tutor_id = tp.user_id
            )
            WHERE EXISTS (
                SELECT 1 FROM api.reviews r WHERE r.tutor_id = tp.user_id
            );
        """
        res = await db.execute(text(query_comm))
        affected += res.rowcount

    if run_efficiency:
        query_eff = """
            UPDATE api.tutor_profiles tp
            SET rating_efficiency = sub.avg_diff
            FROM (
                SELECT 
                    r1.tutor_id,
                    CAST(AVG(COALESCE(r2.score, 0) - COALESCE(r1.score, 0)) / 20 * 5 AS DECIMAL(3,2)) as avg_diff
                FROM api.student_results r1
                JOIN api.student_results r2 ON r1.student_id = r2.student_id AND r1.tutor_id = r2.tutor_id
                WHERE r1.type = 'initial_test' AND r2.type = 'control_test'
                GROUP BY r1.tutor_id
            ) sub
            WHERE tp.user_id = sub.tutor_id;
        """
        res = await db.execute(text(query_eff))
        affected += res.rowcount
            
    await db.commit()
    return {"status": "ok", "message": f"Updated {affected} records"}

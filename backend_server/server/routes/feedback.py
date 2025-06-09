import traceback
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend_server.database import Feedback as DBFeedback
from backend_server.database import User as DBUser
from backend_server.database import get_db
from backend_server.server.auth import get_current_active_user
from backend_server.server.schemas import FeedbackAdminResponse, FeedbackCreate, UserInDB
from backend_server.utils.logs import L

router = APIRouter()


@router.post("/feedback")
async def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: UserInDB = Depends(get_current_active_user),  # Use UserInDB for consistency
    db: AsyncSession = Depends(get_db),
):
    """
    Submit feedback from a user.
    The user is identified by the JWT token.
    """
    # Ensure the username in the payload matches the authenticated user,
    # or simply rely on current_user.username if that's the desired behavior.
    # For now, we'll use current_user.username as the source of truth.
    new_feedback = DBFeedback(
        user_username=current_user.username,  # Use username from the authenticated user
        feedback_text=feedback_data.feedback,
        timestamp=datetime.utcnow(),  # Use datetime from the datetime module
    )
    try:
        db.add(new_feedback)
        await db.commit()
        await db.refresh(new_feedback)
        return {"status": "success", "message": "Feedback submitted successfully."}
    except Exception as e:
        await db.rollback()
        L.error(f"Error submitting feedback: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Could not submit feedback.")


@router.get("/admin/feedbacks", response_model=List[FeedbackAdminResponse])
async def get_all_feedbacks(
    current_user: UserInDB = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve all feedbacks. Accessible only by admin users.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")

    try:
        result = await db.execute(
            select(
                DBFeedback.id, DBFeedback.user_username, DBUser.email, DBFeedback.feedback_text, DBFeedback.timestamp
            )
            .join(DBUser, DBFeedback.user_username == DBUser.username)
            .order_by(DBFeedback.timestamp.desc())
        )
        feedbacks = result.all()
        return [
            FeedbackAdminResponse(
                id=fb.id,
                user_username=fb.user_username,
                user_email=fb.email,
                feedback_text=fb.feedback_text,
                timestamp=fb.timestamp,
            )
            for fb in feedbacks
        ]
    except Exception as e:
        L.error(f"Error fetching all feedbacks: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Could not retrieve feedbacks.")

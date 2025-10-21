"""
Feedback API Routes
Allows users to submit feedback and bug reports which are created as GitHub issues
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Literal, Optional
import httpx
import os
from datetime import datetime, timedelta
from collections import defaultdict

router = APIRouter(prefix="/feedback", tags=["feedback"])

# Rate limiting: Track submissions by IP address
submission_tracker = defaultdict(list)
MAX_SUBMISSIONS_PER_DAY = 10
MAX_SUBMISSIONS_PER_HOUR = 3


class FeedbackSubmission(BaseModel):
    """Feedback submission model"""
    name: Optional[str] = Field(None, max_length=100, description="User's name (optional)")
    email: Optional[str] = Field(None, max_length=100, description="User's email (optional)")
    feedback_type: Literal["bug", "feedback", "question"] = Field(..., description="Type of feedback")
    message: str = Field(..., min_length=10, max_length=2000, description="Feedback message")


def check_rate_limit(ip_address: str) -> bool:
    """
    Check if IP address has exceeded rate limits
    Returns True if allowed, False if rate limited
    """
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    day_ago = now - timedelta(days=1)

    # Get submissions from this IP
    submissions = submission_tracker[ip_address]

    # Remove old submissions
    submissions = [s for s in submissions if s > day_ago]
    submission_tracker[ip_address] = submissions

    # Check limits
    recent_submissions = [s for s in submissions if s > hour_ago]

    if len(recent_submissions) >= MAX_SUBMISSIONS_PER_HOUR:
        return False
    if len(submissions) >= MAX_SUBMISSIONS_PER_DAY:
        return False

    return True


def record_submission(ip_address: str):
    """Record a submission timestamp for rate limiting"""
    submission_tracker[ip_address].append(datetime.now())


async def create_github_issue(feedback: FeedbackSubmission) -> dict:
    """
    Create a GitHub issue from feedback submission
    Returns the created issue data
    """
    # Get GitHub credentials from environment
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO", "lewistv/iz-apps-xcri")

    if not github_token:
        raise HTTPException(
            status_code=500,
            detail="GitHub integration not configured"
        )

    # Determine issue title and labels
    type_labels = {
        "bug": ["bug", "user-feedback"],
        "feedback": ["enhancement", "user-feedback"],
        "question": ["question", "user-feedback"]
    }

    type_titles = {
        "bug": "Bug Report",
        "feedback": "User Feedback",
        "question": "User Question"
    }

    # Build issue body
    issue_body = f"""## {type_titles[feedback.feedback_type]}

**Message:**
{feedback.message}

---

**Submitted by:** {feedback.name or 'Anonymous'}
**Email:** {feedback.email or 'Not provided'}
**Type:** {feedback.feedback_type}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Source:** XCRI Feedback Form
"""

    # Create GitHub issue via API
    url = f"https://api.github.com/repos/{github_repo}/issues"
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # Truncate message for title if needed
    title_message = feedback.message[:80] + "..." if len(feedback.message) > 80 else feedback.message

    payload = {
        "title": f"[User {type_titles[feedback.feedback_type]}] {title_message}",
        "body": issue_body,
        "labels": type_labels[feedback.feedback_type]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=10.0)

        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create GitHub issue: {response.text}"
            )


@router.post("/")
async def submit_feedback(feedback: FeedbackSubmission, request: Request):
    """
    Submit feedback which creates a GitHub issue

    Rate limited to:
    - 3 submissions per hour per IP
    - 10 submissions per day per IP
    """
    # Get client IP address
    client_ip = request.client.host

    # Check rate limit
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )

    try:
        # Create GitHub issue
        issue = await create_github_issue(feedback)

        # Record submission
        record_submission(client_ip)

        return {
            "success": True,
            "message": "Thank you for your feedback! We've received your submission.",
            "issue_number": issue.get("number"),
            "issue_url": issue.get("html_url")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )


@router.get("/status")
async def get_feedback_status():
    """
    Get feedback system status (for testing)
    """
    github_token = os.getenv("GITHUB_TOKEN")
    github_repo = os.getenv("GITHUB_REPO", "lewistv/iz-apps-xcri")

    return {
        "configured": bool(github_token),
        "repository": github_repo,
        "rate_limits": {
            "per_hour": MAX_SUBMISSIONS_PER_HOUR,
            "per_day": MAX_SUBMISSIONS_PER_DAY
        }
    }

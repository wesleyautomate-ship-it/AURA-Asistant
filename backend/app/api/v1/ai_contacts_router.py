from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["AI Contacts"])


class FollowUpRequest(BaseModel):
    contactId: str
    tone: Optional[str] = None
    goal: Optional[str] = None


class FollowUpDraft(BaseModel):
    draft: str


@router.post("/ai/followup", response_model=FollowUpDraft)
async def ai_followup(req: FollowUpRequest) -> FollowUpDraft:
    tone = req.tone or "Friendly"
    goal = req.goal or "Re-engage"
    draft = (
        f"Hi there,\n\nJust following up on our last conversation. "
        f"{ 'Would you be available for a quick call this week?' if goal.lower().startswith('schedule') else ''}"
        f"{ 'I attached a brochure with tailored options you might like.' if goal.lower().startswith('share') else ''}"
        f"{ 'I thought you might enjoy some fresh listings that match your preferences.' if goal.lower().startswith('nurture') else ''}"
        f"{ 'Let me know if you had any questions I can help with.' if goal.lower().startswith('re') else ''}"\
        f"\n\nBest regards,\nYour Agent\n\nTone: {tone}"
    )
    return FollowUpDraft(draft=draft)


class SummaryBody(BaseModel):
    contactId: str


class SummaryResponse(BaseModel):
    summary: str


@router.post("/ai/summarize", response_model=SummaryResponse)
async def ai_summarize(body: SummaryBody) -> SummaryResponse:
    return SummaryResponse(
        summary=(
            "Summary: Interested in waterfront, 2–3BR around 6M AED; prefers Marina/Palm, "
            "responsive to brochures; follow up this week."
        )
    )


class NextBestAction(BaseModel):
    title: str
    detail: str


@router.get("/ai/next-best-action", response_model=NextBestAction)
async def next_best_action(contactId: str = Query(...)) -> NextBestAction:
    return NextBestAction(
        title="Schedule a follow-up call",
        detail="They opened your brochure twice yesterday. Propose a 10–15 min call.",
    )


class Recommendation(BaseModel):
    id: str
    title: str
    area: str
    price: str
    route: str


class RecommendResponse(BaseModel):
    items: List[Recommendation]


@router.get("/ai/recommend", response_model=RecommendResponse)
async def recommend(contactId: str = Query(...)) -> RecommendResponse:
    return RecommendResponse(
        items=[
            Recommendation(
                id="rec-1",
                title="Marina 2BR with Sea View",
                area="Dubai Marina",
                price="AED 6.2M",
                route="/ai-workflow/brochure",
            ),
            Recommendation(
                id="rec-2",
                title="Palm Jumeirah 3BR",
                area="Palm Jumeirah",
                price="AED 6.8M",
                route="/ai-workflow/cma",
            ),
        ]
    )


from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models.schemas import TicketResponse
from app.core.orchestrator import Orchestrator

router = APIRouter(tags=["Support Tickets"])
orchestrator = Orchestrator()


@router.post("/support-ticket", response_model=TicketResponse)
async def create_support_ticket(
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None)
):
    if not audio and not image and not description:
        raise HTTPException(400, "Au moins un fichier ou une description est requis")

    try:
        result = await orchestrator.process(audio, image, description)
        
        return TicketResponse(
            transcription=result["transcription"],
            image_diagnostic=result["image_diagnostic"],
            rag_rule=result["rag_rule"],
            ticket_status=result["ticket_status"],
            confidence=result["confidence"],
            reasoning=result["reasoning"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur interne : {str(e)}")
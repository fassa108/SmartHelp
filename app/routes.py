from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models.schemas import TicketResponse
from app.utils.validators import (
    validate_audio_file,
    validate_image_file,
    read_file_within_limit
)
from app.services.audio_service import AudioService
from app.services.vision_service import VisionService
from app.services.rag_service import RAGService
from app.services.diagnostic_service import DiagnosticService

router = APIRouter(tags=["Support Tickets"])
audio_service = AudioService()
vision_service = VisionService()
rag_service = RAGService()
diagnostic_service = DiagnosticService()


@router.post("/support-ticket", response_model=TicketResponse)
async def create_support_ticket(
    audio: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None)
):
    if not audio and not image and not description:
        raise HTTPException(400, "Au moins un fichier ou une description est requis")

    audio_bytes = None
    image_bytes = None
    transcription = None
    image_diagnostic = None
    rag_rule = None
    ticket_status = "À vérifier"
    confidence = 0.5

    try:
        # === TRAITEMENT AUDIO ===
        if audio:
            audio_bytes = await read_file_within_limit(audio)
            validate_audio_file(audio, audio_bytes)
            transcription = audio_service.transcribe(audio_bytes, audio.filename)

        # === TRAITEMENT IMAGE ===
        if image:
            image_bytes = await read_file_within_limit(image)
            validate_image_file(image, image_bytes)
            image_diagnostic = vision_service.analyze(image_bytes)

        # === RAG (recherche dans la FAQ) ===
        if transcription or description:
            query_text = description or transcription
            rag_results = rag_service.query(query_text, top_k=3)
            rag_rule = "\n\n---\n".join(rag_results) if rag_results else "Aucune règle trouvée"
        else:
            rag_rule = "Pas de texte à analyser"

        # === DIAGNOSTIC FINAL ===
        diagnostic = diagnostic_service.diagnostiquer(
            transcription=transcription,
            image_diagnostic=image_diagnostic,
            rag_rule=rag_rule
        )

        return TicketResponse(
            transcription=transcription,
            image_diagnostic=image_diagnostic,
            ticket_status=diagnostic["ticket_status"],
            confidence=diagnostic["confidence"],
            reasoning=diagnostic["reasoning"]  
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur interne : {str(e)}")
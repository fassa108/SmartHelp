from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models.schemas import TicketResponse
from app.utils.validators import (
    validate_audio_file,
    validate_image_file, 
    read_file_within_limit
    )
from app.services.file_service import FileService

router = APIRouter(tags=["Support Tickets"])

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
    
    try:
        # 1. Lire l'audio en mémoire
        if audio:
            audio_bytes = await read_file_within_limit(audio)  # ← Lire d'abord
            validate_audio_file(audio, audio_bytes)            # ← Puis valider avec le contenu
        
        # 2. Lire l'image en mémoire
        if image:
            image_bytes = await read_file_within_limit(image)  # ← Lire d'abord
            validate_image_file(image, image_bytes)            # ← Puis valider avec le contenu
        
        return TicketResponse(
            transcription="Transcription en cours...",
            image_diagnostic="Analyse en cours...",
            rag_rule="Règle en cours...",
            ticket_status="À vérifier",
            confidence=0.85
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur interne : {str(e)}")
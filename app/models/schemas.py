from pydantic import BaseModel
from typing import Optional

class TicketResponse(BaseModel):
    transcription: Optional[str] = None
    image_diagnostic: Optional[str] = None
    ticket_status: str
    confidence: float
    reasoning: Optional[str] = None     
class ErrorResponse(BaseModel):
    detail: str
    status_code: int
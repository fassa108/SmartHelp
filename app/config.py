"""
Configuration centralisée — toutes les variables d'environnement du projet.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Serveur
    APP_NAME: str = "Support Ticket Assistant"
    DEBUG: bool = True
    PORT: int = 8000
    
    # Fichiers
    MAX_FILE_SIZE_MB: int = 50
    
    # Modèles IA (ajoutés progressivement)
    WHISPER_MODEL: str = "openai/whisper-small"
    VIT_MODEL: str = "google/vit-base-patch16-224"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Device
    INFERENCE_DEVICE: str = "cpu"
    
    # Types MIME autorisés
    ALLOWED_AUDIO_TYPES: set = {"audio/mpeg", "audio/wav", "audio/wave", "audio/x-wav"}
    ALLOWED_IMAGE_TYPES: set = {"image/png", "image/jpeg", "image/jpg", "image/bmp", "image/webp"}
    
    @property
    def ALLOWED_CONTENT_TYPES(self) -> set:
        return self.ALLOWED_AUDIO_TYPES | self.ALLOWED_IMAGE_TYPES
    
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    class Config:
        env_file = ".env"

settings = Settings()
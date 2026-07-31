from fastapi import HTTPException
from PIL import Image
import io

class FileService:
    @staticmethod
    async def read_image_from_bytes(contents: bytes) -> Image.Image:
        """Convertit des bytes en image PIL."""
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
            return Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception:
            raise HTTPException(400, "Fichier image invalide ou corrompu")
"""
Service d'inspection visuelle des produits - Transformers v5
"""

import io
import torch
from PIL import Image
from transformers import pipeline
from app.config import settings


class VisionService:
    _instance = None
    _pipe = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Charge le modèle VLM une seule fois (Singleton)."""
        device = 0 if torch.cuda.is_available() and settings.INFERENCE_DEVICE == "cuda" else -1
        
        model_name = settings.VLM_MODEL
        
        self._pipe = pipeline(
            task="image-text-to-text",
            model=model_name,
            device=device,
            torch_dtype=torch.float32 if device == "cpu" else torch.bfloat16
        )

    def analyze(self, image_bytes: bytes) -> str:
        """
        Analyse une image de produit pour détecter des défauts.
        Retourne un diagnostic textuel.
        """
        try:
            # Charger l'image
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # Prompt pour l'analyse
            instruction = (
                "Analyse cette image de produit. Réponds uniquement par un de ces mots : "
                "'conforme' si le produit n'a aucun défaut, "
                "'defaut' si tu vois une fissure, casse, rayure ou finition médiocre, "
                "ou 'incertain' si tu ne peux pas juger clairement."
            )
            
            # Format conversationnel pour image-text-to-text (v5)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": instruction},
                    ],
                }
            ]
            
            # Inférence
            output = self._pipe(text=messages, max_new_tokens=20, do_sample=False)
            
            # Extraire la réponse
            raw_text = output[0]["generated_text"][-1]["content"]
            
            # Parser la réponse
            return self._parse_output(raw_text)
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'analyse : {str(e)}")

    def _parse_output(self, raw_text: str) -> str:
        """Parse la réponse du modèle et retourne un diagnostic lisible."""
        text_lower = raw_text.lower()
        
        if "defaut" in text_lower or "defective" in text_lower:
            return "Produit présentant un défaut (casse, rayure, etc.)"
        elif "conforme" in text_lower or "compliant" in text_lower:
            return "Produit conforme, aucun défaut détecté"
        elif "incertain" in text_lower or "uncertain" in text_lower:
            return "Analyse incertaine, inspection manuelle recommandée"
        else:
            return f"Analyse non concluante : {raw_text}"
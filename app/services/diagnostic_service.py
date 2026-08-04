"""
Service de diagnostic - Logique métier pour déterminer le statut final.
"""

from app.models.schemas import TicketResponse


class DiagnosticService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def diagnostiquer(self, transcription: str, image_diagnostic: str, rag_rule: str) -> dict:
        status = "À vérifier"
        confidence = 0.5
        reasoning = []

        # === 1. RAG (priorité sur tout) ===
        if rag_rule and rag_rule != "Pas de texte à analyser":
            if "Refusé" in rag_rule or "Non remboursable" in rag_rule:
                status = "Refusé"
                confidence = 0.7
                reasoning.append("Règle RAG: refus")
            elif "Remboursable" in rag_rule:
                status = "Remboursable"
                confidence = 0.7
                reasoning.append("Règle RAG: remboursable")
            elif "À vérifier" in rag_rule or "En attente" in rag_rule:
                status = "À vérifier"
                confidence = 0.5
                reasoning.append("Règle RAG: à vérifier")
        
        # === 2. Image (vérification seulement) ===
        if image_diagnostic:
            if "défaut" in image_diagnostic.lower():
                if status != "Refusé":
                    status = "Remboursable"
                    confidence = min(confidence + 0.2, 0.95)
                    reasoning.append("Défaut détecté sur l'image")
            elif "conforme" in image_diagnostic.lower():
                if status == "Remboursable":
                    status = "À vérifier"
                    confidence = max(confidence - 0.1, 0.3)
                    reasoning.append("Produit conforme selon l'image")
        
        # === 3. Audio (mots-clés) ===
        if transcription:
            if "cassé" in transcription.lower() or "endommagé" in transcription.lower():
                if status != "Refusé":
                    status = "Remboursable"
                    confidence = min(confidence + 0.1, 0.95)
                    reasoning.append("Mots-clés audio: cassé/endommagé")
            elif "fait tomber" in transcription.lower() or "chute" in transcription.lower():
                if status == "Remboursable":
                    status = "À vérifier"
                    reasoning.append("Mots-clés audio: chute/mauvaise manipulation")
            elif "conforme" in transcription.lower():
                if status != "Refusé":
                    status = "À vérifier"
                    reasoning.append("Mots-clés audio: conforme")

        # === 4. Confiance finale ===
        confidence = round(min(confidence, 0.95), 2)

        return {
            "ticket_status": status,
            "confidence": confidence,
            "reasoning": " | ".join(reasoning) if reasoning else "Diagnostic par défaut"
        }
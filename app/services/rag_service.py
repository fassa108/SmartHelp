import pickle
import re
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import settings


class RAGService:
    _instance = None
    _model = None
    _chunks = []
    _embeddings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Charge ou crée les embeddings avec chunks longs (sections entières)."""
        cache_path = "app/data/embeddings.pkl"
        self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # 1. Charger depuis le cache si existant
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = pickle.load(f)
                self._chunks = data["chunks"]
                self._embeddings = data["embeddings"]
            print(f"RAG: {len(self._chunks)} chunks chargés du cache")
            return
        
        # 2. Lire le fichier FAQ
        with open(settings.FAQ_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 3. Découpage par SECTION (chunks longs)
        # Capture tout depuis "--- SECTION X :" jusqu'à la prochaine section ou la fin
        section_pattern = r"---\s*SECTION \d+ : .*?(?=---\s*SECTION \d+ : |\Z)"
        self._chunks = re.findall(section_pattern, content, re.DOTALL)
        
        # 4. Fallback : si pas de sections, découpage par règle
        if not self._chunks or len(self._chunks) < 2:
            rule_pattern = r"- REGLE \d+\.\d+ .*?(?=\n- REGLE \d+\.\d+|\Z)"
            self._chunks = re.findall(rule_pattern, content, re.DOTALL)
        
        # 5. Fallback final : découpage par ligne
        if not self._chunks:
            self._chunks = [line.strip() for line in content.split('\n') if line.strip() and line.startswith('-')]
        
        # 6. Vectorisation
        self._embeddings = self._model.encode(self._chunks)
        
        # 7. Sauvegarde du cache
        with open(cache_path, "wb") as f:
            pickle.dump({"chunks": self._chunks, "embeddings": self._embeddings}, f)
        
        print(f"RAG: {len(self._chunks)} chunks indexés et sauvegardés")

    def query(self, question: str, top_k: int = 5) -> list:
        """
        Recherche les chunks les plus pertinents.
        Retourne une liste de chunks (texte).
        """
        # 1. Embedding de la question
        q_embedding = self._model.encode([question])
        
        # 2. Calcul de la similarité cosinus
        similarities = cosine_similarity(q_embedding, self._embeddings)[0]
        
        # 3. Récupération des indices des meilleurs scores
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # 4. Retour des chunks correspondants
        return [self._chunks[i] for i in top_indices]
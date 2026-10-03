# Support Ticket Assistant

> Assistant API pour la création automatisée de tickets de support à partir d'audio, d'images et de texte.

## Description

Ce projet fournit une API FastAPI qui reçoit un audio, une image et/ou une description textuelle, puis exécute une chaîne de traitements (transcription audio, analyse d'image, recherche RAG et diagnostic LLM) pour produire un ticket de support structuré.

## Caractéristiques

- Transcription audio (Whisper)
- Analyse d'image (description / diagnostic)
- Recherche augmentée par récupération (RAG) sur la FAQ locale
- Diagnostic / recommandation via un LLM externe (clé GROQ)
- Points d'entrée d'API pour tests unitaires des services

## Structure du projet

- [app/](app/) : code principal de l'application
- [app/main.py](app/main.py) : point d'entrée FastAPI
- [app/routes.py](app/routes.py) : routes exposées (endpoint principal `/support-ticket` et endpoints de test)
- [app/config.py](app/config.py) : configuration via `.env` et `pydantic-settings`
- [app/services/](app/services/) : implémentations des services (audio, vision, rag, diagnostic)
- [app/core/](app/core/) : orchestrateur qui compose les services
- [app/data/](app/data/) : données projet (ex. `faq.txt`, base Chroma)
- `requirements.txt` : dépendances Python

## Installation

1. Cloner le dépôt et se placer à la racine du projet.
2. Créer et activer un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Configuration

Les paramètres sont gérés par `app/config.py` et peuvent être fournis via un fichier `.env` à la racine. Variables importantes :

- `GROQ_API_KEY` : clé API pour le service LLM externe (si utilisé)
- `PORT` : port d'exécution (par défaut `8000`)
- `INFERENCE_DEVICE` : `cpu` ou `cuda` selon le runtime

Créer un fichier `.env` minimal si nécessaire :

```
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
```

## Lancer l'application

Démarrer en mode développement avec Uvicorn :

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible sur `http://localhost:8000`. L'interface interactive Swagger est accessible via `http://localhost:8000/docs`.

## Endpoints principaux

- `GET /` : message d'accueil
- `GET /health` : état de santé
- `POST /support-ticket` : endpoint principal qui accepte `audio` (fichier), `image` (fichier) et/ou `description` (form field). Retourne `TicketResponse`.

Exemple d'appel minimal (description textuelle) :

```bash
curl -X POST "http://localhost:8000/support-ticket" -F "description=Mon imprimante ne s'allume plus"
```

Exemple d'envoi d'un fichier audio :

```bash
curl -X POST "http://localhost:8000/support-ticket" -F "audio=@/chemin/vers/audio.mp3" -F "description=Problème vocal"
```

Endpoints de test (unitaires pour chaque service) :

- `POST /test/audio` : teste uniquement le service audio
- `POST /test/image` : teste uniquement le service vision
- `POST /test/rag` : teste uniquement le service RAG
- `POST /test/diagnostic` : teste le service de diagnostic

## Schéma de réponse

La réponse principale est définie par `app/models/schemas.py` (`TicketResponse`) et contient :

- `transcription` : transcription audio (optionnel)
- `description_image` : description / diagnostic image (optionnel)
- `rag_rule` : résultat de la recherche RAG (optionnel)
- `ticket_status` : statut suggéré du ticket
- `confidence` : confiance du diagnostic (float)
- `reasoning` : explication / raisonnement (optionnel)

## Données & persistance

Le dossier `app/data/` contient les ressources locales (ex. `faq.txt`) et la base Chroma sous `app/data/chroma_db/`.

## Tests et développement

- Utilisez les endpoints `/test/*` pour vérifier rapidement les services.
- Pour le développement, activez `DEBUG` dans `.env` ou via `app/config.py`.

## Contribution

Les contributions sont bienvenues : ouvrez une issue pour discuter d'une fonctionnalité, puis soumettez une Pull Request.

## Licence

Ajoutez ici la licence souhaitée (ex. MIT) ou supprimez cette section si le dépôt est privé.

# Support Ticket Assistant API
API FastAPI pour l'automatisation des réclamations clients.
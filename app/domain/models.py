"""Modèles métier de cryptokilla (généré par create-gitsky-project).

Ne pas éditer à la main pour un besoin partagé : remonter la modification dans
le template puis propager via `copier update` (Chap 17).
"""

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.core.database import Base

# Enregistre les tables de l'arène (couche C1, AMEND-04) sur Base.metadata —
# nécessaire au create_all() dev (app/core/main.py, ENVIRONMENT=development
# uniquement) ; la prod passe par la migration Alembic dédiée
# (alembic/core/versions/0004_arena_c1_foundation.py).
from app.domain.arena import models as arena_models  # noqa: F401



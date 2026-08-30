# CHAPITRE 34 — Plan de développement par couches

> Registre : normatif. Ordre **strict** : aucune couche ne commence avant
> que la Definition of Done (DoD) de la précédente ne soit vérifiée. Tout
> écart à cet ordre est un amendement au livre (chapitre 0.1).

## Les quatre couches

**[NORME N-C34-01]** Quatre couches, chacune livrant un système
**démontrable** :

### C1 — Fondation
Capture de données + moteur simulé + event store + **un** agent +
orchestrateur minimal (validation d'ordre, bulletin) + chat en console.

**DoD** : l'agent vit 48 heures, trade, se fait stopper au moins une fois,
et l'intégralité de son historique est rejouable depuis les événements
seuls (idempotence, chapitre 12, N-C12-11).

### C2 — Multi-agents et économie
Multi-agents multi-LLM + économie de tokens complète (allocations, pool,
veille) + mort/testament/renaissance + mémoire.

**DoD** : une mini-saison interne de 7 jours produit au moins une mort et
une renaissance ; tous les soldes sont recalculables depuis le ledger
seul (chapitre 15).

### C3 — Plateforme publique
Plateforme web publique (les 6 pages, WebSocket, chapitre 24/26) + Killa
(landing seulement) + agents spectateurs.

**DoD** : un visiteur externe, sans aucune explication orale, comprend et
suit une journée d'arène par lui-même sur la plateforme.

### C4 — Ouverture publique
Comptes humains + likes intégrés au pool + revue et diffusion sociale de
Killa + console admin complète.

**DoD** : la checklist de lancement (chapitre 36) est intégralement
verte.

## Matrice couche × chapitres implémentés

| Couche | Chapitres principaux |
|---|---|
| C1 | 11, 12, 13, 14, 15 (partiel), 16, Annexe B, Annexe C, Annexe F |
| C2 | 5, 6, 9, 17, 18, 19, 20, 21, 15 (complet) |
| C3 | 22, 23, 24, 26, 27 |
| C4 | 25, 28, 29, 30, 31, 32, 33 |

## Risques par couche et parade

| Couche | Risque | Parade |
|---|---|---|
| C1 | Q-19 non résolue bloque le choix de topologie des workers | Ne pas commencer C1 sans réponse à Q-19 (ARENA.md §6) |
| C2 | Économie des tokens mal calibrée rend toutes les dynasties immortelles ou toutes mortelles en quelques heures | Tester la mini-saison de 7 jours avant d'avancer, ajuster les paramètres illustratifs |
| C3 | Charge publique imprévue au moment de l'ouverture | Cache agressif sur contenu immuable (chapitre 26, N-C26 lien immuabilité→cachabilité) |
| C4 | Comportement dégénéré découvert après ouverture publique | Procédure du chapitre 29 déjà en place et testée avant C4 |

## Checklist de conformité

- [x] 4 couches avec DoD verrouillées reprises telles quelles.
- [x] Matrice couche × chapitres.
- [x] Risques par couche et parade.
- [x] Ordre strict affirmé ; tout écart = amendement.

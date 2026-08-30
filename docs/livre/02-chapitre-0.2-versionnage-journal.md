# CHAPITRE 0.2 — Versionnage et journal des décisions

> Registre : gouvernance.

## Versionnage sémantique du livre

**[NORME N-C0.2-01]** Le livre est versionné : `v0.x` désigne le
brainstorming (l'état actuel de rédaction, lot par lot) ; `v1.0` marque le
**gel pour développement** — le moment où le texte cesse d'être en
construction active et devient la référence contre laquelle le code est
écrit ; `v1.x` couvre les amendements ultérieurs pendant le développement
(comme AMEND-B1 à AMEND-13, déjà intégrés au fil de la rédaction).

## Journal et registre — normatifs

**[NORME N-C0.2-02]** Le journal des décisions et le registre des
questions ouvertes vivent tous deux en **Annexe G** et sont **normatifs** :
une question ouverte marquée **bloquante** empêche le gel `v1.0` tant
qu'elle n'est pas tranchée.

## Format d'une entrée de journal

```
D-<numéro> — <énoncé de la décision>
Chapitre(s) propriétaire(s) : <référence>
Alternative écartée : <si connue>
```

## Classification proposée des questions ouvertes (à valider, non tranchée)

**[NORME N-C0.2-03]** « Bloquante pour v1.0 » désigne ici ce qui empêche
le **gel du livre et le démarrage du développement** (couche C1) —
distinct d'une question qui gate seulement un jalon plus tardif (une
couche ultérieure, le lancement de la saison 1, ou une bascule future vers
le réel). Sur cette base, seule **Q-19** bloque au sens strict le gel
`v1.0` : elle bloque explicitement la couche C1 elle-même (ARENA.md §6).
Toutes les autres questions non tranchées gatent un jalon spécifique et
plus tardif, sans empêcher le développement de commencer.

**Proposition de classification (à valider par l'admin)** :

| Q | Sujet | Classe proposée | Jalon réellement concerné |
|---|---|---|---|
| Q-01 | Seuil de mort (zéro strict ou plancher) | Non bloquante | Avant saison 1 (chapitre 36) |
| Q-02 | Take profit obligatoire ? | Non bloquante | Avant saison 1 |
| Q-03 | Testaments/dynasties traversent les saisons ? | Non bloquante | Aucun jalon précis, v1 fonctionne sans trancher |
| Q-04 | Modification params secrets en saison | **Tranchée** (Lot 2) | — |
| Q-05 | Paires, devise, capital initial exact | Non bloquante | Avant saison 1 |
| Q-06 | Versions LLM épinglées, politique MAJ | Non bloquante | Avant saison 1 |
| Q-07 | Compression du temps en saison à blanc | Non bloquante | Avant toute saison à blanc (chapitre 35) |
| Q-08 | Une position par paire ou cumul | **Tranchée** (Lot 2) | — |
| Q-09 | Compaction de contexte facturée ? | Non bloquante | Aucun jalon précis |
| Q-10 | Plafond/distillation de l'héritage | Non bloquante | Saisons très longues seulement |
| Q-11 | Personnalité identique à la renaissance ? | Non bloquante | Avant saison 1 |
| Q-12 | Garde-fou de toxicité du chat public | Non bloquante pour v1.0 | **Bloquante pour l'ouverture publique du chat** (couche C3/C4, chapitre 36) |
| Q-13 | Embeddings : local ou API | Non bloquante | Avant couche C2 |
| Q-14 | Messages des spectateurs dans le chat | **Reportée** | Saison future, hors périmètre v1 |
| Q-15 | Monétisation | **Reportée** | Hors périmètre du livre (chapitre 25) |
| Q-16 | Revue juridique RGPD | Non bloquante | **Bloquante pour couche C4** |
| Q-17 | Statut juridique du live réel | **Reportée** | Bloquante uniquement pour une bascule future au réel, jamais pour v1 |
| Q-18 | Journal d'audit admin public ? | Non bloquante | Aucun jalon précis |
| Q-19 | Infrastructure du template (workers, WS, tâches planifiées) | **Bloquante pour v1.0** | Couche C1 — condition de démarrage du développement |
| Q-20 | Killa/spectateurs/notation sur `MODULE_AGENTIC` ou domaine | Non bloquante | Avant couche C3 |

## Checklist de conformité

- [x] Sémantique `v0`/`v1` posée (N-C0.2-01).
- [x] Classification proposée pour chaque Q-xx, marquée « Proposition », rien n'est tranché.

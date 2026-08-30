# CHAPITRE 35 — Stratégie de test

> Registre : normatif. Dépendances : l'ensemble des `[NORME]` du livre.

## Une norme, un test minimum

**[NORME N-C35-01]** Chaque `[NORME]` du livre a **au moins un** test
automatisé. La traçabilité `N-<chapitre>-<n°>` → test est maintenue dans
une table générée (format : `id de la norme | fichier de test | statut`),
régénérée à chaque exécution de la suite de tests plutôt que tenue à la
main.

## Stub LLM obligatoire

**[NORME N-C35-02]** Tous les composants doivent être testables avec un
LLM **scripté** (réponses déterministes, sans appel réseau réel) — aucune
logique du système n'a le droit d'exiger un vrai appel LLM pour être
testée. C'est ce qui rend la suite reproductible et rapide, y compris
pour les chemins normalement peuplés par la cognition d'un agent (boucle
du chapitre 16, notation du chapitre 12.4).

## Architecture de test

- **Unités** — chaque composant (moteur de fill, pipeline de validation,
  machine à états) testé isolément avec des entrées déterministes.
- **Intégration** — la séquence horaire complète (chapitre 12.2), un
  cycle naissance→mort→renaissance (chapitres 5, 21), rejouée avec le
  stub LLM.
- **Saison à blanc** — au moins une mini-saison accélérée exécutée avant
  tout lancement public (couche C3/C4, chapitre 34).

## Saisons à blanc — compression du temps

**[OUVERT : Q-07]** — deux options possibles pour compresser le temps
d'une saison à blanc, non tranchées ici :

1. **Horloge accélérée globale** — le temps du système avance plus vite
   que le temps réel (ex. 1 heure simulée = 1 minute réelle), les
   composants restant inchangés.
2. **Rejeu de données historiques en accéléré** — une période de marché
   déjà capturée est rejouée à travers le moteur (chapitre 13.3, usage
   « replay »), à une cadence artificielle.

Les deux options sont documentées ici sans arbitrage ; le choix reste à
faire avant la première saison à blanc.

## Six scénarios de chaos (liste minimale verrouillée)

| # | Scénario | Comportement attendu |
|---|---|---|
| 1 | Crash d'un agent en plein cycle de raisonnement | Reprise sans pénalité (R-17, chapitre 16.5) ; état reconstruit depuis la base. |
| 2 | Crash de l'orchestrateur entre les étapes 3 et 4 de la séquence horaire | Reprise idempotente : aucune double allocation (chapitre 12, N-C12-11) — test dédié de l'exigence d'idempotence. |
| 3 | Panne du flux Kraken | Gel des validations d'ordre, marquage `stale`, `season.event kind: notice` publié (chapitre 12, N-C12-17 ; chapitre 14.1). |
| 4 | Réponse LLM malformée ou timeout | L'appel échoue proprement (`E-TIMEOUT`/`E-SCHEMA`, Annexe C), aucun état corrompu. |
| 5 | Base verrouillée en écriture | Les écritures en attente sont retentées ou mises en file, aucune perte silencieuse d'événement. |
| 6 | Tentative d'injection via `web_fetch` | Le rayon d'explosion borné contient l'effet (chapitre 28, N-C28-03) : au pire, un trade borné par le moteur de risque déterministe. |

## Checklist de conformité

- [x] « 1 [NORME] = 1 test minimum » présent (N-C35-01).
- [x] Stub LLM obligatoire (N-C35-02).
- [x] Les 6 scénarios de chaos couverts.
- [x] Q-07 documentée avec ses deux options, non tranchée.

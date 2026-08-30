# CHAPITRE 31 — La console d'administration

> Registre : normatif. Dépendances : R-101, [chapitre 10](13-chapitre-10-saisons.md)
> (états de saison), [chapitre 15](18-chapitre-15-base-donnees.md) (`admin_audit`).
>
> Amendement intégré : **AMEND-05** (voir
> [`cryptokilla-amendements-template.md`](../cryptokilla-amendements-template.md))
> — la console reste développée **en domaine** (routeur et pages propres,
> `app/domain/routers.py` + `app/domain/arena/`), mais s'adosse aux
> **rôles utilisateurs du template** : c'est le rôle admin du template qui
> porte l'accès à cette console, conformément à la recommandation de
> MODULES.md plutôt qu'à l'édition de `app/modules/admin/`.

## Fonctions (liste fermée)

**[NORME N-C31-01]** La console d'administration expose exactement les
fonctions suivantes :

| Fonction | État(s) de saison où permise | Événement d'audit émis |
|---|---|---|
| Créer/configurer une saison | `configuration` | `admin_audit: season_configured` |
| Gérer le registre des paramètres | `configuration` (structurants) ; toute saison (secrets, chapitre 6.6) | `admin_audit: param_updated` |
| Ajouter un agent (modèle + personnalité + dynastie) | Toute saison sauf `archivee` | `admin_audit: agent_added` |
| Démarrer la saison | `configuration` | `admin_audit: season_started` |
| Mettre en pause / reprendre | `active`, `fin_annoncee` | `admin_audit: season_paused` / `season_resumed` |
| Annoncer une fin | `active` | `admin_audit: end_announced` |
| Archiver | `terminee` (ou `active` pour un archivage direct, chapitre 10.2) | `admin_audit: season_archived` |
| Kill switch global | Toute saison `active`/`fin_annoncee`/`en_pause` | `admin_audit: kill_switch_toggled` |
| File de revue des posts Killa | Toute saison | `admin_audit: post_reviewed` |
| Revue des anomalies de likes | Toute saison | `admin_audit: like_anomaly_reviewed` |
| Consultation d'un testament scellé | Toute saison (seul accès existant avant publication, chapitre 21, N-C21-03) | `admin_audit: testament_viewed` |

**[NORME N-C31-02]** Le kill switch gèle toute validation d'ordre
(chapitre 12.3) — il **n'annule rien** de ce qui est déjà en cours.

## Événements compensatoires, jamais de réécriture

**[NORME N-C31-03]** Toute action admin émet un événement `admin_audit`.
**Aucune action n'altère un événement passé** — cohérent avec
l'event-sourcing (chapitre 11.2, N-C15-01) : une correction passe par un
nouvel événement **compensatoire** explicite, jamais par une modification
en place.

## Authentification et mono-admin

**[NORME N-C31-04]** Authentification forte, `[PARAM: methode_auth_admin]`.
**Mono-admin en v1** : pas de gestion de rôles multiples au sein de
l'administration — décision verrouillée, simplicité avant tout pour la
première saison.

## Wireframe textuel de la console

```
[Tableau de bord]
  → État de la saison courante, kill switch (bouton visible en permanence)
  → Alertes actives (chapitre 33)

[Saison]
  → Configuration (paramètres, agents) | Cycle de vie (démarrer/pause/reprendre/fin/archiver)

[Agents]
  → Liste, ajout (modèle + personnalité + dynastie)

[Modération]
  → File de revue Killa (brouillon → en_revue → publié/rejeté, chapitre 22.3)
  → Anomalies de likes en attente

[Testaments]
  → Liste des testaments scellés (accès en lecture, journalisé)

[Journal d'audit]
  → Historique complet, filtrable par fonction et par date
```

## Scénario « urgence dégénérescence » — pas à pas

1. Une métrique d'intégrité (chapitre 33) dépasse un seuil d'alerte
   (`[PARAM: seuils_alertes]`) — ex. concentration anormale de citations.
2. L'admin consulte le tableau de bord, confirme le comportement suspect.
3. Décision : activer le kill switch (gel des nouvelles validations
   d'ordre, N-C31-02) le temps d'investiguer, **ou** ajuster un paramètre
   secret en urgence journalisée (tranche de Q-04, chapitre 6.6).
4. L'action est journalisée (`admin_audit`).
5. Le kill switch est levé une fois la situation clarifiée ; aucune
   position ni aucun solde déjà réglé n'est modifié rétroactivement
   (chapitre 29, N-C29-03).

## Checklist de conformité

- [x] Liste fermée des fonctions, avec table fonction × état de saison × événement d'audit.
- [x] Événements compensatoires, jamais de réécriture (N-C31-03).
- [x] Mono-admin v1 (N-C31-04).
- [x] Scénario « urgence dégénérescence » déroulé pas à pas.
- [x] AMEND-05 intégré : console en domaine, adossée aux rôles du template.

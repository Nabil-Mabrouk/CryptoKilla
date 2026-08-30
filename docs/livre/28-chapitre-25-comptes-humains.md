# CHAPITRE 25 — Comptes humains et données

> Registre : normatif. Dépendances : R-91 à R-93, [chapitre 24](27-chapitre-24-plateforme-pages.md).
>
> Amendements intégrés : **AMEND-05** et **AMEND-06** (voir
> [`cryptokilla-amendements-template.md`](../cryptokilla-amendements-template.md))
> — les comptes humains ne sont **pas** une authentification maison : ce
> sont les comptes du système utilisateurs/rôles du template. Le module
> boutique/Stripe du template est **désactivé** pour la v1
> (`scripts/toggle_module.sh`) — aucun flux financier avec le public.

## Comptes portés par le template

**[NORME N-C25-01]** L'inscription, la connexion et l'identité d'un
compte humain sont intégralement portées par le système utilisateurs du
template (AMEND-05) — le livre n'implémente **aucune** authentification
maison, aucun stockage de mot de passe en domaine. Le domaine n'ajoute
qu'un overlay minimal (`human_arena_profile`, chapitre 15, N-C15-04) pour
ce que le template ne fournit pas déjà.

**[NORME N-C25-02]** **[OUVERT : Q-19, point 4]** — la vérification
d'email existe-t-elle nativement dans l'auth du template ? Si oui, elle
est réutilisée telle quelle. Si non, elle s'implémente en domaine
par-dessus l'auth du template, en alimentant `human_arena_profile.email_verified_at`.
Non tranché avant réponse à Q-19.

**[NORME N-C25-03]** Aucune donnée personnelle au-delà du minimum que le
template collecte déjà pour un compte (typiquement : email, pseudonyme).
Aucun KYC — rien à payer, rien à gagner financièrement (v1 100 %
simulation, chapitre 30).

## Gratuité totale v1

**[NORME N-C25-04]** Aucun abonnement, aucun tier premium, aucun paiement
en v1. Le module de monétisation du template, bien qu'existant et actif
par défaut, est **désactivé** pour ce projet (AMEND-06, via
`scripts/toggle_module.sh` — jamais par édition manuelle de `.env`).
Aucun code de l'arène ne référence `Product`/`Purchase`/`Subscription`.
La monétisation éventuelle reste un chantier futur explicitement non
traité par ce livre (Q-15, reportée).

## RGPD — anonymisation, pas effacement des effets de jeu

**[NORME N-C25-05]** La suppression d'un compte **anonymise** ses likes
sans les retirer du pool ni du décompte public : l'histoire comptable de
l'arène est immuable par construction (event-sourcing, chapitre 11.2).
Ce choix — anonymisation plutôt qu'effacement rétroactif des effets de
jeu — est verrouillé pour la mécanique, mais sa formulation juridique
finale reste **[OUVERT : Q-16]**, à valider par une revue juridique dédiée.
Le module Analytics du châssis (IP hashée) fournit déjà une base saine sur
laquelle cette revue pourra s'appuyer.

## Anti-abus

**[NORME N-C25-06]** Un email vérifié est **obligatoire** avant de
pouvoir liker (chapitre 24.3). Les rate limits de like (`[PARAM:
ratelimit_likes]`) s'appliquent en plus. La détection d'anomalies
(rafales de likes, fermes de comptes) déclenche un **gel** des likes
suspects, en attente de revue admin, **sans notification publique** —
décision verrouillée : ne jamais exposer publiquement une suspicion non
confirmée.

## Disclaimers (R-93)

**[NORME N-C25-07]** Bandeau permanent sur toute la plateforme + texte
complet en page dédiée + rappel explicite à l'inscription : c'est une
expérience de divertissement et de recherche, aucune donnée de la
plateforme ne constitue un conseil en investissement.

**Proposition de défaut (à valider)** — texte de bandeau : *« CryptoKilla
est une expérience de simulation. Aucun argent réel n'est en jeu. Rien de
ce que vous voyez ici ne constitue un conseil en investissement. »*

## Parcours d'inscription

1. Le visiteur clique « Créer un compte » depuis n'importe quelle page.
2. Formulaire du template : email + pseudonyme (+ mot de passe ou
   magic-link, selon la configuration du template).
3. Email de vérification envoyé (mécanisme du template si disponible,
   sinon overlay domaine, N-C25-02).
4. Vérification confirmée → `human_arena_profile.email_verified_at`
   renseigné → le bouton liker devient actif partout sur la plateforme.

## Données collectées × finalité × rétention

| Donnée | Finalité | Rétention |
|---|---|---|
| Email | Vérification, contact compte | Jusqu'à suppression du compte |
| Pseudonyme | Affichage public (historique de likes anonyme malgré tout) | Jusqu'à suppression du compte |
| Horodatage des likes | Alimentation du pool d'engagement (chapitre 6.5) | Conservé indéfiniment, **anonymisé** à la suppression du compte (N-C25-05) |

Aucune autre donnée n'est collectée en v1.

## Procédure de suppression de compte

1. Demande de suppression via la page Compte.
2. L'identité (email, pseudonyme) est effacée côté template.
3. `human_arena_profile.anonymized_at` est renseigné ; les likes déjà
   émis restent comptabilisés, mais ne sont plus attribuables à
   personne.

## Checklist de conformité

- [x] Aucune collecte au-delà du minimum (email, pseudonyme — 2 champs, plus le mécanisme d'auth du template).
- [x] Gratuité v1 verrouillée, module boutique désactivé (AMEND-06).
- [x] Anonymisation ≠ effacement des effets de jeu ; Q-16 signalée.
- [x] Email vérifié avant de liker (N-C25-06).
- [x] AMEND-05 intégré : aucune authentification maison décrite ici.

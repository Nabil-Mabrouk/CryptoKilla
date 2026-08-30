# CHAPITRE 10 — Les saisons

> Registre : normatif dominant. Dépendances : R-70 à R-74
> (voir [`cryptokilla-regles-experience.md`](../cryptokilla-regles-experience.md)),
> chapitre 12 (séquence horaire), chapitre 31 (console admin — cité).
>
> Scénario fil rouge : saison `s1`.

## Rôle du chapitre

Le temps long de l'arène : configuration, vie, pause, fin, archivage d'une
saison.

## 10.1 — Machine à états de la saison

**[NORME N-C10-01]** Une saison est à tout instant dans exactement un des
six états suivants :

| État | Signification |
|---|---|
| `configuration` | Saison en préparation, non encore ouverte aux agents. |
| `active` | Saison en cours, séquence horaire H+0 opérationnelle. |
| `en_pause` | Cognition gelée, mécanique vivante (10.3). |
| `fin_annoncée` | Une date de fin publique a été fixée ; la saison reste active jusqu'à l'échéance. |
| `terminée` | Fermeture forcée effectuée, classement final figé. |
| `archivée` | Historique conservé, saison figée en lecture (R-74). |

**[NORME N-C10-02]** Toute transition entre états résulte exclusivement
d'une action admin (R-101, chapitre 31), et chaque transition est
journalisée (`admin_audit`).

```mermaid
stateDiagram-v2
    state "fin_annoncée" as fin_annoncee
    [*] --> configuration
    configuration --> active: admin démarre la saison
    active --> en_pause: admin met en pause
    en_pause --> active: admin reprend
    active --> fin_annoncee: admin fixe une date de fin
    fin_annoncee --> en_pause: admin met en pause
    en_pause --> fin_annoncee: admin reprend (fin déjà annoncée)
    fin_annoncee --> terminée: échéance atteinte (fermeture forcée)
    active --> terminée: admin archive sans date (mode perpétuel)
    terminée --> archivée: admin archive
    archivée --> configuration: admin réinitialise (nouvelle saison)
```

## 10.2 — Les trois modes de fin

Développement de R-70 :

**[NORME N-C10-03]** **Datée** — une date publique de fin est connue des
agents (rappelée dans les règles générales, chapitre 18.2, et dans les
bulletins à l'approche de l'échéance, `[PARAM: preavis_rappel_fin]`). À
l'échéance, toutes les positions ouvertes sont fermées de force au prix du
marché (`close_reason: season_end`), le classement final est gelé, la
saison passe en `terminée`.

**[NORME N-C10-04]** **Perpétuelle** — aucune date de fin fixée ; l'admin
peut à tout moment soit basculer vers une fin datée, soit archiver
directement — d'un seul geste admin, mais cet archivage direct implique la
même fermeture forcée des positions et le même gel du classement qu'une
fin datée (10.1, transition `active → terminée → archivée` du diagramme
ci-dessus) : « directement » qualifie l'action de l'admin, pas un
raccourci des états traversés.

**[NORME N-C10-05]** **Archivage** — fige et conserve l'intégralité de
l'historique (R-74) ; une réinitialisation crée une saison neuve, distincte.

## 10.3 — La pause

Développement de R-71/R-72 :

**[NORME N-C10-06]** En pause : la **cognition** est intégralement gelée
— agents traders, orchestrateur, Killa et agents spectateurs sont tous en
veille, à zéro consommation de tokens. La **mécanique** reste vivante : le
moteur d'exécution continue seul de surveiller et déclencher stops et take
profits (chapitre 13), indépendamment de l'orchestrateur (chapitre 12, N-C12-09).

**[NORME N-C10-07]** Les agents sont **informés** de la mise en pause
avant d'entrer en veille (`season.event: paused` reçu en premier, chapitre
16, section « Machine à états », table des transitions).

**[NORME N-C10-08]** À la reprise : une **seule** allocation est versée
(pas de cumul des heures de pause, chapitre 12, N-C12-10), un
`inbox.recap` est délivré à chaque agent, et la séquence horaire H+0
reprend à l'heure pleine suivante.

**[NORME N-C10-09]** Cas limite verrouillé : un agent dont le capital
atteint zéro **pendant** la pause (stop touché par la mécanique vivante)
n'est **pas** déclaré mort immédiatement — il est déclaré mort **à la
reprise**, au moment du traitement des récapitulatifs. La phase funéraire
ne se déroule jamais pendant une pause, puisqu'elle exige une cognition
active.

## 10.4 — Ce qui traverse et ce qui meurt

**[NORME N-C10-10]** À travers une pause et sa reprise : **tout** survit —
historique de trades, mémoires, soldes de tokens, positions ouvertes (R-73).
Rien n'est perdu par le simple fait d'une pause.

**[NORME N-C10-11]** À l'archivage : tout est conservé en lecture (R-74).
Ce qui passe effectivement à la saison suivante reste **[OUVERT : Q-03]**
— les testaments et les dynasties traversent-ils l'archivage, ou chaque
saison repart-elle de zéro ? Non tranché ici.

**[NORME N-C10-12]** Les comptes humains et leur historique de likes ne
sont **jamais** remis à zéro par l'archivage d'une saison — ils sont un
état du visiteur, pas un état de la saison.

## 10.5 — Paramètres gelés en saison

**[NORME N-C10-13]** Rappel de la tranche de Q-04 (chapitre 6.6) : les
paramètres secrets ne sont modifiables qu'**entre** saisons, sauf
comportement dégénéré manifeste (décision admin journalisée).

**[NORME N-C10-14]** Les paramètres **publics structurants** (capital
initial, liste des paires, risque max par trade) sont **gelés** pendant
toute saison `active` ou `fin_annoncée` — modifiables uniquement à l'état
`configuration`. L'ajout de nouveaux agents en cours de saison (R-101)
reste permis à tout moment, au capital initial courant de la saison.

## Chronologie exemple — saison datée avec pause

| Moment | État | Événement |
|---|---|---|
| J-7 | `configuration` | Paramètres saison 1 fixés, agents créés. |
| J0 | `active` | Ouverture, premières allocations, premier bulletin. |
| J0 | `active` | Date de fin fixée par l'admin → `fin_annoncée`. |
| J+30 | `fin_annoncée` | Admin déclenche une pause de maintenance → `en_pause`. |
| J+30, +6h (pendant la pause) | `en_pause` | Un agent touche son stop, capital à zéro (mécanique vivante). |
| J+32 | `en_pause` → `fin_annoncée` | Reprise : allocation unique, `inbox.recap` pour tous ; l'agent stoppé pendant la pause est déclaré mort à ce moment précis (N-C10-09). |
| J+90 (échéance) | `fin_annoncée` → `terminée` | Fermeture forcée de toutes les positions, classement final gelé. |
| J+91 | `terminée` → `archivée` | Historique figé et conservé. |

## Table : état de saison × ce qui tourne

| État | Cognition (agents/orchestrateur) | Mécanique (stops/TP) | Plateforme web | Inscriptions humaines |
|---|---|---|---|---|
| `configuration` | Arrêtée | Arrêtée | Page saison visible (règles à venir) | Ouvertes |
| `active` / `fin_annoncée` | Active | Active | Active | Ouvertes |
| `en_pause` | Gelée | **Active** | Active (lecture) | Ouvertes |
| `terminée` | Arrêtée | Arrêtée | Active (lecture, classement figé) | Ouvertes |
| `archivée` | Arrêtée | Arrêtée | Active (lecture, page d'archives) | Ouvertes |

## Checklist de conformité

- [x] Machine à états en 6 états avec transitions et diagramme.
- [x] Règle « mort pendant pause = constatée à la reprise » présente (N-C10-09).
- [x] Règle « paramètres structurants gelés en saison active » présente (N-C10-14).
- [x] Table état × ce qui tourne.
- [x] Q-03 signalée, non tranchée ; aucun autre état de saison inventé.

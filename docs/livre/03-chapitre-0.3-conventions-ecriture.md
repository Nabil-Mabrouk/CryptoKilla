# CHAPITRE 0.3 — Conventions d'écriture

> Registre : gouvernance. Ce chapitre reprend **in extenso** les consignes
> générales qui ont encadré la pré-rédaction de tout le livre (jointes à
> chaque lot de pré-rédaction) — elles deviennent ici une norme du livre
> lui-même, applicable à toute rédaction future (amendements compris).

**[NORME N-C0.3-01]** Les huit consignes suivantes s'appliquent à toute
rédaction ou révision de ce livre :

1. **Tu rédiges, tu n'inventes pas.** Tout ce qui figure sous « DÉCISIONS
   VERROUILLÉES » doit être repris tel quel (reformulation stylistique
   permise, altération du sens interdite). Si une information manque pour
   rédiger, écris `[OUVERT : question précise]` dans le texte — n'improvise
   **jamais** une valeur, un champ, une règle ou un nom.
2. **Aucune valeur numérique inventée.** Toute valeur configurable s'écrit
   `[PARAM: nom_du_parametre]`. Une valeur par défaut peut être proposée
   **uniquement** dans un encadré séparé intitulé « Proposition de défaut
   (à valider) ».
3. **Références croisées obligatoires.** Les règles du document « Règles
   de l'Expérience » se citent par identifiant (R-xx), les questions
   ouvertes par Q-xx. Ne pas réécrire une règle : la citer et la
   développer.
4. **Marqueurs** : `[NORME]` règle testable, `[PARAM]` valeur du registre
   des paramètres, `[LORE]` narratif, `[OUVERT]` question non tranchée.
   Chaque section normative se termine par la liste de ses `[NORME]`
   numérotées (format `N-<chapitre>-<n°>`).
5. **Style** : français technique, précis, sans emphase marketing dans les
   parties normatives. Les exemples chiffrés sont fictifs mais réalistes
   et cohérents entre eux dans tout le chapitre.
6. **Public cible** : des agents IA développeurs. Optimiser pour la
   non-ambiguïté : tables, schémas de champs, énumérations exhaustives,
   cas d'erreur explicites. Chaque interface liste **tous** ses cas
   d'échec.
7. **Cohérence inter-chapitres.** En cas de contradiction apparente entre
   un chapitre et un document fourni, ne pas trancher : signaler
   `[CONFLIT : description]`.
8. **Format de sortie** : Markdown, titres hiérarchisés, une section
   « Checklist de conformité » en fin de chapitre reprenant les critères
   d'achèvement du brief.

## Checklist de conformité

- [x] Les huit consignes reprises intégralement, sans altération de sens, présentées comme normes du livre lui-même.

# Grande Guilde de la Rose des Vents

Babillard de quêtes collaboratif pour une campagne D&D 5.5e de style West Marches sur la Sword Coast.

Site : https://ironyan004mfg.github.io/rose-des-vents/

## Architecture
- **GitHub Pages** héberge `index.html` (HTML, CSS et JavaScript, sans framework).
- **Cloud Firestore** (projet `rose-des-vents-d98df`) contient les données, synchronisées en temps réel :
  - `bureaux/{id}` : les 8 comptoirs
  - `quetes/{id}` : les quêtes (statuts : ouverte, encours, terminee, archivee)
  - `inscriptions/{idQuête}__{uid}` : les demandes des joueurs, séparées des quêtes
  - `admins/{uid}` : les comptes administrateurs (modifiables seulement dans la console Firebase)
  - `aventuriers`, `config` : réservés à la renommée (phase 2)
- **Firebase Authentication** : connexion anonyme (joueurs), Google (DM), courriel/mot de passe (robot de Claude).
- **`firestore.rules`** : toutes les autorisations sont vérifiées côté serveur. À copier dans la console Firebase → Firestore → Règles.

## Supercharged
Aucune limite d'inscriptions. Quand les inscriptions confirmées dépassent le maximum de joueurs recommandé,
la quête passe « Supercharged » (le DM peut aussi le forcer).

## Mode DM
Connexion Google. Créer, modifier, archiver ou supprimer des quêtes, confirmer ou refuser des inscriptions,
ajouter des participants, exporter et importer en JSON (avec aperçu). Le bouton « Migrer les données intégrées »
copie dans Firestore les comptoirs et quêtes d'origine (bloc `bb-seed`) sans jamais écraser ce qui existe déjà.

## Administration par Claude
`tools/rdv_admin.py` se connecte avec le compte robot (`claude@rose-des-vents.local`, mot de passe dans
`RDV_PASSWORD`, jamais dans le dépôt). Les règles Firestore s'appliquent au robot comme à un admin du site.

## Tests
Les règles et le site ont été testés avec les émulateurs Firebase (`?emu=1` branche le site sur les émulateurs locaux).

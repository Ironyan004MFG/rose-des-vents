# Inventaire de référence des têtes

Cette liste est le **gabarit commun à toutes les races**. Chaque race a exactement les mêmes 46 cases, avec les mêmes identifiants et les mêmes rôles, donc le même nombre de têtes par catégorie.

**Ce qui est commun : la case (numéro, identifiant, rôle, coiffe du métier). Ce qui change : la coiffure, la pilosité et les traits, adaptés à la race** pour qu'on la reconnaisse en un clin d'œil. Les descriptions ci-dessous sont celles du NAIN ; pour une autre race, la case « villageois n° 4 » est une autre coiffure, mais c'est toujours le villageois n° 4. Les coiffes de métier (toque, béret, capuche, casque, chapeau de paille…) restent les mêmes d'une race à l'autre.

Traits par race :
- **nain** : barbes fournies, tresses, anneaux, oreilles rondes, visage large ;
- **halfelin** : imberbe ou favoris, cheveux bouclés, visage rond et jeune, joues pleines, petites oreilles légèrement pointues ;
- autres races : à définir au moment de leurs lots.

- **Identifiant** : nom stable, sans la race. Le fichier d'une race s'appelle `<race>/tete/<identifiant>.png`.
- **Génération** : 2/3 d'hommes, 1/3 de femmes.
- **Hauteur** : nain et halfelin, sourcils sur la ligne des épaules ; humain, elfe, tieffelin, les yeux ; demi-orc, le nez.

## Hommes — villageois (9)

| N° | Identifiant | Coiffure du nain |
|---|---|---|
| 1 | `m_v_01` | cheveux tressés, barbe tressée à anneau (tête d'origine) |
| 2 | `m_v_02` | chauve, grosse barbe carrée |
| 3 | `m_v_03` | cheveux en brosse, barbe courte |
| 4 | `m_v_04` | queue de cheval, grande moustache, menton rasé |
| 5 | `m_v_05` | cheveux longs, barbe à deux tresses |
| 6 | `m_v_06` | cheveux bouclés, visage rasé |
| 7 | `m_v_07` | crête, côtés rasés, barbe en pointe |
| 8 | `m_v_08` | dégarni, favoris, menton rasé |
| 9 | `m_v_09` | chignon haut, barbe à trois anneaux |

## Hommes — métiers et nobles (17)

| N° | Identifiant | Métier | Description |
|---|---|---|---|
| 10 | `m_s_capuche` | voyageur, mage | capuche, barbe |
| 11 | `m_s_grand_chapeau` | voyageur, colporteur | chapeau à large bord |
| 12 | `m_s_toque` | cuisinier | toque de cuisinier |
| 13 | `m_s_moine` | moine | tonsure, visage rasé |
| 14 | `m_s_noble_toque` | noble | toque de velours à plume, barbe courte |
| 15 | `m_s_noble_cercle` | noble | cercle de métal, barbe en pointe |
| 16 | `m_s_noble_chapeau` | noble | chapeau à broche, moustache et barbiche |
| 17 | `m_s_marin` | marin, pêcheur | bonnet de laine, barbe drue |
| 18 | `m_s_erudit` | érudit | calotte, lunettes, longue barbe |
| 19 | `m_s_forgeron` | forgeron | bandeau de cuir, moustache et favoris |
| 20 | `m_s_barde` | barde | béret à plume, moustache fine |
| 21 | `m_s_rodeur` | rôdeur, druide | capuche, barbe courte |
| 22 | `m_s_roublard` | roublard | capuche et foulard, yeux seuls visibles |
| 23 | `m_s_fermier` | fermier | chapeau de paille |
| 24 | `m_s_druide` | druide | couronne de feuilles, longue barbe |
| 25 | `m_s_mineur` | mineur | calotte de cuir à mentonnière, moustache |
| 26 | `m_s_mendiant` | mendiant | bonnet rapiécé, barbe hirsute |

## Hommes — casques (7)

| N° | Identifiant | Porteur | Description |
|---|---|---|---|
| 27 | `m_c_garde` | gardes uniquement | casque à nasal |
| 28 | `m_c_heaume_barbe` | paladin, guerrier | grand heaume, barbe |
| 29 | `m_c_heaume` | paladin, guerrier | grand heaume, sans barbe |
| 30 | `m_c_barbute_barbe` | guerrier | barbute, barbe |
| 31 | `m_c_barbute` | guerrier | barbute, visage rasé |
| 32 | `m_c_cerveliere_barbe` | clerc | cervelière à camail, barbe |
| 33 | `m_c_cerveliere` | clerc | cervelière à camail, visage rasé |

## Femmes (13)

| N° | Identifiant | Rôle | Description |
|---|---|---|---|
| 34 | `f_v_fichu` | villageoise, serveuse | tresse en couronne, fichu |
| 35 | `f_v_nattes` | villageoise | deux longues nattes |
| 36 | `f_v_chignon` | villageoise | gros chignon, mèches libres |
| 37 | `f_v_agee` | villageoise âgée | bonnet de laine, rides |
| 38 | `f_s_erudite` | érudite | chignon strict, calotte, lunettes |
| 39 | `f_s_marchande` | marchande | turban à broche |
| 40 | `f_s_barde` | barde | cheveux ondulés, béret à plume |
| 41 | `f_s_capuche` | rôdeuse, roublarde, druidesse | capuche, mèche sur le front |
| 42 | `f_s_fermiere` | fermière | chapeau de paille, tresse de côté |
| 43 | `f_n_diademe` | noble | chignon sous résille, diadème à pierre |
| 44 | `f_n_tresses` | noble | tresses, épingles à fleur de lys |
| 45 | `f_n_perles` | noble | chaînes de perles |
| 46 | `f_c_cerveliere` | clerc | cervelière à camail |

## Récapitulatif

| Catégorie | Nombre |
|---|---|
| Hommes, villageois | 9 |
| Hommes, métiers et nobles | 17 |
| Hommes, casques | 7 |
| Femmes | 13 |
| **Total** | **46** |

## Correspondance avec les fichiers du nain

Les fichiers du nain gardent pour l'instant leurs noms d'origine (`nain/tete/` et `nain/tete/lot1` à `lot4`). Ils seront renommés selon ces identifiants au moment de brancher le générateur. Correspondance : n° 1 = `head_fix` ; 2 à 9 = `lot1` ; 10 = `head_hood` ; 11 = `head_widehat` ; 12 = `head_toque` ; 13 à 20 = `lot2` ; 21 à 26 = `lot4` ; 27 = `head_helm` ; 28 et 29 = `head_greathelm` et `_sans_barbe` ; 30 et 31 = `head_barbute` et `_rasee` ; 32 et 33 = `head_coif` et `_rasee` ; 34 = `head_naine` ; 35 à 42 = `lot3` ; 43 à 45 = `head_dame_*` ; 46 = `head_coif_femme`.

## Plan des lots pour une nouvelle race

Six planches de 8 (grille 4 x 2), chacune suivie de son calque de matières :

| Lot | Têtes |
|---|---|
| A | n° 1 à 8 |
| B | n° 9 à 16 |
| C | n° 17 à 24 |
| D | n° 25, 26, puis casques 27 à 32 |
| E | n° 33, puis femmes 34 à 40 |
| F | n° 41 à 46 (planche de 6) |

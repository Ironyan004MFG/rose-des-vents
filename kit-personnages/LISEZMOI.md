# Kit de personnages — Rose des Vents (travail en cours)

Sauvegarde des pièces validées du générateur de personnages. **Rien ici n'est encore utilisé par l'app** (`index.html` n'y fait pas référence).

## Principe
- Les dessins viennent de GPT, en gris neutre, au trait de contour foncé, vus en plongée (≈ 85°), devant vers le bas.
- Un personnage = jambes (ou bottes) + **corps complet** (torse, bras, mains, objet tenu — une image par pose) + **tête complète** (visage, oreilles, coiffure, barbe).
- Les masques de matières et la teinte sont faits par le code (`outils/`), pas par GPT.

## Contenu
- `nain/tete/` : tête tressée d'origine, version aux oreilles repeintes (`head_fix.png`) et sa carte de matières (`head_fix_matieres.png` : valeur ÷ 20 → 1 peau, 2 cheveux, 3 barbe, 4 métal).
- `nain/corps/` : robe de mage en 7 poses (relaxed, reach, carry_plate, walk_1 à 4), manteau court (relaxed), aventurier validé (relaxed). Images 1254 × 1254.
- `nain/jambes/` : jambes en pantalon avec bottes (pour les tenues courtes) et bottes seules (pour la robe).
- `objets/` : assiette pleine/vide, livre, plume, fourche, pioche, poignée de charrette.
- `outils/` : scripts Python du banc d'essai (recalage par le col, masques automatiques, teinte, assemblage, marche). Ils viennent tels quels de l'espace de travail : **les chemins sont à adapter** avant de les relancer.

## Réglages d'assemblage (toile 512 × 512)
- Corps 1254 px : recalé sur le col (`norm.py`), puis échelle 0,29, cou posé à (256, 229).
- Tête : posée à (0,0), par-dessus tout ; l'objet tenu à deux mains repasse devant la barbe.
- Bottes sous la robe : décalées de 60 px vers le bas. Jambes : même recalage que le corps.

## À faire
- Poses de l'aventurier (main tendue, assiette, marche), puis les autres classes et morphologies.
- Nettoyage des petits défauts de masques (liseré, cuir).
- Intégration dans les bureaux.

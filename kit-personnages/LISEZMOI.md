# Kit de personnages — Rose des Vents (travail en cours)

Sauvegarde des pièces validées du générateur de personnages. **Rien ici n'est encore utilisé par l'app** (`index.html` n'y fait pas référence).

## Principe
- Les dessins viennent de GPT, en gris neutre, au trait de contour foncé, vus en plongée (≈ 85°), devant vers le bas.
- Un personnage = jambes (ou bottes) + **corps complet** (torse, bras, mains, objet tenu — une image par pose) + **tête complète** (visage, oreilles, coiffure, barbe).
- Les masques de matières et la teinte sont faits par le code (`outils/`), pas par GPT.

## Contenu
- `nain/tete/` : tête tressée d'origine, version aux oreilles repeintes (`head_fix.png`) et sa carte de matières (`head_fix_matieres.png` : valeur ÷ 20 → 1 peau, 2 cheveux, 3 barbe, 4 métal).
- `nain/corps/<tenue>/` : un dossier par tenue, une image 1254 × 1254 par pose. **On n'y dépose que les images validées au montage.**
  - `mage/` : robe à liseré — relaxed, reach, carry_plate, walk_1 à walk_4.
  - `aventurier/` : manteau court, épaulettes et ceinture de cuir — relaxed, reach, carry_plate, walk_1, walk_3. La marche alterne walk_1 → relaxed → walk_3 → relaxed.
  - `fermier/` : chemise aux manches roulées, salopette rapiécée, corde — relaxed, reach, carry (panier de légumes), walk_1, walk_3. Matières séparées par leur gris (`outils/far.py`) ; les poses reprennent les matières du torse de relaxed, identique au pixel près. Le panier et ses légumes ont leurs masques tracés à la main (`far.basket`) et repassent devant la barbe au montage. Fourche : fork_relaxed (dessin GPT), fork_walk_1 et fork_walk_3 assemblés ici (côté fourche de fork_relaxed + bras libre des marches validées, couture fondue dans la salopette) ; masques dans `far.fork`. Longe : lead (bras de GPT nettoyé — damier peint et frange blanche retirés — greffé sur relaxed), lead_walk_1, lead_walk_3 et fork_lead assemblés ici ; masques dans `far.lead`. La longe elle-même est dessinée en code (`outils/rope.py`, largeur 8 px à l'échelle du personnage) à partir du bout de corde qui dépasse du poing. Travail aux champs : fork_work (dessin GPT remis à l'échelle du fermier validé, toile 1254 × 1700 car la fourche dépasse vers le bas ; torse redessiné, donc pas identique au pixel près) ; masques dans `far.work`, bras et fourche repassent devant la barbe, mouvement de va-et-vient fait en code.
  - `manteau_court/` : première version, à gros plis — relaxed (gardée pour référence).
- `nain/jambes/` : jambes en pantalon avec bottes (pour les tenues courtes) et bottes seules (pour la robe).
- `objets/` : assiette pleine/vide, livre, plume, fourche, pioche, poignée de charrette.
- `outils/` : scripts Python du banc d'essai (recalage par le col, masques automatiques, teinte, assemblage, marche). Ils viennent tels quels de l'espace de travail : **les chemins sont à adapter** avant de les relancer.

## Réglages d'assemblage (toile 512 × 512)
- Corps 1254 px : recalé sur le col (`norm.py`), puis échelle 0,29, cou posé à (256, 229).
- Tête : posée à (0,0), par-dessus tout ; l'objet tenu à deux mains repasse devant la barbe.
- Bottes sous la robe : décalées de 60 px vers le bas. Jambes : même recalage que le corps.

## À faire
- Les autres classes, puis les autres morphologies.
- Nettoyage des petits défauts de masques (liseré, cuir).
- Intégration dans les bureaux.

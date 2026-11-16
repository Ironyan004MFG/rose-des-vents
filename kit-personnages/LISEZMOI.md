# Kit de personnages — Rose des Vents (travail en cours)

Sauvegarde des pièces validées du générateur de personnages. **Rien ici n'est encore utilisé par l'app** (`index.html` n'y fait pas référence).

## Principe
- Les dessins viennent de GPT, en gris neutre, au trait de contour foncé, vus en plongée (≈ 85°), devant vers le bas.
- Un personnage = jambes (ou bottes) + **corps complet** (torse, bras, mains, objet tenu — une image par pose) + **tête complète** (visage, oreilles, coiffure, barbe).
- Les masques de matières et la teinte sont faits par le code (`outils/`), pas par GPT.

## Contenu
- `nain/tete/` : tête tressée d'origine, version aux oreilles repeintes (`head_fix.png`) et sa carte de matières (`head_fix_matieres.png` : valeur ÷ 20 → 1 peau, 2 cheveux, 3 barbe, 4 métal). Capuche : `head_dwarf_hood_90.png` (dessin GPT), `head_hood.png` (remise à l'échelle de la tête validée, repère : bout du nez) et `head_hood_matieres.png` (valeur ÷ 20 → 1 peau, 2 sourcils, 3 barbe, 4 métal, 8 tissu de la capuche) ; `outils/heads.py`. Elle se pose sur tous les corps : pèlerin et veilleur (robe de mage), chasseur (aventurier). Grand chapeau : `head_dwarf_widehat_90.png`, `head_widehat.png`, `head_widehat_matieres.png` (6 = cordelette, 8 = feutre), calé sur le bout de la barbe ; pour le berger et le colporteur. Sous ce chapeau, le manche tenu (fourche, bâton) reste sous le bord. Le bâton est fabriqué en code à partir d'une pose à la fourche (`far.staff` : dents retirées, bout arrondi). Casque : `head_dwarf_helm_90.png`, `head_helm.png`, `head_helm_matieres.png` (4 = métal du casque et bague de barbe), pour le garde ; son métal prend la teinte de l'armure.
- `nain/corps/<tenue>/` : un dossier par tenue, une image 1254 × 1254 par pose. **On n'y dépose que les images validées au montage.**
  - `mage/` : robe à liseré — relaxed, reach, carry_plate, walk_1 à walk_4.
  - `aventurier/` : manteau court, épaulettes et ceinture de cuir — relaxed, reach, carry_plate, walk_1, walk_3. La marche alterne walk_1 → relaxed → walk_3 → relaxed.
  - `fermier/` : chemise aux manches roulées, salopette rapiécée, corde — relaxed, reach, carry (panier de légumes), walk_1, walk_3. Matières séparées par leur gris (`outils/far.py`) ; les poses reprennent les matières du torse de relaxed, identique au pixel près. Le panier et ses légumes ont leurs masques tracés à la main (`far.basket`) et repassent devant la barbe au montage. Fourche : fork_relaxed (dessin GPT), fork_walk_1 et fork_walk_3 assemblés ici (côté fourche de fork_relaxed + bras libre des marches validées, couture fondue dans la salopette) ; masques dans `far.fork`. Longe : lead (bras de GPT nettoyé — damier peint et frange blanche retirés — greffé sur relaxed), lead_walk_1, lead_walk_3 et fork_lead assemblés ici ; masques dans `far.lead`. La longe elle-même est dessinée en code (`outils/rope.py`, largeur 8 px à l'échelle du personnage) à partir du bout de corde qui dépasse du poing. Travail aux champs : fork_work (dessin GPT remis à l'échelle du fermier validé, toile 1254 × 1700 car la fourche dépasse vers le bas ; torse redessiné, donc pas identique au pixel près) ; masques dans `far.work`, bras et fourche repassent devant la barbe, mouvement de va-et-vient fait en code.
  - `garde/` : tabard (couleur de faction) et sa bordure (couleur secondaire), épaulières, brassards et gantelets de métal, cotte de mailles, ceinture — relaxed, walk_1 (dessin GPT), walk_3 (walk_1 retournée en miroir, bande centrale du torse gardée telle quelle pour la boucle de ceinture). Pose « main qui tient » : grip (dessin GPT : le poing de gauche serre un bout de manche), grip_walk_1 et grip_walk_3 assemblées ici (côté du poing de grip + bras libre des marches). Aucune peau. Matières dans `outils/grd.py` : 4 métal, 5 tabard, 9 bordure (encolure et bas), 15 cotte de mailles (reconnue à sa texture d'anneaux), 16 vêtement sombre sous le tabard, 6 ceinture.
  - `manteau_court/` : première version, à gros plis — relaxed (gardée pour référence).
- `nain/jambes/` : jambes en pantalon avec bottes (pour les tenues courtes) et bottes seules (pour la robe).
- `objets/` : assiette pleine/vide, livre, plume, fourche, pioche, poignée de charrette.
- Boucliers (`objets/item_shield_heater.png` écu, `item_shield_round.png` rond, `item_shield_pavise.png` pavois, plus long) : dessinés bien de face ; `outils/shields.py` sépare le métal (4) de la face (5, couleur de faction), puis pose le bouclier DEVANT le personnage, grand et incliné, par-dessus l'avant-bras (réglages validés dans `FRONT`). Aucune pose spéciale : le bouclier cache le bras.
- `outils/` : scripts Python du banc d'essai (recalage par le col, masques automatiques, teinte, assemblage, marche). Ils viennent tels quels de l'espace de travail : **les chemins sont à adapter** avant de les relancer.

## Réglages d'assemblage (toile 512 × 512)
- Corps 1254 px : recalé sur le col (`norm.py`), puis échelle 0,29, cou posé à (256, 229).
- Tête : posée à (0,0), par-dessus tout ; l'objet tenu à deux mains repasse devant la barbe.
- Bottes sous la robe : décalées de 60 px vers le bas. Jambes : même recalage que le corps.

## À faire
- Les autres classes, puis les autres morphologies.
- Nettoyage des petits défauts de masques (liseré, cuir).
- Intégration dans les bureaux.

- Armes (`objets/item_spear.png` lance, `item_halberd.png` hallebarde, `item_axe.png` hache, `item_mace.png` masse, `item_sword.png` épée) : dessinées à part, verticales, sur fond blanc (retiré en code). `outils/weapons.py` sépare métal (4), bois (28) et cuir (6), cale la taille sur l'épaisseur du manche et glisse l'arme dans le poing de la pose grip ; les doigts du gantelet repassent par-dessus. La hache est retournée pour que sa lame soit vers l'extérieur ; la hallebarde garde sa lame vers l'intérieur. La lance et la hallebarde (armes d'allonge) ont la hampe allongée en code, sans déformer la pointe.
- Emblèmes de faction : dessinés en code, simplifiés (`outils/emblems.py` : 11 emblèmes et la liste validée `GARDES` des 15 gardes par région, avec leurs couleurs ; aperçu dans `planches/`). Posés au centre de l'écu et du pavois (jamais sur le bouclier rond, qui garde son umbo) et sur la poitrine du tabard, centré entre la barbe et la ceinture (réglage validé : `CHEST=(257,358)`, `CHEST_SIZE=84`) : l'emblème est dessiné AVANT la tête, donc la barbe (et la ceinture) passent par-dessus (`grd.char(..., emb=…)`, `CHEST`, `CHEST_SIZE`). Les gardes sont ceux de la faction de la région (Poing Enflammé à Baldur's Gate…) ; la Guilde n'emploie pas de gardes.

## Gardes par région (liste validée)

Une région peut avoir plusieurs gardes. L'Église de Lathandre n'est pas une garde : son emblème servira aux clercs et paladins.

| Région | Garde | Tabard / bordure | Emblème |
|---|---|---|---|
| Baldur's Gate | Poing Enflammé | rouge / acier | poing dans les flammes (lore) |
| Baldur's Gate | Guet de la Haute-Ville | bleu nuit / or | porte à herse (inventé) |
| Neverwinter | Garde de Neverwinter | bleu / argent | trois flocons et volute (lore) |
| Neverwinter | Veilleurs de Wintershield | bleu pâle / blanc | un grand flocon (inventé) |
| Waterdeep | Guet de la Cité | vert / or | croissant de lune sur l'eau (inventé) |
| Waterdeep | Garde de la Cité | noir / or | tour crénelée (inventé) |
| Triboar | Les Douze | rouge sang / noir | hure de sanglier (lore) |
| Mirabar | La Hache de Mirabar | noir / rouille | hache double dressée (lore) |
| Silverymoon | Chevaliers d'Argent | bleu roi / argent | croissant et étoile (lore) |
| Daggerford | Milice de Daggerford | bleu profond / argent | dague ensanglantée (lore) |
| Luskan | Nefs Kurth, Baram, Suljack, Taerl, Rethnor | marine, bordeaux, vert, ardoise, noir / blanc cassé | ancre (inventé) |

## Objets de la carte

`objets/item_lantern.png`, `item_bow.png`, `item_quiver.png`, `item_bundle.png`, `item_woodaxe.png` : dessins isolés sur fond blanc (retiré en code), matières et teintes dans `outils/items.py`, montages dans `outils/carte.py`.

- **Chasseur (validé)** : aventurier + capuche ; arc en travers du dos et carquois derrière l'autre épaule (`carte.chasseur`), aperçu dans `planches/chasseur.png`. Aucune main ne tient l'arc : les essais de « main qui tient l'arc » (greffe ou dessin GPT) ont été abandonnés.
- **Colporteur (ballot validé)** : aventurier + ballot dans le dos (`carte.colporteur`, hauteur 150). Sous le grand chapeau, seule la couverture roulée dépasse ; avec une autre tête, on voit tout le ballot.
- **Bûcheron (validé)** : fermier, pose à la fourche, où tout l'outil est remplacé par la hache de bûcheron (`carte.axe_farmer`), glissée sous les doigts. La hache d'armes du garde (`item_axe.png`) reste disponible en variante.
- **Lanterne (validée)** : `objets/hand_lantern.png` est un poing fermé sur l'anse d'une lanterne, dessiné seul par GPT (sans bracelet ni manche). `outils/advlant4.py` le pose au bout du bras tendu de la pose « reach » : la main ouverte est retirée d'après ses matières, le haut du poing glisse sous le bracelet, et sous le bord du bracelet le poing et la lanterne sont au premier plan (devant le manteau). Réglage validé : échelle 0,56, la main remplit la largeur de la manche sans dépasser le bracelet. Résultat : `nain/corps/aventurier/body_dwarf_adventurer_reach_lantern.png` (toile plus haute, la lanterne descend sous le cadre habituel), aperçu dans `planches/lanterne.png`. Les essais de greffe d'une main dessinée avec son bracelet ont échoué (jonction difforme) : toujours demander la main SEULE.
- **Veilleur (validé)** : mage, bras tendu, lanterne en main nue — `nain/corps/mage/body_dwarf_robe_reach_lantern.png`, aperçu `planches/veilleur.png`. Fait par `outils/lanterne.py` (`graft2`, `veilleur`), la méthode à réutiliser pour toute main posée sous un bracelet : le poing prend exactement la largeur du bracelet et se centre dessous ; il remonte jusqu'à remplir l'ouverture ; ordre des couches vêtement < poing et lanterne < bracelet ; les encoches du bord du bracelet sont fermées (sinon la main « traverse » le métal) ; l'ancienne main est retirée avec son trait et le vêtement rebouché. Le poing ne pivote jamais (il s'efface à moitié).
- **Patrouille de nuit** : `nain/corps/garde/body_dwarf_guard_reach_lantern.png` = l'image COMPLÈTE dessinée par GPT (garde, bras tendu, gantelet et lanterne d'un seul tenant), simplement remise à l'échelle du garde validé (`lanterne.garde_reach`). Son torse diffère un peu du garde validé (gorgerin plus simple, bordure seulement en bas). L'essai de ne garder que le bras sur le torse validé (`garde_reach2`) laissait une coche dans le bras : abandonné. Aperçu `planches/patrouille_de_nuit.png`.

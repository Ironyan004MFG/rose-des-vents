"""Quelles têtes vont sur quels corps (règle de Yannick : générer les bonnes têtes sur les bons corps, jamais une tête casquée sur une robe).
Identifiants de têtes = ceux d'INVENTAIRE.md, communs à toutes les races. Corps = tenues du kit."""
CIVIL=('fermier','pourpoint','aventurier')
GENERIQUE=('aventurier','mage','fermier','plates','barbare','forgeron','cuisinier','pourpoint')
GENERIQUE_F=('serveuse','robe','fermier','aventurier','mage','plates')
# corps UNISEXES : portés par une femme, ils sont resserrés de 10 % en largeur
UNISEXE=('aventurier','mage','fermier','garde','plates')
# équivalents féminins : cuisinier -> serveuse ; pourpoint -> robe. Barbare et forgeron : hommes seulement (torse nu), pas d'équivalent pour l'instant.
EQUIV_F={'cuisinier':'serveuse','pourpoint':'robe'};HOMMES=('barbare','forgeron','cuisinier','pourpoint');FEMMES=('serveuse','robe');SERRE_F=.9
TETES={
 # têtes GÉNÉRIQUES : sur n'importe quel corps (un métier « sans » son chapeau), sauf le garde, qui est TOUJOURS casqué
 **{f'm_v_{i:02d}':GENERIQUE for i in range(1,10)},
 'm_s_capuche':('aventurier','mage'),'m_s_grand_chapeau':CIVIL,'m_s_toque':('cuisinier',),'m_s_moine':('pourpoint','mage'),
 # nobles : seulement sur le corps de noble (pourpoint, robe) ; jamais sur un forgeron, un fermier ou un aventurier
 'm_s_noble_toque':('pourpoint',),'m_s_noble_cercle':('pourpoint',),'m_s_noble_chapeau':('pourpoint',),
 'm_s_marin':CIVIL,'m_s_erudit':('mage','pourpoint'),'m_s_forgeron':('forgeron','barbare'),'m_s_barde':('pourpoint',),
 'm_s_rodeur':('aventurier',),'m_s_roublard':('aventurier',),'m_s_fermier':('fermier',),'m_s_druide':('mage',),
 'm_s_mineur':('fermier','forgeron','aventurier'),'m_s_mendiant':('fermier',),
 # casques : gardes et armures seulement ; les PETITS casques (nasal, barbute) vont aussi sur l'aventurier
 'm_c_garde':('garde','plates','aventurier'),'m_c_barbute':('garde','plates','aventurier'),'m_c_barbute_barbe':('garde','plates','aventurier'),
 'm_c_heaume':('plates','garde'),'m_c_heaume_barbe':('plates','garde'),'m_c_cerveliere':('garde','plates'),'m_c_cerveliere_barbe':('garde','plates'),
 # femmes : jamais sur un corps d'homme
 'f_v_fichu':GENERIQUE_F,'f_v_nattes':GENERIQUE_F,'f_v_chignon':GENERIQUE_F,'f_v_agee':GENERIQUE_F,
 'f_s_erudite':('robe','mage'),'f_s_marchande':('robe','serveuse'),'f_s_barde':('robe',),'f_s_capuche':('aventurier',),'f_s_fermiere':('fermier',),
 'f_n_diademe':('robe',),'f_n_tresses':('robe',),'f_n_perles':('robe',),'f_c_cerveliere':('garde','plates'),
}
CORPS=('aventurier','mage','fermier','garde','plates','barbare','forgeron','cuisinier','serveuse','pourpoint','robe')
def corps_pour(tete): return TETES[tete]
def tetes_pour(corps): return [t for t,c in TETES.items() if corps in c]
if __name__=='__main__':
    assert len(TETES)==46,len(TETES)
    for c in CORPS: print(f'{c:11s}{len(tetes_pour(c)):3d}  '+', '.join(tetes_pour(c)))

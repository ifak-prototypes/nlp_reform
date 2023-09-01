from typing import List

import streamlit as st

from nlp_reform.dto import Version, Relation, DecompResult
from nlp_reform.translate import translate
from nlp_reform_pos_dep.pos_dep import PosDepReform
from nlp_reform_sem_sim.modules.decompose_req import add_conditions_conjunctions
from nlp_reform_sem_sim.sem_sim import SemSimReform
from nlp_reform_srl.srl_based import SrlReform
from ui.ui import ReformUI

st.set_page_config(page_title='Re-Form',
                   # page_icon="data/logo_white.svg",
                   layout='centered',
                   )


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()),
                    unsafe_allow_html=True)


local_css("ui/css/style.css")


def main():
    ui = ReformUI(st=st)
    ui.add_sidebar()
    ui.write_title()
    if ui.version == Version.POS_DEP:
        ui.input_requirement()
        reform = PosDepReform()
    elif ui.version == Version.SRL:
        ui.input_requirement()
        reform = SrlReform()
    elif ui.version == Version.SEM_SIM:
        ui.input_requirement_sem_sim()
        reform = SemSimReform()
    else:
        raise Exception('Invalid version chosen!')

    if ui.req:
        decomp: DecompResult = reform.decomp_req(ui.req)

        relations: List[Relation] = []
        for idx, clause in enumerate(decomp.clauses):
            relation: Relation = reform.parse_relation(clause)
            ui.display_relation_elements(idx, relation)
            relations.append(relation)

        structure = translate(relations=relations,
                              conjunctions=decomp.conjunctions
                              )
        ui.display_full_relation(structure)


if __name__ == "__main__":
    main()

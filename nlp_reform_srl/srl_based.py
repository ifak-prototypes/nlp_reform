from typing import List

from nlp_reform.dto import Relation, DecompResult, Clause
from nlp_reform.reform import Reform
from nlp_reform_sem_sim.modules.decompose_req import add_conditions_conjunctions
from nlp_reform_srl.modules.srl_frames import SemFrames
from nlp_reform_srl.modules.map_frames_to_relation import *
from util import pre_process_req

sem_frames = SemFrames()


class SrlReform(Reform):

    def parse_relation(self, clause: Clause) -> Relation:
        srl_frames = get_srl_frames(clause.text, sem_frames)
        if clause.condition:
            is_guard = True
            condition_value = clause.condition
        else:
            is_guard, condition_value = check_if_guard(clause.text)
        relation = map_frame_to_relation(srl_frames, clause.text, condition_value, is_guard)

        return relation

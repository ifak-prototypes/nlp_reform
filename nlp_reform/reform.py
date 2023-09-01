from abc import ABC, abstractmethod
from typing import List

from nlp_reform.dto import Relation, DecompResult
from util import pre_process_req, decompose_req, resolve_pronouns


class Reform(ABC):

    def decomp_req(self, req: str) -> DecompResult:
        # pre-process the requirement
        og_clause = []
        req_ = pre_process_req.clean_newlines(req)
        req_, events = pre_process_req.process_events_in_quotes(req_)
        # decompose newlines as clauses
        decomp_nl = decompose_req.decompose_newlines(req_)
        # decompose conditions
        decomp_cond = []
        for decomp in decomp_nl:
            decomp_cond.extend(decompose_req.decompose_conditions(decomp))
        # decompose conjunctions
        decomp_conj = []
        for decomp in decomp_cond:
            print(decomp)
            decomp = resolve_pronouns.resolve_pronouns(decomp)
            decomp = decompose_req.decompose_between(decomp)
            decomp = decompose_req.decompose_NPConj(decomp)
            print(decomp)
            decomp_conj.extend(decompose_req.decompose_conjunctions(decomp))

        for decomp in decomp_cond:
            og_clause.extend(decompose_req.decompose_conjunctions(decomp))

        # replace XX back to event name
        decomp_conj_ = []
        print(events)
        for clause in decomp_conj:
            if 'XX' in clause:
                clause = clause.replace('XX', events[0]).replace('"', '')
            decomp_conj_.append(clause)
        og_clause_ = []
        for clause in og_clause:
            if 'XX' in clause:
                clause = clause.replace('XX', events[0]).replace('"', '')
            og_clause_.append(clause)
        if 'XX' in req_:
            req_ = req_.replace('XX', events[0]).replace('"', '')

        return decompose_req.add_conditions_conjunctions(req_, decomp_conj_, og_clause_)

    @abstractmethod
    def parse_relation(self, sub_req: str) -> Relation:
        pass
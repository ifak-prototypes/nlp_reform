import re
import spacy
from typing import List

from nlp_reform.dto import Relation, Clause, DecompResult, Condition
from nlp_reform.reform import Reform
from nlp_reform_pos_dep.modules.find_comparative_symbol import \
    find_comparative_symbol
from nlp_reform_pos_dep.modules.normalize_req import normalize_req
from nlp_reform_pos_dep.modules.parse_relation import \
    parse_relation_bool_action, parse_relation_comparative, \
    parse_relation_intensive
from nlp_reform_pos_dep.modules.parse_semantics import parse_syntax
from nlp_reform_sem_sim.modules import decompose_req
from nlp_reform_sem_sim.modules.decompose_req import add_conditions_conjunctions
from util.decompose_req import decompose_between


spacy_model = "en_core_web_sm"
nlp = spacy.load(spacy_model)


class PosDepReform(Reform):

    def parse_relation(self, clause: Clause) -> Relation:
        normalized_req = normalize_req(nlp, [clause.text])[0]
        events = re.findall("'.*'", normalized_req)
        for event in events:
            normalized_req = re.sub(event, re.sub('\s', '_', event),
                                    normalized_req)

        comp_symbol = find_comparative_symbol(nlp, normalized_req)
        print(comp_symbol)
        print(normalized_req)
        syntax = parse_syntax(nlp, normalized_req)

        relation = Relation()
        doc = nlp(normalized_req)
        if comp_symbol == "":
            relation = parse_relation_bool_action(doc, syntax, clause.condition)
        if comp_symbol != "":
            if 'Intensive' in syntax.verb_type and comp_symbol != '=':
                relation = parse_relation_intensive(doc, syntax)
            else:
                relation = parse_relation_comparative(nlp, normalized_req,
                                                      syntax, comp_symbol)

        relation.syntax = syntax
        relation.clause = clause.text
        if clause.condition:
            relation.condition = clause.condition
        else:
            relation.condition = 'then'
        return relation

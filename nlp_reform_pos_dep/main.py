import re

from nlp_reform_v1.modules.get_req_from_file import get_req_from_file
from nlp_reform_v1.modules.normalize_req import normalize_req
from nlp_reform_v1.modules.parse_relation import parse_relation_comparative, parse_relation_bool_action, \
    parse_relation_intensive
from nlp_reform_v1.modules.parse_semantics import parse_syntax
from util import decompose_req
from util.comparative_symbol import find_comparative_symbol
# from nlp_reform_v1.modules.find_comparative_symbol import find_comparative_symbol
# from nlp_reform_pipeline.modules import decompose_req
from nlp_reform_v1.definitions import Relations, Relation

import pandas as pd

import spacy
spacy_model = "en_core_web_sm"
nlp = spacy.load(spacy_model)


def decomp_req(req):
    decomp_nl = decompose_req.decompose_newlines(req)
    # decompose conditions
    decomp_cond = []
    for decomp in decomp_nl:
        decomp_cond.extend(decompose_req.decompose_conditions(decomp))
    # decompose conjunctions
    decomp_conj = []
    for decomp in decomp_cond:
        decomp_conj.extend(decompose_req.decompose_conjunctions(decomp))

    decomp_req = decomp_conj

    return decomp_req


def parse_relation(sub_req):
    normalized_req = normalize_req(nlp, [sub_req])[0]
    events = re.findall("'.*'", normalized_req)
    for event in events:
        normalized_req = re.sub(event, re.sub('\s', '_', event), normalized_req)

    comp_symbol = find_comparative_symbol(nlp, normalized_req)
    syntax = parse_syntax(nlp, normalized_req)

    relation = Relation()
    doc = nlp(normalized_req)
    if comp_symbol == "":
        relation = parse_relation_bool_action(doc, syntax)
    if comp_symbol != "":
        if 'Intensive' in syntax.verb_type and comp_symbol != '=':
            relation = parse_relation_intensive(doc, syntax)
        else:
            relation = parse_relation_comparative(nlp, normalized_req, syntax, comp_symbol)

    relation.syntax = syntax
    relation.clause = sub_req

    return relation


def get_relation(req):
    relations = []
    # decompose newlines as clauses
    decomp_nl = decompose_req.decompose_newlines(req)
    # decompose conditions
    decomp_cond = []
    for decomp in decomp_nl:
        decomp_cond.extend(decompose_req.decompose_conditions(decomp))
    # decompose conjunctions
    decomp_conj = []
    for decomp in decomp_cond:
        decomp_conj.extend(decompose_req.decompose_conjunctions(decomp))

    decomp_req = decomp_conj

    for sub_req in decomp_req:
        normalized_req = normalize_req(nlp, [sub_req])[0]
        events = re.findall("'.*'", normalized_req)
        for event in events:
            normalized_req = re.sub(event, re.sub('\s', '_', event), normalized_req)

        comp_symbol = find_comparative_symbol(nlp, normalized_req)
        syntax = parse_syntax(nlp, normalized_req)

        doc = nlp(normalized_req)
        if comp_symbol == "":
            relation = parse_relation_bool_action(doc, syntax)
        if comp_symbol != "":
            if 'Intensive' in syntax.verb_type and comp_symbol != '=':
                relation = parse_relation_intensive(doc, syntax)
            else:
                relation = parse_relation_comparative(nlp, normalized_req, syntax, comp_symbol)

        relation.clause = sub_req
        relations.append(relation)

    return Relations(relations=relations, req=req)


def main():
    reqs = get_req_from_file('data/input/req.txt')

    output = []
    for req in reqs[:2]:
        all_relations = get_relation(req)
        print(all_relations.req)
        output.append(
            {
                'req': all_relations.req
            }
        )
        for relation in all_relations.relations:
            print(relation.clause)
            print(relation)
            print(relation.get_text())
            print()
            output.append(
                {
                    'req': relation.clause,
                    'details': relation,
                    'relation': relation.get_text()
                }
            )
        print('-----------\n')

    df = pd.DataFrame(output)

    writer = pd.ExcelWriter("output.xlsx", engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    workbook = writer.book
    workbook_format = workbook.add_format({'text_wrap': True})
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column(1, 1, 40, workbook_format)
    worksheet.set_column(2, 2, 45, workbook_format)
    worksheet.set_column(3, 3, 60, workbook_format)
    writer.save()


if __name__ == '__main__':
    main()

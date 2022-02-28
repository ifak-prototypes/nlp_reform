import os
import xml.etree.ElementTree as ET

from typing import List, Optional, Union
from lib.models import Clause, Operator


def find_comparative_symbol(doc, text, spacy_nlp):
    tokens = []
    for token in spacy_nlp(text):
        tokens.append(token.lemma_)

    comp_symbol = ""

    for child in doc:
        symbol = child.find('comp_symbol').text
        for child_1 in child:
            if child_1.text in tokens:
                comp_symbol = symbol

    return comp_symbol


def detect_operator(
    clause: Clause,
    spacy_nlp,
    op_file_xml
):
    doc = spacy_nlp(clause.text)
    verb_text = ''
    for token in doc:
        if token.tag_ == 'VBZ':
            verb_text = token.text
            string = clause.text.split(" ")
            try:
                index = string.index(verb_text)  # name_
                next_word = string[index + 1]
            except:
                next_word = ''
            verb_text = verb_text + ' ' + next_word

    comp_symbol = find_comparative_symbol(op_file_xml, verb_text, spacy_nlp)

    if comp_symbol == '=':
        return Operator.EqualTo
    elif comp_symbol == '>':
        return Operator.GreaterThan
    elif comp_symbol == '>=':
        return Operator.GreaterThanEqualTo
    elif comp_symbol == '<':
        return Operator.LessThan
    elif comp_symbol == '<=':
        return Operator.LessThanEqualTo
    else:
        return Operator.EqualTo


def load_operator_symbols():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    op_file_xml = os.path.join(script_dir, 'data', 'operator_symbols.xml')
    return ET.parse(op_file_xml).getroot()


def detect_operators(
    clauses: List[Clause],
    spacy_nlp,
    operator_symbols
) -> List[Operator]:
    return [detect_operator(clauses[i], spacy_nlp, operator_symbols) for i in range(len(clauses))]


def detect_operators_static(clauses: List[Clause]):
    return [Operator.EqualTo] * len(clauses)
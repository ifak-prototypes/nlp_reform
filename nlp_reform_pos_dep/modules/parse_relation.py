import re
from spacy.matcher.matcher import Matcher
from nlp_reform.dto import Relation

conditional_clauses = ['if', 'while', 'when', 'until']


# def parse_relation(doc, action_symbol_constraints, subj, obj, verb_type, action_type):
#     relation = ""
#     object = ""
#     advcl = ""
#     nsubj = ""
#     acomp = ""
#
#     action_symbol = "".join(action_symbol_constraints[1])
#     action_constraint = "".join(action_symbol_constraints[2])
#
#     for type in verb_type:
#         if type == "Prepositional":
#             for token in doc:
#                 if token.dep_ == 'ROOT':
#                     for child in token.children:
#                         if child.dep_ == 'dobj':
#                             object = child.text
#                         if child.dep_ == 'advcl':
#                             advcl = child.text
#             relation = object + ' = ' + advcl
#
#         if type == "Dative":
#             for token in doc:
#                 if token.dep_ == 'ROOT':
#                     for child in token.children:
#                         if child.dep_ == 'dobj':
#                             object = child.text
#                         if child.dep_ == 'punct' or child.dep_ == 'pobj':
#                             advcl = child.text
#             if object.strip() and advcl.strip():
#                 relation = object + ' = ' + advcl
#
#         if type == "Intensive":
#             nsubj_1 = ''
#             nsubj_2 = ''
#             for token in doc:
#                 if token.dep_ == 'ROOT':
#                     for child in token.children:
#                         if child.dep_ == 'nsubj':
#                             nsubj_1 = child.text
#                         if child.dep_ == 'acomp' or child.dep_ == 'attr':
#                             acomp = child.text
#             for chunk in doc.noun_chunks:
#                 if chunk.root.dep_ == 'nsubj':
#                     nsubj_2 = re.sub('\\b[a|A]\\b', '', chunk.text).strip()
#                     nsubj_2 = re.sub('\\b[a|A]n\\b', '', nsubj_2).strip()
#                     nsubj_2 = re.sub('\\b[t|T]he\\b', '', nsubj_2).strip()
#                     nsubj_2 = re.sub(' ', '_', nsubj_2)
#
#             if nsubj_2:
#                 nsubj = nsubj_2
#             else:
#                 nsubj = nsubj_1
#
#             relation = nsubj + ' = ' + acomp
#
#     if "Intensive" in verb_type and action_type == 'bool_action':
#         relation = action_symbol + '(' + action_constraint + ')'
#
#     if action_type == 'bool_action':
#         for chunk in doc.noun_chunks:
#             if chunk.root.dep_ == 'nsubj' or chunk.root.dep_ == 'nsubjpass':
#                 subj = re.sub('\\b[a|A]\\b', '', chunk.text).strip()
#                 subj = re.sub('\\b[a|A]n\\b', '', subj).strip()
#                 subj = re.sub('\\b[t|T]he\\b', '', subj).strip()
#                 subj = re.sub(' ', '_', subj)
#                 if action_constraint not in subj:
#                     relation = subj + ': ' + action_constraint + ' == ' + action_symbol
#                 else:
#                     relation = action_constraint + ' == ' + action_symbol
#
#                 if 'Negative' in verb_type:
#                     pos_neg = '!='
#                 else:
#                     pos_neg = '=='
#         else:
#             relation = subj + '==' + action_symbol
#             rel = Relation(left=subj, symbol='==', right=action_symbol)
#
#     if action_type == 'simple_verb':
#         subject = ''
#         subject_ = ''
#         root_verb = ''
#         object = ''
#         actor = ''
#         signal = ''
#         first_object = ''
#         second_object = ''
#         subject_compound = ''
#
#         for token in doc:
#             if token.dep_ == 'ROOT':
#                 root_verb = token.lemma_
#             if token.dep_ == 'dobj' or token.dep_ == 'attr' or token.dep_ == 'acomp':
#                 first_object = token.text
#             if token.dep_ == 'subtok':
#                 second_object = token.text
#             if token.dep_ == 'nsubj':
#                 for child in token.children:
#                     if child.dep_ == 'compound':
#                         subject_compound = child.text + '_'
#                 subject_ = subject_compound + token.text
#                 subject = subject_compound + token.text + ': '
#
#             object = first_object + ' ' + second_object
#             if subject.strip() and object.strip():
#                 if root_verb == 'be':
#                     signals_from_file = dec_det_.signals
#                     for signal_actors in signals_from_file:
#                         if subject_ in signal_actors['name']:
#                             signal = signal_actors['name']
#                             actor = signal_actors['actor']
#                     relation = subject + '= ' + object.strip()
#                 else:
#                     relation = subject + root_verb + '(' + object.strip() + ')'
#
#     if "Transitive" in verb_type or action_type == 'verb_noun':
#         if action_symbol_constraints != [[], [], []]:
#             for action in action_symbol_constraints[0]:
#                 if len(action_symbol_constraints[0]) == len(action_symbol_constraints[1]) \
#                         and len(action_symbol_constraints[0]) == len(action_symbol_constraints[2]):
#                     if action in doc.text:
#                         action_index = action_symbol_constraints[0].index(action)
#                         action_symbol = action_symbol_constraints[1][action_index]
#                         action_constraint = action_symbol_constraints[2][action_index]
#
#                         match = "".join(action_constraint)
#                         match = re.sub(" ", '_', match).strip()
#
#                         for token in doc:
#                             if token.dep_ == 'nsubj':
#                                 nsubj = token.text
#
#                         subj = nsubj + ": "
#
#                         if "Negative" in verb_type:
#                             relation = subj + "! " + action_symbol + '(' + match + ')'
#                         else:
#                             relation = subj + action_symbol + '(' + match + ')'
#
#     if "Negative" in verb_type and "Transitive" not in verb_type:
#         relation = "! " + relation
#
#     # Append 'if' or 'while' on knowing the occurrence of these words in the requirement
#     found = False
#     for clause in conditional_clauses:
#         match_quotes = re.compile('^' + clause, re.IGNORECASE).search(doc.text)
#         if match_quotes:
#             found = True
#             relation = clause + ' (' + relation + ')'
#     if not found:
#         relation = 'then (' + relation + ')'
#
#     return relation


def parse_relation_comparative(nlp, norm_req, syntax, comp_symbol):
    doc = nlp(norm_req)
    left_word = ""
    right_word = ""

    matcher = Matcher(nlp.vocab)
    matcher_right = Matcher(nlp.vocab)
    left_pattern = [{'DEP': 'nsubj'},
                    {'DEP': 'ROOT'}
                    ]
    matcher.add("Action", None, left_pattern)
    matches = matcher(doc)
    if matches:
        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            for token in doc:
                if token.dep_ == 'ROOT':
                    for child in token.children:
                        if child.dep_ == "nsubj" or child.dep_ == "amod":
                            left_word = child.text

    right_pattern = [{'DEP': 'ROOT'}, {'OP': '*'},
                     {'DEP': 'pobj'}
                     ]
    right_pattern_2 = [{'DEP': 'ROOT'}, {'OP': '*'},
                       {'DEP': 'dobj'}
                       ]
    right_pattern_3 = [{'DEP': 'ROOT'}, {'OP': '*'},
                       {'DEP': 'attr'}
                       ]

    matcher_right.add("Action", None, right_pattern)
    matcher_right.add("Action", None, right_pattern_2)
    matcher_right.add("Action", None, right_pattern_3)
    matches_right = matcher_right(doc)
    if matches_right:
        for match_id, start, end in matches_right:
            span = doc[start:end]  # The matched span
            for token in doc:
                if token.dep_ == "pobj" or token.dep_ == 'dobj':
                    right_word = token.text
                if token.dep_ == "attr" or token.dep_ == "dobj":
                    for token_child in token.children:
                        if token_child.dep_ == "nummod":
                            right_word = token_child.text + token.text

    relation = left_word + " " + comp_symbol + " " + right_word
    print(relation)
    # if left_word in subj and right_word in obj:
    relation = Relation(left=syntax.subj, symbol=comp_symbol, right=syntax.obj)

    # Append 'if' or 'while' on knowing the occurrence of these words in the requirement
    #for clause in conditional_clauses:
    #    match_quotes = re.compile('^' + clause, re.IGNORECASE).search(doc.text)
    #    if match_quotes:
    #        relation.condition = clause

    return relation


def parse_relation_bool_action(doc, syntax, condition=None):

    if condition == 'if':
        left_value = syntax.subj
        right_value = syntax.action_symbol + '_' + syntax.obj
    else:
        right_value = syntax.obj
        if syntax.action_symbol:
            left_value = syntax.action_symbol + '_' + syntax.subj
        else:
            left_value = syntax.subj

        if syntax.obj and not syntax.action_symbol:
            left_value = 'set_' + left_value
    relation = Relation(left=left_value, symbol='==', right=right_value)

    # Append 'if' or 'while' on knowing the occurrence of these words in the requirement
    #for clause in conditional_clauses:
    #    match_quotes = re.compile('^' + clause, re.IGNORECASE).search(doc.text)
    #    if match_quotes:
    #        relation.condition = clause

    if 'Negative' in syntax.verb_type:
        relation.neg_or_pos = 'neg'

    return relation


def parse_relation_intensive(doc, syntax):
    if "Intensive" in syntax.verb_type:
        nsubj_1 = ''
        nsubj_2 = ''
        for token in doc:
            if token.dep_ == 'ROOT':
                for child in token.children:
                    if child.dep_ == 'nsubj':
                        nsubj_1 = child.text
                    if child.dep_ == 'acomp' or child.dep_ == 'attr':
                        acomp = child.text
        for chunk in doc.noun_chunks:
            if chunk.root.dep_ == 'nsubj':
                nsubj_2 = re.sub('\\b[a|A]\\b', '', chunk.text).strip()
                nsubj_2 = re.sub('\\b[a|A]n\\b', '', nsubj_2).strip()
                nsubj_2 = re.sub('\\b[t|T]he\\b', '', nsubj_2).strip()
                nsubj_2 = re.sub(' ', '_', nsubj_2)

        if nsubj_2:
            nsubj = nsubj_2
        else:
            nsubj = nsubj_1

        relation = Relation(left=nsubj, symbol='==', right=acomp)

    if "Intensive" in syntax.verb_type and syntax.action_type == 'bool_action':
        relation = Relation(left=syntax.action_symbol, symbol='(', right=syntax.action_constraint[0])

    # Append 'if' or 'while' on knowing the occurrence of these words in the requirement
    #for clause in conditional_clauses:
    #    match_quotes = re.compile('^' + clause, re.IGNORECASE).search(doc.text)
    #    if match_quotes:
    #        relation.condition = clause

    if 'Negative' in syntax.verb_type:
        relation.neg_or_pos = 'neg'

    return relation

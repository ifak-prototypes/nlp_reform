import re
from typing import List

import spacy

from nlp_reform.dto import Relation, Syntax
from nlp_reform_srl.modules.sequence_diagram import *
from nlp_reform_srl.modules.srl_frames import SemFrames
from util.comparative_symbol import find_comparative_symbol
from util import decompose_req

from enum import Enum

pp = pprint.PrettyPrinter(indent=2)

spacy_nlp = spacy.load('en_core_web_sm')


class Arguments(Enum):
    # Arguments
    V = 'V'
    ARG0 = 'ARG0'
    ARG1 = 'ARG1'
    ARG2 = 'ARG2'
    ARG3 = 'ARG3'
    ARG4 = 'ARG4'
    # Argument Modifiers
    ADV = 'ARGM-ADV'
    LOC = 'ARGM-LOC'
    MNR = 'ARGM-MNR'
    MOD = 'ARGM-MOD'
    TMP = 'ARGM-TMP'
    CAU = 'ARGM-CAU'
    DIR = 'ARGM-DIR'
    NEG = 'ARGM-NEG'
    EXT = 'ARGM-EXT'
    GOL = 'ARGM-GOL'
    PRD = 'ARGM-PRD'


# This function checks if the requirement text passed has a condition in it.
def check_if_guard(decomp_req):
    is_guard = False
    condition_value = 'then'
    for condition in decompose_req.CONDITIONS:
        if condition in decomp_req:
            is_guard = True
            condition_value = condition
            break
    return is_guard, condition_value


def map_frame_to_relation(frames, clause, condition_value, is_guard) -> Relation:
    action, verb, left_value, right_value, symbol = '', '', '', '', ''
    relation = Relation()
    remove_next_word = False
    next_word = ''
    for current_frame in frames:
        print(current_frame)
        action = current_frame[Arguments.V.value]
        doc_ = spacy_nlp(action)
        verb = doc_[0].lemma_
        if verb == 'be':
            remove_next_word = True
        if is_guard:
            string = clause.split(" ")
            try:
                index = string.index(action)  # name_
                next_word = string[index + 1]
            except:
                next_word = ''
            verb = verb + ' ' + next_word
            symbol = find_comparative_symbol(spacy_nlp, verb)

        if Arguments.NEG.value in current_frame:
            relation.neg_or_pos = 'neg'

        if Arguments.ARG0.value in current_frame:
            left_value = current_frame[Arguments.ARG0.value]
            if Arguments.ARG1.value in current_frame:
                right_value = current_frame[Arguments.ARG1.value]
            elif Arguments.ARG2.value in current_frame:
                right_value = current_frame[Arguments.ARG2.value]

        elif Arguments.ARG1.value in current_frame:
            left_value = current_frame[Arguments.ARG1.value]
            if Arguments.ARG2.value in current_frame:
                right_value = current_frame[Arguments.ARG2.value]
            elif Arguments.ARG4.value in current_frame:
                right_value = current_frame[Arguments.ARG4.value]
            elif Arguments.PRD.value in current_frame:
                right_value = current_frame[Arguments.PRD.value]
            elif Arguments.MNR.value in current_frame:
                right_value = current_frame[Arguments.MNR.value]

        elif Arguments.ARG3.value in current_frame:
            left_value = current_frame[Arguments.ARG3.value]
            if Arguments.ARG4.value in current_frame:
                right_value = current_frame[Arguments.ARG4.value]

    left_value = re.sub(r'"\s*([^"]*?)\s*"', r'"\1"', left_value)  # remove space in quotation for mark signal in clause
    syntax = Syntax(subj=left_value,
                    obj=right_value,
                    action=action
                    )

    if right_value and not symbol:
        symbol = '=='

    if not is_guard and verb:
        left_value = verb + ' ' + left_value

    relation.syntax = syntax

    all_stopwords = spacy_nlp.Defaults.stop_words
    # all_stopwords.remove('')
    left_value = left_value.lower().replace('"', '').split(" ")
    left_value = [word for word in left_value if not word in all_stopwords]
    left_value = ' '.join(left_value)
    left_value = left_value.replace(' ', '_')

    right_value = right_value.split(" ")
    right_value = [word for word in right_value if not word in all_stopwords]
    if remove_next_word:
        print(next_word)
        right_value = [word for word in right_value if word != next_word]
    right_value = ' '.join(right_value)

    relation.left = left_value
    relation.symbol = symbol
    relation.right = right_value
    relation.clause = clause
    relation.condition = condition_value

    return relation


def get_srl_frames(clause, sem_frames):
    srl_frames = sem_frames.get_frames(text=clause)

    if not srl_frames:
        print('Decomposed requirement has no SRL frames', clause)
        frame_spacy = []
        # If no SRL frames, then check with spacy and add frames manually
        doc = spacy_nlp(clause)
        temp = dict()
        for token in doc:
            print(token.text, token.dep_, token.pos_)
            if token.dep_ == 'ROOT':  # or token.pos_ == 'VERB'
                temp[Arguments.V.value] = token.text
                print('Verb', token.text)

            if 'nsubj' in token.dep_:
                temp[Arguments.ARG1.value] = token.text
                print('nsubj', token.text)

            if 'dobj' in token.dep_:
                temp[Arguments.ARG2.value] = token.text
                print('dobj', token.text)

        frame_spacy.append(temp)
        print(frame_spacy)
        if frame_spacy:
            srl_frames = frame_spacy

    return srl_frames

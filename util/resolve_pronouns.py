#######################################################################################################################
# Documentation
# resolve_pronouns.py
# This module resolves third person pronouns in the input requirement and replaces the pronouns with the referred
# subject.
#
# Inputs:
#
# Outputs:
#
# Is called by:
#
#######################################################################################################################
# Libraries
import re
import spacy
from spacy.matcher import Matcher

DISPLAY_LOG = False

spacy_model = "en_core_web_sm"
nlp = spacy.load(spacy_model)


def resolve_pronouns(req):
    req_ = re.sub('\. ', ', ', req)

    doc = nlp(req_)
    subjIndex = -1
    pronIndex = -1
    pron = ''
    subj = ''
    pron_root = ''
    subj_mod = ''
    subj_conj = ''
    subj_end = ''
    pron_resolved_req = ''
    num_agreement_flag = -1  # This flag is initialized with -1, 0 if disagreed, 1 if agreed
    pleonastic_pron_flag = 0

    for token in doc:
        if token.pos_ == 'PRON':
            pron_ = token.text
            if token.head.lemma_ == 'be':
                for child in token.head.children:
                    if child.dep_ == 'aux' or child.dep_ == 'xcomp':
                        pleonastic_pron_flag = 1

    if pleonastic_pron_flag:
        if DISPLAY_LOG: print("\tPleonastic pronoun cited. Pronoun '%s' has no direct referent." % (pron_))

    for token in doc:
        if token.pos_ == 'PRON':
            if pleonastic_pron_flag == 0:
                pron = token.text
                pronIndex = token.i
                pron_root = token.head.text

        if subjIndex == -1:
            if 'subj' in token.dep_ and token.pos_ != 'PRON':
                subj_token = token
                for child in subj_token.children:
                    if subj_mod == '':
                        if 'mod' in child.dep_ or 'compound' in child.dep_ or 'det' in child.dep_:
                            subj_mod = child.text
                for child in subj_token.children:
                    if 'conj' in child.dep_:
                        subj_conj = child.text

                matcher = Matcher(nlp.vocab)
                if subj_mod:
                    if subj_conj:
                        pattern_subj = [
                            {'ORTH': subj_mod},
                            {'OP': '*'},
                            {'ORTH': subj_token.text},
                            {'OP': '*'},
                            {'ORTH': subj_conj},
                        ]
                    else:
                        pattern_subj = [
                            {'ORTH': subj_mod},
                            {'OP': '*'},
                            {'ORTH': subj_token.text},
                        ]
                else:
                    if subj_conj:
                        pattern_subj = [
                            {'ORTH': subj_token.text},
                            {'OP': '*'},
                            {'ORTH': subj_conj},
                        ]
                    else:
                        pattern_subj = [
                            {'ORTH': subj_token.text},
                        ]
                matcher.add("Action", None, pattern_subj)
                matches = matcher(doc)

                for match_id, start, end in matches:
                    span = doc[start:end]  # The matched span
                    subj_found = span.text.strip()
                    subj = span.text.strip()
                    subj = re.sub('\\ba\\b|\\bA\\b', 'the', subj)
                    subj = re.sub('\\ban\\b|\\bAn\\b', 'the', subj)
                    subj = re.sub('\\bThe\\b', 'the', subj)
                subjIndex = token.i

    if pronIndex != -1 and subjIndex != -1:
        if pronIndex > subjIndex:
            # Identify the number of subject
            doc = nlp(subj)
            subj_num = ''
            for token in doc:
                if token.tag_ == 'NNS' or token.tag_ == 'NNPS':
                    subj_num = 'Plural'
                if token.text == 'and' or token.text == 'AND':
                    subj_num = 'Plural'
            if subj_num == '':
                subj_num = 'Singular'
            # Identify the number of pronoun
            if pron == 'it' or pron == 'its' or pron == 'itself':
                pron_num = 'Singular'
            if pron == 'they' or pron == 'them' or pron == 'their' or pron == 'themselves':
                pron_num = 'Plural'
            # Identify the number of root of pronoun
            doc = nlp(pron_root)
            verb_num = ''
            for token in doc:
                if token.tag_ == 'VBZ':
                    verb_num = 'Singular'
            if verb_num == '':
                verb_num = 'Unknown'

            if verb_num != 'Unknown':
                if subj_num == verb_num and pron_num == verb_num:
                    num_agreement_flag = 1
                    if DISPLAY_LOG: print('\tResolution with farthest subject possible')
                if subj_num != verb_num or pron_num != verb_num or subj_num != pron_num:
                    num_agreement_flag = 0
                    if DISPLAY_LOG: print('\tResolution of pronouns not attempted since the numbers (of Subject, Pronoun and Root of Pronoun) do not match.')
                    if DISPLAY_LOG: print('\t\tSubject: %s -- %s' % (subj, subj_num))
                    if DISPLAY_LOG: print('\t\tPronoun: %s -- %s' % (pron, pron_num))
                    if DISPLAY_LOG: print('\t\tPronoun Verb: %s -- %s' % (pron_root, verb_num))
            else:
                if subj_num == pron_num:
                    num_agreement_flag = 1
                    if DISPLAY_LOG: print('\tResolution with farthest subject possible')
                if subj_num != pron_num:
                    num_agreement_flag = 0
                    if DISPLAY_LOG: print('\tResolution of pronouns not attempted since the numbers (of Subject and Pronoun) do not match.')
                    if DISPLAY_LOG: print('\t\tSubject: %s -- %s' % (subj, subj_num))
                    if DISPLAY_LOG: print('\t\tPronoun: %s -- %s' % (pron, pron_num))
                    if DISPLAY_LOG: print('Pronoun Verb: %s \t\t Pronoun Verb Number: &s' % (pron_root, verb_num))

            if num_agreement_flag == 1:
                pron_resolved_req = re.sub('\\b' + pron + '\\b', subj, req)
                if DISPLAY_LOG: print("\tResolving pronoun '%s' (found at index: %s) with the subject phrase '%s' (found at index: %s)"
                    % (pron, pronIndex, subj_found, subjIndex))
                if DISPLAY_LOG: print('\tResolved Requirement: ', pron_resolved_req)
            else:
                pron_resolved_req = req

    if pron_resolved_req == '' and num_agreement_flag == -1:
        if DISPLAY_LOG: print('\tNo pronouns found to be resolved.')
        pron_resolved_req = req

    return pron_resolved_req


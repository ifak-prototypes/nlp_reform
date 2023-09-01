#######################################################################################################################
# Documentation:
# decompose_req.py
# This module decomposes the input requirement. It identifies Multiple conditions, Between phrases, Root and Noun
# Phrase conjunctions in the requirements and decompose each step-by-step. This gives easy-to-process sub-requirements.
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
from spacy.matcher import Matcher

# Modules / Functions
from nlp_reform_v1.modules.helper.read_write_artefacts import get_values_from_artefacts

# Variables
from nlp_reform_v1 import nlp, DISPLAY_LOG


#######################################################################################################################
def decompose_req_mod(req):
    # The requirement is decomposed to sub-requirements if there are multiple conditional clauses in it.
    # Eg: 'Temperature is greater than Tmin and pressure is lesser than Pmax' will be decomposed into
    # 'Temperature is greater than Tmin' and 'pressure is lesser than Pmax'
    MultipleCond_decomposed = decompose_MultipleCond(req)

    # Requirements with phrase 'between' is rephrased using this function.
    # Eg: 'The temperature has a value between t_min and t_max' is rephrased as
    # 'The temperature has a value greater than t_min and lesser than t_max'
    Between_replaced_req = []
    if DISPLAY_LOG: print('[Between Phrase]')
    for req in MultipleCond_decomposed:
        replaced_req = decompose_Between("".join(req))
        Between_replaced_req.append(replaced_req)

    # This checks if there is a ROOT conjunction in the requirement. If any is present, it is decomposed
    # to sub-requirements
    decomposed_RootConj_list = []
    if DISPLAY_LOG: print('[ROOT Conjunction]')
    for req in Between_replaced_req:
        root_conj_flag, NP_conj_flag = check_RootConj_NPConj_decomp(req)
        if root_conj_flag:
            if DISPLAY_LOG: print('\t%s: %s' % (req, 'FOUND'))
            sub_clause_flag = 1
            error_count = 10  # used to exit the loop under an erroneous condition
            decomposed_req_ = []
            decomposed_req_.append(req)
            # This loop keeps decomposing the conjunctions in the decomposed requirements until either of the conditions
            # occur - No more sub clauses returned (i.e. flag will be 0) or error count hits 0.
            while sub_clause_flag and error_count:
                sub_clause_flag, clauses = decompose_RootConj(decomposed_req_)
                error_count = error_count - 1
                decomposed_req_ = clauses
            for item in decomposed_req_:
                if item not in decomposed_RootConj_list:
                    decomposed_RootConj_list.append(item)
        else:
            if req not in decomposed_RootConj_list:
                decomposed_RootConj_list.append(req)
                if DISPLAY_LOG: print('\t%s: %s' % (req, 'NOT_FOUND'))

    # This checks if there is a Noun Phrase (NP) conjunction in the requirement. If any is present, it is decomposed
    # to sub-requirements
    decomposed_NPConj_list = []
    if DISPLAY_LOG: print('[NP Conjunction]')
    for req in decomposed_RootConj_list:
            root_conj_flag, NP_conj_flag = check_RootConj_NPConj_decomp(req)
            if NP_conj_flag:
                if DISPLAY_LOG: print('\t%s: %s' % (req, 'FOUND'))
                sub_clause_flag = 1
                error_count = 10  # used to exit the loop under an erroneous condition
                decomposed_req_ = decomposed_RootConj_list
                while sub_clause_flag and error_count:
                    sub_clause_flag, clauses = decompose_NPConj(decomposed_req_)
                    error_count = error_count - 1
                    decomposed_req_ = clauses
                for item in decomposed_req_:
                    if item not in decomposed_NPConj_list:
                        decomposed_NPConj_list.append(item)
            else:
                if req not in decomposed_NPConj_list:
                    decomposed_NPConj_list.append(req)
                if DISPLAY_LOG: print('\t%s: %s' % (req, 'NOT_FOUND'))

    unique_NP_clauses = []
    for clause in decomposed_NPConj_list:
        clause = re.sub('\\ba\\b|\\ban\\b', 'the', clause)
        clause_ = re.sub('\.$|\\bif\\b', '', clause)
        clause_super_flag = 0
        for other_clause in decomposed_NPConj_list:
            other_clause = re.sub('\\ba\\b|\\ban\\b', 'the', other_clause)
            other_clause_ = re.sub('\.$|\\bif\\b', '', other_clause)
            if clause_ != other_clause_ and other_clause_ in clause_:
                # print(clause, " : ", other_clause, " : L superclause of R")
                clause_super_flag = 1

        if clause_super_flag != 1:
            if clause not in unique_NP_clauses:
                unique_NP_clauses.append(clause)

    # This removes occurrence of conjunction words in the requirement
    decomposed_req = unique_NP_clauses
    req_stripped = []
    for req in decomposed_req:
        req_stripped_text = re.sub('\\band\\b|\\bor\\b|\\bAND\\b|\\bOR\\b', '', req).strip()
        if req_stripped_text:
            req_stripped.append(req_stripped_text)

    decomposed_req = req_stripped
    return decomposed_req

#######################################################################################################################
def decompose_MultipleCond(req):
    doc =nlp (req)
    MultipleCond_flag = 0
    matcher = Matcher(nlp.vocab)
    # This pattern matches If/if .... if/when/while/./,         -> MULTIPLE IFs
    pattern = [
               {'ORTH': {"REGEX": '[i|I]f'}},
               {'OP': '*'},
               {'ORTH': {"REGEX": 'if|when|while|\.|,'}},
               ]
    # This pattern matches When/when .... if/when/while/./,     -> MULTIPLE WHENs
    pattern_2 = [
               {'ORTH': {"REGEX": '[w|W]hen'}},
               {'OP': '*'},
               {'ORTH': {"REGEX": 'if|when|while|\.|,'}},
               ]
    # This pattern matches While/while .... if/when/while/./,   -> MULTIPLE WHILEs
    pattern_3 = [
               {'ORTH': {"REGEX": '[w|W]hile'}},
               {'OP': '*'},
               {'ORTH': {"REGEX": 'if|when|while|\.|,'}},
               ]
    matcher.add("Action", None, pattern)
    matcher.add("Action", None, pattern_2)
    matcher.add("Action", None, pattern_3)
    matches = matcher(doc)
    sub_clauses = []
    for match_id, start, end in matches:
        span = doc[start:end]  # The matched span
        sub_clauses.append(span.text)
        MultipleCond_flag = 1

    # This piece of code strips the conditional clauses from each other and provide a unique set of clauses
    unique_clauses = []
    for clause in sub_clauses:
        clause_unique_flag = 0
        clause_super_flag = 0
        for other_clause in sub_clauses:
            if clause == other_clause:
                clause_unique_flag = 1
            if clause != other_clause and other_clause in clause:
                clause_super_flag = 1

            # If a clause is a super-clause of any other clause, it is neglected. Else appended to unique clauses list
            if clause_unique_flag == 1 and clause_super_flag == 0:
                clause = re.subn('(when|if|while)$', '', clause)[0].strip()
                if clause not in unique_clauses:
                    unique_clauses.append(clause)

    # Concatenation of unique clauses is obtained and stripped from the main clause.
    # This shall provide the remainder of the main clause with no conditional clauses.
    clause_sum = ""
    for clause in unique_clauses:
        clause_sum = clause_sum + ' ' + clause
    req_remainder = re.sub(clause_sum.strip(), "", req).strip()

    # Decomposed requirements will have all unique conditional clauses
    # and the remainder clause from the main clause
    decomposed_req = []
    for unique_clause in unique_clauses:
        unique_clause = re.sub('and$|or$|AND$|OR$', '', unique_clause).strip()
        decomposed_req.append(unique_clause)
    decomposed_req.append(req_remainder)

    if MultipleCond_flag:
        if DISPLAY_LOG: print('[Multiple Condition]: FOUND')
    else:
        if DISPLAY_LOG: print('[Multiple Condition]: NOT_FOUND')

    return decomposed_req


def decompose_Between(req):
    BETWEEN_replaced_req = ''
    doc = nlp(req)
    BETWEEN_flag = 0
    matcher = Matcher(nlp.vocab)
    first_word, second_word = '', ''
    value_first_word, value_second_word = '', ''
    # This pattern checks if there is a match for 'between <something> and/AND <something>'
    pattern = [
        {'ORTH': 'between'},
        {},
        {'ORTH': {"REGEX": 'and|AND'}},
        {},
    ]
    matcher.add("Action", None, pattern)
    matches = matcher(doc)

    sub = ''
    pattern = re.compile('.*between', re.IGNORECASE)
    match_pattern = re.search(pattern, req)
    if match_pattern:
        sub = re.sub('between', '', match_pattern.group(0))
        BETWEEN_flag = 1

    values_found_flag = 0
    # If there is a pattern match, then the phrase 'between <something> and/AND <something>' is rephrased as
    # 'greater than <something> and/AND lesser than <something>'
    if matches:
        for match_id, start, end in matches:
            span = doc[start:end]

            result = re.search('between(.*)and', span.text)
            first_word = result.group(1).strip()
            value_first_word = get_values_from_artefacts(first_word)
            result = re.search('and(.*)', span.text)
            second_word = result.group(1).strip()
            value_second_word = get_values_from_artefacts(second_word)
            if value_first_word != 'NOT_FOUND' and value_second_word != 'NOT_FOUND':
                values_found_flag = 1
                if value_first_word > value_second_word:
                    text = re.sub('between', 'lesser than', span.text)
                    text = re.sub('and|AND', 'and ' + sub + 'greater than', text)
                else:
                    text = re.sub('between', 'greater than', span.text)
                    text = re.sub('and|AND', 'and ' + sub + 'lesser than', text)
            else:

                text = re.sub('between', 'greater than', span.text)
                text = re.sub('and|AND', 'and ' + sub + 'lesser than', text)
            BETWEEN_replaced_req = re.sub(span.text, text, req)
    else:
        BETWEEN_replaced_req = req

    if BETWEEN_flag:
        if DISPLAY_LOG: print('\t%s: %s' % (req, 'FOUND'))
        if DISPLAY_LOG: print('\t\t%s - %s' % (first_word, value_first_word))
        if DISPLAY_LOG: print('\t\t%s - %s' % (second_word, value_second_word))
        if values_found_flag != 1:
            if DISPLAY_LOG: print("\t\tValues of '%s' and/or '%s' are not found. Assuming the first value to be smaller than the second."
                % (first_word, second_word))
    else:
        if DISPLAY_LOG: print('\t%s: %s' % (req, 'NOT_FOUND'))

    return BETWEEN_replaced_req

def check_RootConj_NPConj_decomp(decomposed_req):
    doc = nlp(decomposed_req)
    root_conj_flag = 0 # Set to high when there is a ROOT conjunction in the requirement
    NP_conj_flag = 0 # Set to high when there is a Noun Phrase (NP) conjunction in the requirement

    for token in doc:
        if token.dep_ == 'ROOT':
            for child in token.children:
                if child.dep_ == 'conj':
                    root_conj_flag = 1
        if token.dep_ == 'nsubj' or token.dep_ == 'nsubjpass' or token.dep_ == 'nmod' or\
                token.dep_ == 'dobj' or token.dep_ == 'pobj' or \
                token.dep_ == 'prep' or token.dep_ == 'acomp' or token.dep_ == 'advmod':
            sub_obj = token
            for token_1 in doc:
                if token_1.dep_ == 'conj':
                    for ancestor in token_1.ancestors:
                        if ancestor == sub_obj:
                            NP_conj_flag = 1

    return root_conj_flag, NP_conj_flag

def decompose_NPConj(decomposed_req):
    NP_decomposed_clause = []
    subj = ''
    subj_mod = ''
    obj = ''
    obj_mod = ''
    acomp_obj = ''
    acomp_obj_mod = ''
    acomp_obj_end = ''
    sub_clause_flag = 0

    to_replace_list = []
    to_replace_list_stripped = []
    rem_from_main_clause = []
    sub_clause = ''
    sub_clause_list = []

    for req in decomposed_req:
        sub_clause_list = []
        doc = nlp(req)
        for token in doc:
            # This checks if any of the child of SUBJETCS 'nsubj' or 'nsubjpass' has a dependency 'conj'.
            # If then, the parent token is called 'subj_token' and the child token is called 'conj_token'.
            # Further, if there is any child of 'subj_token' has a modifier dependency (ie, amod, nummod, appos, etc.),
            # the child token is called 'subj_mod'. in this case, 'subj_mod' precedes 'subj_token'.
            if token.dep_ == 'nsubj' or token.dep_ == 'nsubjpass':
                subj_token = token
                for token_1 in doc:
                    if token_1.dep_ == 'conj':
                        conj_token = token_1
                        for ancestor in conj_token.ancestors:
                            if ancestor == subj_token:
                                subj = subj_token.text
                                for child in subj_token.children:
                                    if 'mod' in child.dep_:
                                        subj_mod = child.text
            # This checks if any of the child of OBJECTS 'dobj' or 'pobj' or 'prep' has a dependency 'conj'.
            # If then, the parent token is called 'obj_token' and the child token is called 'conj_token'.
            # Further, if there is any child of 'obj_token' has a modifier dependency (ie, amod, nummod, appos, etc.),
            # the child token is called 'obj_mod'. in this case, 'obj_mod' precedes 'obj_token'.
            if token.dep_ == 'dobj' or token.dep_ == 'pobj' or token.dep_ == 'prep':
                obj_token = token
                for token_1 in doc:
                    if token_1.dep_ == 'conj':
                        conj_token = token_1
                        for ancestor in conj_token.ancestors:
                            if ancestor == obj_token:
                                obj = obj_token.text
                                for child in obj_token.subtree:
                                    if child not in conj_token.subtree:
                                        if 'mod' in child.dep_ or 'appos' in child.dep_ or 'compound' in child.dep_:
                                            obj_mod = child.text
            # This checks if any of the child of COMPELEMNTARY OBJECTS 'acomp' has a dependency 'conj'.
            # If then, the parent token is called 'acomp_obj' and the child token is called 'conj_token'.
            # Further, if there is any child of 'acomp_obj' has a modifier dependency (ie, amod, nummod, appos, etc.),
            # the child token is called 'acomp_obj_mod'. in this case, 'acomp_obj_mod' precedes 'acomp_obj'.
            # The child of 'conj_token' with dependency 'pobj' is called 'acomp_obj_end'.
            if token.dep_ == 'acomp' or token.dep_ == 'advmod':
                obj_token = token
                for token_1 in doc:
                    if token_1.dep_ == 'conj':
                        conj_token = token_1
                        for ancestor in conj_token.ancestors:
                            if ancestor == obj_token:
                                acomp_obj = obj_token.text
                                for child in obj_token.subtree:
                                    if child not in conj_token.subtree:
                                        if 'mod' in child.dep_ or 'appos' in child.dep_:
                                            acomp_obj_mod = child.text
                        for child in token_1.subtree:
                            if child.dep_ == 'pobj':
                                acomp_obj_end = child.text
                if token.dep_ == 'prep' and token.head.dep_ != 'acomp':
                    obj_token = token
                    for token_1 in doc:
                        if token_1.dep_ == 'conj':
                            conj_token = token_1
                            for ancestor in conj_token.ancestors:
                                if ancestor == obj_token:
                                    acomp_obj = obj_token.text
                                    for child in obj_token.subtree:
                                        if child not in conj_token.subtree:
                                            if 'mod' in child.dep_ or 'appos' in child.dep_:
                                                acomp_obj_mod = child.text
                            for child in token_1.subtree:
                                if child.dep_ == 'pobj':
                                    acomp_obj_end = child.text
        matcher = Matcher(nlp.vocab)

        if subj_mod:
            pattern_subj = [
                {'ORTH': subj_mod},
                {'OP': '*'},
                {'DEP': 'conj'},
            ]
        else:
            pattern_subj = [
                {'ORTH': subj},
                {'OP': '*'},
                {'DEP': 'conj'},
            ]

        if obj_mod:
            pattern_obj = [
                {'ORTH': obj_mod},
                {'OP': '*'},
                {'DEP': 'conj'},
            ]
        else:
            pattern_obj = [
                {'ORTH': obj},
                {'OP': '*'},
                {'DEP': 'conj'},
            ]

        if acomp_obj:
            pattern_obj_acomp = [
                {'ORTH': acomp_obj},
                {'OP': '*'},
                {'ORTH': acomp_obj_end},
            ]
            matcher.add("Action", None, pattern_obj_acomp)

        if acomp_obj_mod:
            pattern_obj_acomp = [
                {'ORTH': acomp_obj_mod},
                {'OP': '*'},
                {'ORTH': acomp_obj_end},
            ]
            matcher.add("Action", None, pattern_obj_acomp)

        matcher.add("Action", None, pattern_subj)
        matcher.add("Action", None, pattern_obj)
        matches = matcher(doc)

        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            sub_clause_list.append(span.text.strip())

        if sub_clause_list:
            sub_clause = min(sub_clause_list, key=len)
            sub_clause_flag = 1

        if acomp_obj or acomp_obj_mod:
            matcher = Matcher(nlp.vocab)
            doc = nlp(sub_clause)
            pattern_obj_1 = [
                {'DEP': 'pobj'},
                {'OP': '*'},
                {'DEP': 'cc'},
                {'OP': '*'},
                {'DEP': 'pobj'}
            ]
            matcher.add("Action", None, pattern_obj_1)
            matches = matcher(doc)
            two_objects_flag = 0
            if matches:
                two_objects_flag = 1

            if two_objects_flag == 0:
                sub_clause = re.sub(acomp_obj_end, '', sub_clause).strip()

        # Any conjunction word form the end of the sub-clause is removed.
        sub_clause = re.sub('\\band$|\\bor$|\\bAND$|\\bOR$', '', sub_clause).strip()
        # Remaining clause 'rem_from_main_clause' is obtained by replacing the sub_clause with '_REPLACE_'
        if sub_clause:
            try:
                rem_from_main_clause = re.sub(sub_clause, '_REPLACE_', req).strip()
            except:
                pass
                # print('Could not substitute.')
        # If no sub_clause found, the whole main clause is retained.
        else:
            rem_from_main_clause = re.sub(sub_clause, '', req).strip()

        # This list has every phrase that has to be replaced in the main clause.
        to_replace_list = re.split('\\band\\b|\\bor\\b|\\bAND\\b|\\bOR\\b', sub_clause)

        # This strips off any article (dependency 'det') in the phrases to be replaced.
        for element in to_replace_list:
            if element:
                if element not in to_replace_list_stripped:
                    element = re.sub('\\ba\\b|\\ban\\b|\\bthe\\b', '', element)
                    to_replace_list_stripped.append(element.strip())

        # Replaced clause 'replaced_clause' replaces the word '_REPLACE_' with every word from
        # the phrases to be replaced 'to_replace_list'.
        replaced_clause = []
        for word_to_replace in to_replace_list_stripped:
            replaced_clause.append(re.sub('_REPLACE_', word_to_replace, rem_from_main_clause).strip())

        for clause in replaced_clause:
            if clause not in NP_decomposed_clause and clause:
                NP_decomposed_clause.append(clause)

        if sub_clause_flag == 0:
            NP_decomposed_clause = decomposed_req

    return sub_clause_flag, NP_decomposed_clause

def decompose_RootConj(decomposed_req):
    clauses = []
    sub_clause_flag = 0 # This flag is reset to 0. It becomes 1 only when a sub_clause is found.

    for clause in decomposed_req:
        sub_clause = ''
        sub_clause_list = []
        subj_conj_list = []
        doc = nlp(clause)
        root = ''
        cconj = ''
        conj = ''
        for token in doc:
            if token.dep_ == 'ROOT':
                root = token.text
                for child in token.children:
                    if child.dep_ == 'cc':
                        cconj = child.text
                    if child.dep_ == 'conj':
                        conj = child.text

        matcher = Matcher(nlp.vocab)
        matcher_root_cconj = Matcher(nlp.vocab)
        matcher_subj_conj = Matcher(nlp.vocab)

        # This pattern checks if there is an occurrence
        # '* ROOT * CCONJ (specifically, of the Root an not an NP)'
        pattern = [
            {'OP': '*'},
            {'ORTH': root},
            {'OP': '*'},
            {'ORTH': cconj},
        ]
        # This pattern checks the occurrence
        # 'ROOT * CCONJ'. This is used to compute the subject clause.
        pattern_root_cconj = [
            {'ORTH': root},
            {'OP': '*'},
            {'ORTH': cconj},
        ]
        # This pattern checks the occurrence
        # '* conj'. This is used to compute the object clause.
        pattern_subj_conj = [
            {'OP': '*'},
            {'ORTH': conj},
        ]
        matcher.add("Action", None, pattern)
        matcher_root_cconj.add("Action", None, pattern_root_cconj)
        matcher_subj_conj.add("Action", None, pattern_subj_conj)
        matches = matcher(doc)
        matches_root_cconj = matcher_root_cconj(doc)
        matcher_subj_conj = matcher_subj_conj(doc)

        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            sub_clause_list.append(span.text.strip())

        root_cconj = ''
        for match_id, start, end in matches_root_cconj:
            span = doc[start:end]  # The matched span
            root_cconj = span.text

        for match_id, start, end in matcher_subj_conj:
            span = doc[start:end]  # The matched span
            subj_conj_list.append(span.text.strip())

        if subj_conj_list:
            subj_conj = max(subj_conj_list, key=len)
        else:
            subj_conj = clause

        if sub_clause_list:
            sub_clause = max(sub_clause_list, key=len)
            sub_clause_flag = 1  # This flag is made as a sub_clause is found.

        # Subject clause is formulated by stripping the
        # 'ROOT * CCONJ'
        # from
        # '* ROOT * CCONJ'
        # Here the initial * indicates all that belongs to the subject.
        subj_clause = re.sub(root_cconj, '', sub_clause)

        # Object clause is formulated by stripping the
        # '* conj'
        # from
        # main clause
        obj_clause = re.sub(subj_conj, '', clause).strip()
        ## print('obj_clause is: ', obj_clause)

        # 'sub_clause' is obtained by removing any conjunction in the beginning of the matches obtained.
        # This retrieves meaningful sub-requirements.
        sub_clause = re.sub('^and|and$|or$|AND$|OR$', '', sub_clause).strip()
        ## print("\t\tSub Clause found: ", sub_clause)

        # Remaining clause ('rem_from_main_clause') is formulated by stripping
        # the obtained sub-clause from the main-clause.
        try:
            rem_from_main_clause = re.sub(sub_clause, '', clause).strip()
            rem_from_main_clause = re.sub('^and|^or|^AND|^OR', '', rem_from_main_clause).strip()
        except:
            # print('Could not substitute.')
            rem_from_main_clause = sub_clause
        ## print("\t\tRem Clause found: ", rem_from_main_clause)

        # This identifies the subject and object phrases in both the clauses (sub_clause and rem_from_main_clause).
        subj_first_clause = ''
        subj_second_clause = ''
        obj_first_clause = ''
        obj_second_clause = ''

        doc = nlp(sub_clause)
        for token in doc:
            if token.dep_ == 'nsubj' or token.dep_ == 'nsubjpass' or token.dep_ == 'expl':
                subj_first_clause = token.text
            if token.dep_ == 'dobj' or token.dep_ == 'pobj':
                obj_first_clause = token.text
        doc = nlp(rem_from_main_clause)
        for token in doc:
            if token.dep_ == 'nsubj' or token.dep_ == 'nsubjpass' or token.dep_ == 'expl':
                subj_second_clause = token.text
            if token.dep_ == 'dobj' or token.dep_ == 'pobj':
                obj_second_clause = token.text

        # If the first clause has a subject phrase and the second clause does not have one,
        # it means that the subject phrase of the first clause belongs to the second clause too.
        # Hence the Remaining clause is prefixed with the subject phrase of the first clause.
        # This is done only if the second clause lacks a subject phrase.
        if subj_first_clause:
            if subj_second_clause == '':
                rem_from_main_clause = subj_clause + \
                                       re.sub('\\band\\b|\\bor\\b|\\bAND\\b|\\bOR\\b',
                                              '', rem_from_main_clause).strip()
        # If the second clause has an object phrase and the first clause does not have one,
        # it means that the object phrase of the second clause belongs to the first clause too.
        # Hence the Sub clause is suffixed with the object phrase of the second clause.
        # This is done only if the first clause lacks an object phrase.
        if obj_second_clause and obj_clause and sub_clause:
            if obj_first_clause == '':
                sub_clause = sub_clause + ' ' +  obj_clause

        # The list 'clauses' has both the 'sub_clause' and the 'rem_from_main_clause'
        if sub_clause not in clauses and sub_clause:
            clauses.append(sub_clause)
        if rem_from_main_clause not in clauses and rem_from_main_clause:
            clauses.append(rem_from_main_clause)

    return sub_clause_flag, clauses

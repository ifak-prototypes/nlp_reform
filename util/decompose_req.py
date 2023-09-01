import re
import nltk
import spacy

from spacy.matcher import Matcher
from nlp_reform.dto import Clause, DecompResult

CONDITIONS = ['if', 'when', 'until', 'while', 'combined']
CONJUNCTIONS = ['and', 'or', 'but']

spacy_nlp = spacy.load('en_core_web_sm')


def decompose_newlines(req):
    """
    decompose newlines in the requirement into clauses.
    """
    decomposed_req = []
    sent_list = nltk.tokenize.sent_tokenize(req)
    for s in sent_list:
        decomposed_req.append(str(s))

    decomposed_req = remove_empty_clauses(decomposed_req)

    return decomposed_req


def decompose_conditions(req):
    """
    check if there is a conditional word in the requirement and decomposes it. If there are no
    conditional words, the input requirement is returned as is.
    """
    decomposed_req = []
    doc = spacy_nlp(req)
    cond_ind = []
    # Check if any of the token of the requirement is a conditional word.
    for token in doc:
        if token.text in CONDITIONS:
            cond_ind.append(token.i)
    cond_ind.append(len(doc))

    # If the list cond_ind contains more than one element, decompose the requirement corresponding to the index of
    # the conditional word. Otherwise, return the input requirement as is.
    if len(cond_ind) > 1:
        decomposed_req.append("%s" % doc[:cond_ind[0]])
        for ind in range(len(cond_ind) - 1):
            decomposed_req.append("%s" % doc[cond_ind[ind]:cond_ind[ind + 1]])
    else:
        decomposed_req.append(req)

    decomposed_req = remove_empty_clauses(decomposed_req)

    return decomposed_req


def decompose_conjunctions(req):
    """
    decompose requirements with conjunctions into different clauses.
    """
    decomposed_req = []
    doc = spacy_nlp(req)
    cond_ind = []
    # Check if any of the token of the requirement is a conjunction.
    for token in doc:
        # if token.text in conjunctions:
        #     cond_ind.append(token.i)
        if token.dep_ == 'cc':
            #for ancestor in token.ancestors:
            #    if ancestor.text == 'between':
            #        break
            #else:
            cond_ind.append(token.i)

    if cond_ind:
        decomposed_req.append("%s" % doc[:cond_ind[0]])
        for i, ind in enumerate(cond_ind):
            try:
                decomposed_req.append("%s" % doc[ind + 1:cond_ind[i + 1]])
            except:
                decomposed_req.append("%s" % doc[ind + 1:])
    else:
        decomposed_req.append(req)

    decomposed_req = remove_empty_clauses(decomposed_req)

    return decomposed_req


def add_conditions_conjunctions(req, clauses, og_clauses):
    """
    add the details of conditions and conjunctions in (or, between) the clauses.
    conditions_list gives the condition per clause (len of list = len of clauses)
    conjunctions_list gives the conjunctions between the clauses (len of list = len of clauses - 1)
    """
    conditions_list = []
    for clause in clauses:
        cond_flag = False
        for cond in CONDITIONS:
            if re.findall(r'\b%s\b' % cond, clause):
                conditions_list.append(cond)
                cond_flag = True
        if not cond_flag:
            conditions_list.append(None)

    conjunctions_list = []
    for ind, clause in enumerate(og_clauses[:-1]):
        conj_flag = False
        for conj in CONJUNCTIONS:
            text = f'{clause} {conj} {og_clauses[ind + 1]}'
            if text in req:
                conjunctions_list.append(conj)
                conj_flag = True

        if not conj_flag:
            conjunctions_list.append('')


    # copy the condition to the successor if a conjunction occurs at the same index.
    # COND: ['when', ''] CONJ: ['and', '']
    # should be replaced as COND: ['when', 'when'] CONJ: ['and', '']

    for ind, (cond, conj) in enumerate(zip(conditions_list, conjunctions_list)):
        if cond and conj:
            if not conditions_list[ind + 1]:
                conditions_list[ind + 1] = cond

    # TODO: If there is only one clause, conjunctions_list will be an empty list. This may cause type mismatch. But
    #  the constraint is the length of the list should be 1 less than the clauses list.
    # conjunctions_list = [''] if not conjunctions_list else conjunctions_list

    assert len(conditions_list) == len(clauses), \
        f'Length mismatch - COND and CLAUSES\n{conditions_list}\n[{clauses}'

    assert len(conjunctions_list) == len(clauses) - 1, \
        f'Length mismatch - CONJ and CLAUSES\n{conjunctions_list}\n[{clauses}'

    # decomp = {
    #     'clauses': clauses,
    #     'conditions': conditions_list,
    #     'conjunctions': conjunctions_list
    # }

    clauses_ = []
    for clause, condition in zip(clauses, conditions_list):
        clauses_.append(Clause(text=clause, condition=condition))

    return DecompResult(clauses=clauses_, conjunctions=conjunctions_list)


def remove_empty_clauses(decomp_req):
    return [decomp for decomp in decomp_req if decomp]


def decompose_between(req):
    BETWEEN_replaced_req = ''
    doc = spacy_nlp(req)
    BETWEEN_flag = 0
    matcher = Matcher(spacy_nlp.vocab)
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
            result = re.search('and(.*)', span.text)
            second_word = result.group(1).strip()

            text = re.sub('between', 'greater than', span.text)
            text = re.sub('and|AND', 'and ' + sub + 'lesser than', text)
            BETWEEN_replaced_req = re.sub(span.text, text, req)
    else:
        BETWEEN_replaced_req = req

    return BETWEEN_replaced_req


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
        doc = spacy_nlp(req)
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
        matcher = Matcher(spacy_nlp.vocab)

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
            matcher = Matcher(spacy_nlp.vocab)
            doc = spacy_nlp(sub_clause)
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

    return NP_decomposed_clause


# This function tries to match each of the frame spans with the requirement fragments and check if there is a
# conjunction between the frame spans. This should work only if there are more than 2 frames for the given requirement.
def get_conjunctions_from_frame_spans(frame_spans, req):
    # If there is only one frame span, return an empty list.
    if len(frame_spans) <= 1:
        conj_infos = []
        return conj_infos

    req = re.sub("[,']", '', req)
    req_split = req.split(' ')
    # Append the start index of the requirement
    conj_indices = [0]
    conj_value = []
    for conj in CONJUNCTIONS:
        if conj in req_split:
            conj_ind = req_split.index(conj)
            conj_indices.append(conj_ind)
            conj_value.append(conj)
    # Append the last index of the requirement
    conj_indices.append(len(req_split))

    # If there is no conjunction found, the function should return an empty list.
    if not conj_value:
        conj_infos = []
        return conj_infos

    # If there is a conjunction, the requirement can be split based on the index of the conjunction.
    # For eg: 'Something shall be opened and something shall be closed' can be split as
    # ['Something shall be opened', 'something shall be closed']
    req_split_with_conj = []
    for i in range(1, len(conj_indices)):
        conj_split = req_split[conj_indices[i - 1]:conj_indices[i]]
        req_split_with_conj.append(conj_split)

    # This list has information regarding which splits are joined by a conjunction.
    conj_split_info = []
    for ind in range(len(req_split_with_conj) - 1):
        conj_split_info.append(
            {
                'req_split': (ind, ind + 1),  # the indices are corresponding to the requirement split
                'conj': conj_value[ind]
            }
        )

    # Now, check which requirement split matches with the frame spans
    matches = {}
    for req_ind, conj_split in enumerate(req_split_with_conj):
        for span_ind, span in enumerate(frame_spans):
            count = 0
            span_split = span.split(' ')
            for _ in span_split:
                if _ in [',', '.', '"', "'"]:
                    # remove punctuations from the list to make it consistent with the  requirement split
                    # TODO: look out for more punctuations that could cause the lists - requirement split and span split
                    #  to be inconsistent.
                    span_split.remove(_)
            for _ in span_split:
                if _ in conj_split:
                    count += 1
            if count == len(span_split):
                # if the count of matching words and the the length of span are equal, assume it to match with the
                # corresponding requirement split
                matches[req_ind] = span_ind

    # If there are no more than 2 matches, the function should return an empty list.
    if len(matches.keys()) <= 1:
        conj_infos = []
        return conj_infos

    conj_infos = []
    for info in conj_split_info:
        first_ind, second_ind = info['req_split'][0], info['req_split'][1]
        conj = info['conj']
        try:
            conj_infos.append(
                {
                    'frame_id': (matches[first_ind], matches[second_ind]),
                    # the indices are corresp. to the frame split
                    'conj': conj
                }
            )
        except:
            error = True

    return conj_infos

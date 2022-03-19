import re
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


nltk.download("wordnet")
nltk.download('punkt')  # Not sure if this is needed later. right now used for separating req into sentences

CONDITIONS = ['if', 'when', 'until', 'while', 'combined']
CONJUNCTIONS = ['and', 'or', 'but']

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


def decompose_conditions(req, models):
    """
    check if there is a conditional word in the requirement and decomposes it. If there are no
    conditional words, the input requirement is returned as is.
    """
    decomposed_req = []
    doc = models.spacy_nlp(req)
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


def decompose_conjunctions(req, models):
    """
    decompose requirements with conjunctions into different clauses.
    """
    decomposed_req = []
    doc = models.spacy_nlp(req)
    cond_ind = []
    # Check if any of the token of the requirement is a conjunction.
    for token in doc:
        # if token.text in conjunctions:
        #     cond_ind.append(token.i)
        if token.dep_ == 'cc':
            for ancestor in token.ancestors:
                if ancestor.text == 'between':
                    break
            else:
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


def add_conditions_conjunctions(req, clauses):
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
            conditions_list.append('')

    conjunctions_list = []
    for ind, clause in enumerate(clauses[:-1]):
        conj_flag = False
        for conj in CONJUNCTIONS:
            text = f'{clause} {conj} {clauses[ind + 1]}'
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

    decomp = {
        'clauses': clauses,
        'conditions': conditions_list,
        'conjunctions': conjunctions_list
    }

    return decomp


def remove_empty_clauses(decomp_req):
    return [decomp for decomp in decomp_req if decomp]

import re
from spacy.matcher import Matcher
from nlp_reform.dto import Syntax


def parse_context_mod(nlp, req):
    doc = nlp(req)

    # By invoking this function, the ACTION; ACTION_SYMBOL AND ACTION_TYPE of the requirement is obtained.
    action, action_symbol, action_type, obj = get_action_and_action_symbol(nlp, doc)

    # By invoking this function, the corresponding ACTION_CONSTRAINT is obtained.
    action_constraint = get_action_constraint(nlp, doc, action_type)

    return action, action_symbol, action_constraint, action_type, obj


def get_action_constraint(nlp, doc, action_type):
    action_constraint = []

    if action_type == 'verb_noun':
        # This pattern checks if there are compund nouns which can be parsed as constraints to the actions.
        # Gives a result only if there are 2 nouns minimum. They are rephrased as noun_noun (with underscores)
        matcher_compound = Matcher(nlp.vocab)
        compound_noun_pattern = [{'POS': 'NOUN', 'OP': '*'},
                                 {'ORTH': '-', 'OP': '*'},
                                 {'POS': 'ADJ', 'OP': '*'},
                                 {'POS': 'NOUN'},
                                 {'POS': 'NOUN', 'OP': '+'},
                                 {'POS': 'ADJ', 'OP': '*'},
                                 ]
        matcher_compound.add("Action", None, compound_noun_pattern)
        matches = matcher_compound(doc)
        comp_noun_list = []
        if matches:
            for match_id, start, end in matches:
                span = doc[start:end]  # The matched span
                if span.text not in comp_noun_list:
                    comp_noun_list.append(span.text)
            unique_comp_nouns = []
            for comp_noun in comp_noun_list:
                comp_noun_unique_flag = 0
                comp_noun_super_flag = 0
                for other_comp_noun in comp_noun_list:
                    if comp_noun == other_comp_noun:
                        comp_noun_unique_flag = 1
                    if comp_noun != other_comp_noun and other_comp_noun in comp_noun:
                        comp_noun_super_flag = 1

                    if len(comp_noun_list) == 1:
                        if comp_noun_unique_flag == 1:
                            unique_comp_nouns.append(comp_noun)
                    else:
                        if comp_noun_super_flag == 1:
                            if comp_noun not in unique_comp_nouns:
                                unique_comp_nouns.append(comp_noun)
            for item in unique_comp_nouns:
                match = "".join(item)
                match = re.sub(" ", '_', match).strip()
                action_constraint = [item]

        match_quotes = re.compile('[\"|\'](.+?)[\"|\']').search(doc.text)
        if match_quotes:
            match_quotes_text = re.sub('[\"|\']', '', match_quotes.group(0))
            match_quotes_text = "".join(match_quotes_text)
            match_quotes_text = re.sub(" ", '_', match_quotes_text).strip()
            action_constraint = [match_quotes_text]

    if action_type == 'bool_action':
        nsubj = ''
        child_sub = ''
        bool_constraint = ''
        for chunk in doc.noun_chunks:
            # print(chunk, chunk.root, chunk.root.dep_)
            if chunk.root.dep_ == 'nsubj' or chunk.root.dep_ == 'nsubjpass' or \
                    chunk.root.dep_ == 'dobj' or chunk.root.dep_ == 'pobj':
                chunk_root = chunk.root
                for token in doc:
                    if token.dep_ == 'ROOT':
                        for child in token.children:
                            if child.text == chunk_root.text:
                                subj = re.sub('\\b[a|A]\\b', '', chunk.text).strip()
                                subj = re.sub('\\b[a|A]n\\b', '', subj).strip()
                                subj = re.sub('\\b[t|T]he\\b', '', subj).strip()
                                subj = re.sub(' ', '_', subj)
                                bool_constraint = subj
                if bool_constraint == '':
                    bool_constraint = chunk.text
        action_constraint.append(bool_constraint)

    return action_constraint


def get_action_and_action_symbol(nlp, doc):
    action = ''
    action_symbol = ''
    action_type = ''
    check_syntax = 0

    matcher = Matcher(nlp.vocab)
    for token in doc:
        if token.dep_ == "ROOT":
            root_verb = token.lemma_
        if token.text == 'if':
            check_syntax = 1

    # ACTION_TYPE: verb_noun
    # This pattern matches 'sends the message', parses the root and noun from it. This is made the ACTION.
    # ACTION is symbolized as 'send_message'. This is the ACTION_SYMBOL.
    # For every action there should be a constraint.
    # The constraint here is made the compund_noun_list obtained. This is the ACTION_CONSTRAINT.
    pattern = [{'LEMMA': root_verb, 'POS': 'VERB'},
               {'OP': '?'},
               {'POS': 'NOUN', 'OP': '+', 'IS_ALPHA': True},
               ]
    matcher.add("Action", None, pattern)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]  # The matched span
        add_token = []
        action_type = 'verb_noun'
        action = ''
        if span.text not in action:
            action = span.text
            for token in nlp(span.text):
                if token.pos_ != "DET" and token.is_alpha == True:
                    if add_token:
                        add_token = ('%s_%s' % (add_token, token.lemma_))
                    else:
                        add_token = '%s' % root_verb

        if add_token not in action_symbol:
            # action_symbol.append(add_token)
            action_symbol = add_token

    # ACTION_TYPE: bool_action
    # This pattern checks if there is a Boolean action like 'is detected(VERB)' or 'is active(ADJ)'.
    # This is then symbolized as 'isDetected', 'isActive' (camel case). This is added as the ACTION_SYMBOL.
    matcher_bool_action = Matcher(nlp.vocab)
    bool_action_pattern = [{'DEP': 'auxpass'},
                           # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                           {'ORTH': 'not', 'OP': '?'},
                           # {'POS': 'VERB', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}},
                           {'POS': 'ADP', 'OP': '!'},
                           ]
    bool_action_pattern_2 = [{'DEP': 'auxpass'},
                             # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                             {'ORTH': 'not', 'OP': '?'},
                             # {'POS': 'ADJ', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}},
                             {'POS': 'ADP', 'OP': '!'},
                             ]

    bool_action_pattern_3 = [{'DEP': 'ROOT'},
                             # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                             {'ORTH': 'not', 'OP': '?'},
                             # {'POS': 'VERB', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}},
                             {'POS': 'ADP', 'OP': '!'},
                             ]
    bool_action_pattern_4 = [{'DEP': 'ROOT'},
                             # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                             {'ORTH': 'not', 'OP': '?'},
                             # {'POS': 'ADJ', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}},
                             {'POS': 'ADP', 'OP': '!'},
                             ]
    bool_action_pattern_5 = [{'DEP': 'ROOT'},
                             # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                             {'ORTH': 'not', 'OP': '?'},
                             # {'POS': 'ADV', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}},
                             {'POS': 'ADP', 'OP': '!'},
                             ]
    bool_action_pattern_6 = [{'DEP': 'ROOT'},
                             # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                             {'ORTH': 'not', 'OP': '?'},
                             # {'POS': 'ADP', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}},
                             {'DEP': 'pobj', 'OP': '!'}
                             ]
    bool_action_pattern_7 = [{'DEP': 'auxpass'},
                             # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                             {'ORTH': 'not', 'OP': '?'},
                             # {'POS': 'VERB', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}}
                             ]
    bool_action_pattern_8 = [{'DEP': 'auxpass'},
                             # {'POS': 'PUNCT', 'OP': '?', "_": {"is_domain_token": False}},
                             {'ORTH': 'not', 'OP': '?'},
                             # {'POS': 'ADJ', 'ORTH': {"REGEX": '$'}, "_": {"is_domain_token": False}}
                             ]
    matcher_bool_action.add("Action", None, bool_action_pattern)
    matcher_bool_action.add("Action", None, bool_action_pattern_2)
    matcher_bool_action.add("Action", None, bool_action_pattern_3)
    matcher_bool_action.add("Action", None, bool_action_pattern_4)
    matcher_bool_action.add("Action", None, bool_action_pattern_5)
    matcher_bool_action.add("Action", None, bool_action_pattern_6)
    matcher_bool_action.add("Action", None, bool_action_pattern_7)
    matcher_bool_action.add("Action", None, bool_action_pattern_8)
    matches = matcher_bool_action(doc)
    add_token = []
    add_obj = []
    for match_id, start, end in matches:
        span = doc[start:end]  # The matched span
        action_type = 'bool_action'
        if span.text not in action:
            action = span.text
            for token in nlp(span.text):
                if token.pos_ == "VERB" or token.pos_ == "ADJ" or token.pos_ == "ADV" or token.pos_ == "ADP" \
                        or token.pos_ == "PROPN":
                    bool_word = token.lemma_  # text
                    if token.pos_ == "PROPN":
                        add_obj.append(bool_word)
                        # add_token.append(bool_word)  # .capitalize())
                    else:
                        add_token.append('%s' % bool_word)  # .capitalize()))
                    for token_2 in doc:
                        if token_2.text == bool_word:
                            for child in token_2.children:
                                if child.dep_ == 'prt':
                                    word_prt = child.text
                                    add_token.append('%s%s' % (bool_word, word_prt))  # .capitalize()
            # if add_token not in action_symbol:
            action_symbol = ''.join(list(dict.fromkeys(add_token)))
            object_ = ''.join(add_obj)
    if action_type != 'verb_noun' and action_type != 'bool_action' and check_syntax == 0:
        action_type = 'simple_verb'

    return action, action_symbol, action_type, object_


def get_subj(nlp, sub_req):
    subj = ''

    doc = nlp(sub_req)
    for chunk in doc.noun_chunks:
        if chunk.root.dep_ == 'nsubj' or chunk.root.dep_ == 'nsubjpass':
            subj = re.sub('\\b[a|A]\\b', '', chunk.text).strip()
            subj = re.sub('\\b[a|A]n\\b', '', subj).strip()
            subj = re.sub('\\b[t|T]he\\b', '', subj).strip()
            subj = re.sub(' ', '_', subj)

    if subj == '':
        for token in doc:
            if token.dep_ == 'nsubj' or token.dep_ == 'nsubjpass':
                subj = token.text

    return subj


def get_obj(nlp, sub_req):
    obj = ''

    doc = nlp(sub_req)
    for chunk in doc.noun_chunks:
        if chunk.root.dep_ == 'pobj' or chunk.root.dep_ == 'dobj':
            obj = re.sub('\\b[a|A]\\b', '', chunk.text).strip()
            obj = re.sub('\\b[a|A]n\\b', '', obj).strip()
            obj = re.sub('\\b[t|T]he\\b', '', obj).strip()
            obj = re.sub(' ', '_', obj)

    if obj == '':
        for token in doc:
            if token.dep_ == 'dobj' or token.dep_ == 'pobj':
                obj = token.text

    return obj


def identify_verb(nlp, sub_requirement):
    doc = nlp(sub_requirement)

    transitive_flag = 0
    dative_flag = 0
    intensive_flag = 0
    extensive_flag = 0
    prepositional_flag = 0
    negative_flag = 0
    intensive_flag_neg = 0

    for token in doc:
        if token.text == 'than':
            intensive_flag_neg = 1
        if token.dep_ == 'ROOT':
            for child in token.children:
                if child.dep_ == 'dobj':
                    transitive_flag = 1
                if child.dep_ == 'acomp' or child.dep_ == 'attr':
                    intensive_flag = 1
                if child.dep_ == 'advmod':
                    extensive_flag = 1
                if child.dep_ == 'prep':
                    dative_flag = 1
                if child.dep_ == 'advcl':
                    prepositional_flag = 1
        if token.dep_ == 'neg':
            negative_flag = 1

    verb_type = []
    if transitive_flag == 1:
        verb_type.append("Transitive")
    if transitive_flag == 0:
        verb_type.append("Intransitive")
    if dative_flag == 1:
        verb_type.append("Dative")
    if intensive_flag == 1 and intensive_flag_neg == 0:
        verb_type.append("Intensive")
    if extensive_flag == 1:
        verb_type.append("Extensive")
    if prepositional_flag == 1:
        verb_type.append("Prepositional")
    if negative_flag == 1:
        verb_type.append("Negative")

    return verb_type


def parse_syntax(nlp, req):
    action, action_symbol, action_constraint, action_type, obj = parse_context_mod(nlp, req)
    verb_type = identify_verb(nlp, req)
    subj = get_subj(nlp, req)
    if obj == '':
        obj = get_obj(nlp, req)

    syntax = Syntax(subj=subj, obj=obj,
                    action=action, action_symbol=action_symbol, action_constraint=action_constraint,
                    action_type=action_type,
                    verb_type=verb_type
                    )
    return syntax

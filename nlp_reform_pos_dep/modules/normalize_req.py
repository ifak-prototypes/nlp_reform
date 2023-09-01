import re
from spacy.matcher import Matcher


def normalize_req(nlp, decomposed_sub_req):
    norm_sub_req = []
    for sub_req in decomposed_sub_req:
        ob_of_root_match_flag = 0
        quotes_match_flag = 0
        doc = nlp(sub_req)
        matcher = Matcher(nlp.vocab)
        # These patterns match with 'temperature of the battery' and replaces the word with
        # 'battery_temperature' in the sub-requirement.
        pattern = [{'DEP': 'nsubj'},
                    {'ORTH': 'of'},
                    {'POS': 'DET', 'OP': '?'},
                   {'POS': 'NOUN', 'OP': '?'},
                    {'ORTH': 'of', 'OP': '?'},
                    {'POS': 'DET', 'OP': '?'},
                    {'POS': 'NOUN', 'OP': '+'}
                    ]
        pattern_2 = [{'DEP': 'nsubj'},
                    {'ORTH': 'of'},
                    {'POS': 'DET', 'OP': '?'},
                    {'POS': 'PROPN', 'OP': '+'}
                    ]
        pattern_3 = [{'DEP': 'nsubjpass'},
                    {'ORTH': 'of'},
                    {'POS': 'DET', 'OP': '?'},
                    {'POS': 'NOUN', 'OP': '+'}
                    ]
        pattern_4 = [{'DEP': 'pobj'},
                    {'ORTH': 'of'},
                    {'POS': 'DET', 'OP': '?'},
                    {'POS': 'NOUN', 'OP': '+'}
                    ]
        pattern_5 = [{'DEP': 'pobj'},
                    {'ORTH': 'of'},
                    {'POS': 'DET', 'OP': '?'},
                    {'POS': 'PROPN', 'OP': '+'}
                    ]
        pattern_6 = [{'DEP': 'dobj'},
                    {'ORTH': 'of'},
                    {'POS': 'DET', 'OP': '?'},
                    {'POS': 'NOUN', 'OP': '+'}
                    ]
        matcher.add("Action", None, pattern)
        matcher.add("Action", None, pattern_2)
        matcher.add("Action", None, pattern_3)
        matcher.add("Action", None, pattern_4)
        matcher.add("Action", None, pattern_5)
        matcher.add("Action", None, pattern_6)
        matches = matcher(doc)
        sub_clause_list = []
        if matches:
            for match_id, start, end in matches:
                span = doc[start:end]  # The matched span
                sub_clause_list.append(span.text.strip())

        if sub_clause_list:
            sub_clause = max(sub_clause_list, key=len)

            first_word_ = []
            for token in nlp(sub_clause):
                if token.dep_ == "pobj": # pobj will always be 'device', 'battery', etc. - of which the root belongs
                    first_word_.append(token.text)

            if len(first_word_) == 2:
                first_word = first_word_[1] + "_" + first_word_[0]
            else:
                first_word = first_word_[0]

            first_word_comp_ = []
            for word in first_word_:
                for token in nlp(sub_clause):
                    if token.text == word:
                        for child in token.children:
                            if child.dep_ == 'compound':
                                first_word_comp_.append(child.text + '_' + token.text)

            if len(first_word_comp_) == 2:
                first_word = first_word_comp_[1] + "_" + first_word_comp_[0]

            for token in nlp(sub_clause):
                if token.dep_ == "ROOT": # root will always be 'temperature', 'pressure', etc.
                    second_word = token.text
            new_word = first_word + "_" + second_word

            new_sub_req = re.sub(span.text, new_word, sub_req)
            ob_of_root_match_flag = 1
            norm_sub_req.append(new_sub_req)

        # This pattern checks if there are words in double quotes. If yes, they are made word_word (with
        # underscores). So they can be treated as nouns. These words are replaced in the sub-requirement.
        matcher_quotes = Matcher(nlp.vocab)
        quotes_pattern = [{'ORTH': '"'},
                          {'OP': '+'},
                          {'ORTH': '"'}
                         ]
        matcher_quotes.add("Action", None, quotes_pattern)
        matches_quotes = matcher_quotes(doc)
        if matches_quotes:
            for match_id, start, end in matches_quotes:
                span = doc[start:end]  # The matched span
            new_word = re.sub(' ', '_', span.text)
            new_sub_req = re.sub(span.text, new_word, sub_req)
            quotes_match_flag = 1
            norm_sub_req.append(new_sub_req)

        # If no matches found in either cases, the input sub-requirement is itself appended as
        # the normalized sub-requirement.
        if ob_of_root_match_flag == 0 and quotes_match_flag == 0:
            norm_sub_req.append(sub_req)
    return norm_sub_req

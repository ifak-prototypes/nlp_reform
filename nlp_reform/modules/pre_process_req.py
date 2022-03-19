import re
import spacy
from spacy.matcher.matcher import Matcher

nlp = spacy.load("en_core_web_sm")


def remove_square_brackets(req):
    """
    removes square brackets in the req
    """
    req = re.sub("\[", "", req)
    req = re.sub("\]", "", req)
    return req


def clean_newlines(req):
    """
    replaces newline characters with a space
    """
    req = re.sub("\r\n", "\n", req)
    req = re.sub("\n\n", "\n", req)
    req = re.sub("\n", " ", req)
    return req


def process_attr_in_square_brackets(req):
    """
    replaces attributes in [] with XX
    """
    req = re.sub("\[.*\]", "XX", req)
    return req


def process_events_in_quotes(req):
    """
    replaces events in [] with XX
    """
    new_req = ""
    event_names = []
    doc = nlp(req)
    matcher_quotes = Matcher(nlp.vocab)
    quotes_pattern = [{'ORTH': '"'},
                      {'OP': '+'},
                      {'ORTH': '"'}
                      ]
    quotes_pattern_2 = [{'ORTH': "'"},
                        {'OP': '+'},
                        {'ORTH': "'"}
                        ]
    #matcher_quotes.add("Action", None, quotes_pattern)
    #matcher_quotes.add("Action", None, quotes_pattern_2)
    matcher_quotes.add("Action", [quotes_pattern])
    matcher_quotes.add("Action", [quotes_pattern_2])
    matches_quotes = matcher_quotes(doc)
    if matches_quotes:
        span = ""
        for match_id, start, end in matches_quotes:
            span = doc[start:end]  # The matched span
        # new_word = re.sub(" ", 'decomp', span.text)
        new_req = re.sub(span.text, "XX", req)  # substituting word with XX
        new_req = re.sub("'", "", new_req)
        new_req = re.sub('"', "", new_req)
        event_names.append(span.text)

    if new_req:
        return new_req, event_names
    else:
        return req, event_names

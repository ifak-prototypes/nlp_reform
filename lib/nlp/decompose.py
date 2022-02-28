from lib.models import Clause, Requirement, DecompositionResult
from typing import List
import re

conditions = [
    'if',
    'when',
    'until',
    'while',
    'combined',
]

conjunctions = [
    'and',
    'or',
    'but',
]

class Span:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def lookup(self, source: str) -> str:
        return source[self.start:self.end]

def tokenize(text: str) -> List[Span]:
    """
    Splits a text into words and punctuation
    """
    result = []
    it = re.finditer(r"[\.\,\n]|[^\s\.\,\n]+", text, re.MULTILINE)
    for match in it:
        result.append(Span(match.start(), match.end()))
    return result

def split_if(spans: List[Span], predicate) -> List[Span]:
    result = []
    newSpan = True
    for span in spans:
        if predicate(span):
            newSpan = True
            continue # discard span, it is a separator
        if newSpan:
            result.append(span)
            newSpan = False
        else:
            result[len(result) - 1].end = span.end
    return result

def decompose(requirement: Requirement) -> DecompositionResult:
    tokens = tokenize(requirement.description)
    def predicate(span):
        s = span.lookup(requirement.description).lower()
        return s in conjunctions or s in conditions or s in [',', '.', '\n']
    spans = split_if(tokens, predicate)

    clauses = [ Clause(
        requirement.description[span.start:span.end],
        span.start, span.end
        )
        for span in spans
    ]
    return DecompositionResult(
        clauses = clauses,
        conjunctions = [''] * (len(clauses)-1)
    )
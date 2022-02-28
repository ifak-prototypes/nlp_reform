import re
from typing import List, Optional, Union

from lib.models import Clause, SignalDetectionResult, Parameter, TrueParameter, FalseParameter


def detect_single_parameter(clause: Clause, spacy_nlp) -> Union[bool, str]:
    result = re.search(r"\[([A-Za-z0-9_]+)\]", clause.text)
    if result:
        param = result.group(1)
    else:
        doc = spacy_nlp(clause.text)
        text_chunk = []
        for chunk in doc.noun_chunks:
            text_chunk.append(chunk.text)
        try:
            param = text_chunk[1]
        except:
            param = True
    return param


def detect_boolean_parameter(clause: Clause, detected_signals: List[SignalDetectionResult], threshold: float = 0.2) -> bool:
    no_list = [' no ', ' not ', 'No', 'Not']
    signal = detected_signals[0].signal
    score = detected_signals[0].score

    clause_neg = any(keyword in clause.text for keyword in no_list)
    desc_neg = any(keyword in signal.description for keyword in no_list)

    if clause_neg or desc_neg:
        # negation rule
        if clause_neg and desc_neg:
            param = True
        elif not clause_neg and not desc_neg:
            param = True
        elif clause_neg and not desc_neg:
            param = False
        else:
            param = False
    else:
        # thresholding the signal detection similarity score
        if score > threshold:
            param = True
        else:
            param = False

    return param


def detect_parameter(parameters: List[Parameter], clause: Clause, detected_signals: List[SignalDetectionResult],
                     spacy_nlp) -> Optional[Parameter]:

    if len(detected_signals) == 0:
        return None

    signal = detected_signals[0].signal
    if signal.type == 'boolean':
        bool_value = detect_boolean_parameter(clause, detected_signals)
        if bool_value:
            return TrueParameter
        else:
            return FalseParameter

    if signal.type == 'single':
        param = detect_single_parameter(clause, spacy_nlp)
        if param == True:
            return TrueParameter
        try:
            return parameters[param]
        except KeyError:
            return None
    
    return None 

def detect_parameters(
        parameters: List[Parameter],
        clauses: List[Clause],
        detected_signals: List[SignalDetectionResult],
        spacy_nlp
    ) -> Optional[Parameter]:
    if len(clauses) != len(detected_signals):
        raise ValueError("length missmatch")
    return [ detect_parameter(parameters, clauses[i], detected_signals[i], spacy_nlp) for i in range(len(clauses))]

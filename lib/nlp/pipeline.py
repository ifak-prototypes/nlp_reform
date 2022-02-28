from typing import List, Union

from lib.models import Architecture, DecompositionResult, Operator, Requirement, Signal, Parameter, PipelineResult, SignalDetectionResult, SoftwareComponent
import json
from lib import serialization
import spacy

def load_spacy():
    try:
        return spacy.load('en_core_web_sm')
    except:
        # In release, the spacy model is stored in a diffrent path,
        # so we need to specify this directly, here
        return spacy.load('en_core_web_sm/en_core_web_sm-3.2.0')

def load_requirement(row_or_object: Union[dict, Requirement], architecture: Architecture):
    # When running from interface.py
    if isinstance(row_or_object, Requirement):
        return row_or_object
    
    # When running using "pipeline.py evaluate"
    if isinstance(row_or_object, dict):
        return serialization.requirement_from_dict(row_or_object, architecture)

    # Illegal operation
    raise Exception("row_or_object must be either a dict or a Requirement object")

def load_architecture(path_or_object: Union[str, Architecture]) -> Architecture:
    # When running from interface.py
    if isinstance(path_or_object, Architecture):
        return path_or_object
    
    # When running using "pipeline.py evaluate"
    if isinstance(path_or_object, str):
        data = json.load( open(path_or_object, "r"))
        return serialization.architecture_from_dict(data)
    
    # Illegal operation
    raise Exception("path_or_object must be either a path or an Architecture object")

def collect(clauses: DecompositionResult, signals: List[List[SignalDetectionResult]], parameters: List[Parameter], operators: List[Operator]) -> PipelineResult:
    assert len(clauses.clauses) == len(signals)
    assert len(clauses.clauses) == len(parameters)
    assert len(clauses.clauses) == len(operators)
    result = PipelineResult()
    for i in range(len(clauses.clauses)):
        result.clauses.append(PipelineResult.Clause(
            clauses.clauses[i],
            signals[i][0].signal if signals[i] else None,
            parameters[i] if parameters[i] else None,
            operators[i]
        ))
    result.conjunctions = clauses.conjunctions
    return result   

def to_json(result: PipelineResult, requirement: Requirement) -> dict:
    return {
        'requirement_id': requirement.id,
        'clauses': [
            {
                'text': i.clause.text,
                'signal': i.signal.id if i.signal else None,
                'operator': i.operator.value if i.operator else None,
                'parameter': i.parameter.id if i.parameter else None,
            }
            for i in result.clauses
        ]
    }

def filter_signals(
    architecture: Architecture,
    allowed_components: List[SoftwareComponent],
    allowed_types = List[str]
):
    result = {}
    for component in allowed_components:
        try:
            signals = architecture.signals_by_component[component.id]
        except KeyError:
            continue
        for signal in signals:
            if signal.type in allowed_types:
                result[signal.id] = signal
    return result

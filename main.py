#! /usr/bin/env python3

import json
import os
from lib.nlp.detect_signals import detect_signals
from lib.nlp.detect_parameter import detect_parameters
from lib.nlp.detect_operators import detect_operators, load_operator_symbols
from lib.nlp.decompose import decompose
from lib.nlp.pipeline import load_architecture, filter_signals, load_requirement, collect, to_json, load_spacy

script_dir = os.path.dirname(os.path.realpath(__file__))

requirements = json.load(open(os.path.join(script_dir, "data", "requirements.json")))
architecture = load_architecture(os.path.join(script_dir, "data", "architecture.json"))

spacy = load_spacy()
operator_symbols = load_operator_symbols()
results = []
for requirement_raw in requirements:
    requirement = load_requirement(requirement_raw, architecture)
    filtered_signals = filter_signals(architecture, requirement.components, ['boolean', 'single'])
    clauses = decompose(requirement)
    signals = detect_signals(architecture.signals, clauses.clauses, spacy)
    parameters = detect_parameters(architecture.parameters, clauses.clauses, signals, spacy)
    operators = detect_operators(clauses.clauses, spacy, operator_symbols)
    result = collect(clauses, signals, parameters, operators)
    results.append(to_json(result, requirement))

json.dump(results, open(os.path.join(script_dir, "results.json"), "w"), indent=4)
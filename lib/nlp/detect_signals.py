import numpy as np
from typing import List, Dict
from thefuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from lib.models import Architecture, Signal, Clause, SignalDetectionResult


def get_tf_scores(clause, description_list, spacy_nlp):
    """
    get TF similarity scores
    """

    def normalize(text):
        doc = spacy_nlp(text)
        return [i.lemma for i in doc]

    text = description_list + [clause]
    vectorizer = TfidfVectorizer(tokenizer=normalize, use_idf=False, sublinear_tf=False, norm='l2')
    vectors = vectorizer.fit_transform(text)
    signals_vectors = vectors[:-1]
    clause_vector = vectors[-1:]
    sim_scores = [cosine_similarity(i.reshape([1, -1]), clause_vector)[0][0] for i in signals_vectors]
    return np.asarray(sim_scores)


def get_fw_score(clause, signal_list):
    """
    get Fuzzy-Wuzzy similarity scores with Token Set ratio
    """
    sim_scores = [fuzz.token_set_ratio(clause, i) for i in signal_list]
    return np.asarray(sim_scores)/100


def get_description_list(signals: List[Signal]):
    return [signals[signal].description for signal in signals]


def detect_signals_single(signals: Dict[str, Signal], clause: Clause, min_score: float, spacy_nlp) -> List[SignalDetectionResult]:
    """
    detect signals from the clause given a list of signal descriptions.
    num_signals: number of similar signals to be returned
    """
    description_list = get_description_list(signals)
    tf_scores = get_tf_scores(clause=clause.text, description_list=description_list, spacy_nlp=spacy_nlp)
    fw_scores = get_fw_score(clause=clause.text, signal_list=description_list)
    # adds the similarity scores of tf and fw, then averages it
    #scores = (tf_scores + fw_scores) / 2
    scores = [ min(tf, fw) for tf, fw in zip(tf_scores, fw_scores)]

    # returning the top 5 signals. pass num_signals as required
    if min_score < 0:
        raise ValueError("min_score must be a positive value")

    result = [
        SignalDetectionResult(
            signals[signal],
            scores[idx]
        )
        for idx, signal in enumerate(signals)
        if scores[idx] > min_score
    ]

    result.sort(key = lambda x: x.score, reverse=True)
    return result

def detect_signals(signals: Dict[str, Signal], clauses: List[Clause], spacy_nlp, min_score: float = 0.2) -> List[List[SignalDetectionResult]]:
    return [ detect_signals_single(signals, clause, min_score, spacy_nlp) for clause in clauses ]

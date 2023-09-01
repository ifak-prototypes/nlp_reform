import numpy as np
import spacy
import re
# from allennlp.predictors.predictor import Predictor
# from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nlp_reform_sem_sim.modules import util

# predictor_SA = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models"
#                                    "/basic_stanford_sentiment_treebank-2020.06.09.tar.gz")
# predictor_TE = Predictor.from_path(
#     "https://storage.googleapis.com/allennlp-public-models/decomposable-attention-elmo-2020.04.09.tar.gz")
# embedder = SentenceTransformer('paraphrase-distilroberta-base-v1')


def get_bert_score(clause, signal_desc, models):
    s1 = models.embedder.encode(clause)
    s2 = models.embedder.encode(signal_desc)
    s = cosine_similarity(s1.reshape(1, -1), s2.reshape(1, -1))[0][0]
    return s


def textual_entailment(clause, signal_desc, models):
    no_list = [' no ', ' not ', 'No', 'Not']
    value = models.predictor_TE.predict(
        premise=signal_desc,
        hypothesis=clause
    )
    label = np.argmax(value['label_probs'])#[:2])
    if label == 0:
        pred_val = 'TRUE'
    elif label == 1:
        pred_val = 'FALSE'
    else:
        if any(keyword in clause for keyword in no_list) and any(
                keyword in signal_desc for keyword in no_list):
            pred_val = 'TRUE'
        elif any(keyword in clause for keyword in no_list) and not any(
                keyword in signal_desc for keyword in no_list):
            print(clause, signal_desc)
            pred_val = 'FALSE'
        elif not any(keyword in clause for keyword in no_list) and not any(
                keyword in signal_desc for keyword in no_list):
            pred_val = 'TRUE'
        else:
            pred_val = 'FALSE'

    return pred_val


def sentiment_analyser(clause, signal_desc, models):
    result_clause = models.predictor_SA.predict(clause)
    result_signal = models.predictor_SA.predict(signal_desc)
    sentiment_clause = result_clause["label"]
    sentiment_signal = result_signal["label"]

    parameter = 'FALSE'
    if sentiment_signal == sentiment_clause:
        parameter = 'TRUE'

    return parameter


def score_threshold(score, threshold=0.6):
    if score < threshold:
        return 'FALSE'
    else:
        return 'TRUE'


def get_parameter_value(clause, signal, score, models):
    no_list = [' no ', ' not ', 'No', 'Not']

    try:
        param_detection = models.config['param_detection']
    except:
        param_detection = 'PD'

    param = ''
    if signal['data_type'] == 'boolean':
        if param_detection == 'TE':
            param = textual_entailment(clause, signal['desc'], models)
        elif param_detection == 'PD':
            score = get_bert_score(clause, signal['desc'], models)
            param = score_threshold(score)
        elif param_detection == 'SA':
            param = sentiment_analyser(clause, signal['desc'], models)

    else:
        result = re.search(r"\[([A-Za-z0-9_]+)\]", clause)
        if result:
            param = result.group(1)
        else:
            doc = models.spacy_nlp(clause)
            text_chunk = []
            for chunk in doc.noun_chunks:
                text_chunk.append(chunk.text)
            try:
                param = text_chunk[1]
                param = param.replace('a ', '')
            except:
                param = 'TRUE'

    return param

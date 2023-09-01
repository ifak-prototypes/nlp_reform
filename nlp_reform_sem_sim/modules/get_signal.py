import nltk
import numpy as np
import string
# from fuzzywuzzy import fuzz
# from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
# embedder = SentenceTransformer('paraphrase-distilroberta-base-v1')


def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]


def normalize(text):
    # remove punctuation, lowercase, stem
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))


def get_tf_scores(clause, signal_list, models):
    all = signal_list + [clause]
    vectorizer = TfidfVectorizer(tokenizer=normalize,
                                 use_idf=False,
                                 sublinear_tf=False,
                                 norm='l2'
                                 )
    vectors = vectorizer.fit_transform(all)
    signals_vectors = vectors[:-1]
    clause_vector = vectors[-1:]
    sim_scores = [cosine_similarity(i.reshape([1, -1]), clause_vector)[0][0] for i in signals_vectors]

    return np.asarray(sim_scores)


def get_fuzzywuzzy_score(clause, signal_list, models):
    sim_scores = [models.fuzz.token_set_ratio(clause, i)/100 for i in signal_list]

    return np.asarray(sim_scores)


def get_bert_score(clause, signal_list, models):
    s1 = models.embedder.encode(clause)
    # s = cosine_similarity(s1.reshape(1, -1), s2.reshape(1, -1))
    sim_scores = [cosine_similarity(s1.reshape(1, -1), models.embedder.encode(i).reshape(1, -1))[0][0] for i in signal_list]
    return np.asarray(sim_scores)


def get_signal(clause, signals, models):
    signal_list = []
    for msg in signals:
        signal_list.append(msg['desc'])

    try:
        signal_detection = models.config['signal_detection']
    except:
        signal_detection = 'bert+fw'

    signal_detection = signal_detection.split('+')

    sim_scores = []
    if signal_detection[0] == 'tf':
        sim_scores = get_tf_scores(clause, signal_list, models)
    elif signal_detection[0] == 'fw':
        sim_scores = get_fuzzywuzzy_score(clause, signal_list, models)
    elif signal_detection[0] == 'bert':
        sim_scores = get_bert_score(clause, signal_list, models)

    if len(signal_detection) != 1 and signal_detection[1] == 'fw':
        sim_scores_fs = get_fuzzywuzzy_score(clause, signal_list, models)
        for i in range(len(sim_scores)):
            sim_scores[i] += sim_scores_fs[i]
            sim_scores[i] = sim_scores[i] / 2

    index = sim_scores.argsort()[-1:][::-1][0]

    return signals[index], sim_scores[index]

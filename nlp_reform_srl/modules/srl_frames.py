from allennlp.predictors.predictor import Predictor
from allennlp.data.dataset_readers.dataset_utils.span_utils import bio_tags_to_spans


def get_span_from_frame(frame):
    span = " ".join([role['span'] for role in frame])
    return span


class SemFrames:
    def __init__(self, path=None):
        self.path = path
        self.not_verb_list = ['shall', 'be', 'max']
        if not self.path:
            self.path = "https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12" \
                        ".15.tar.gz"
        try:
            self.predictor = Predictor.from_path(self.path)
        except FileNotFoundError as e:
            print("Check input path. Input", e.args[0])

    def get_frames(self, text):
        pred = self.predictor.predict(sentence=text)
        words = pred['words']
        verbs = pred['verbs']
        frames = []  # this holds the frames for the text, of all the verbs

        for verb in verbs:
            if verb['verb'] in self.not_verb_list:
                continue
            args = bio_tags_to_spans(verb['tags'])
            if len(args) <= 2:   # filter out SRL frames with arguments <= 2
                continue
            frame_arg = {}
            for arg in args:
                role = arg[0]
                indices = arg[1]
                span_text = " ".join(words[indices[0]:indices[1] + 1])

                frame_arg[role] = span_text

            frames.append(frame_arg)
        return frames

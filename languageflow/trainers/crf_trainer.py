import logging
import pycrfsuite

from languageflow.models.crf_sequence_tagger import CRFSequenceTagger
from languageflow.transformer.tagged import TaggedTransformer

log = logging.getLogger('languageflow')


class CRFTrainer:
    def __init__(self, tagger: CRFSequenceTagger, corpus):
        self.tagger = tagger
        self.corpus = corpus

    def train(self, params):
        features = self.tagger.features
        print(features)
        transformer = TaggedTransformer(features)
        log.info("Start feature extraction")
        X_train, y_train = transformer.transform(self.corpus.train, contain_labels=True)
        X_train, y_train = X_train[:10000], y_train[:10000]
        X_test, y_test = transformer.transform(self.corpus.test, contain_labels=True)
        log.info("Finish feature extraction")

        # Train
        log.info("Start train")
        trainer = pycrfsuite.Trainer(verbose=True)
        for xseq, yseq in zip(X_train, y_train):
            trainer.append(xseq, yseq)
        trainer.set_params(params)
        filename = 'tmp/model.tmp'
        trainer.train(filename)
        logger.info("Finish train")

        # Tagger
        logger.info("Start tagger")
        tagger = pycrfsuite.Tagger()
        tagger.open(filename)
        y_pred = [tagger.tag(x_seq) for x_seq in X_test]
        sentences = [[item[0] for item in sentence] for sentence in self.corpus.test]
        sentences = zip(sentences, y_test, y_pred)
        texts = []
        for s in sentences:
            tokens, y_true, y_pred = s
            tokens_ = ["\t".join(item) for item in zip(tokens, y_true, y_pred)]
            text = "\n".join(tokens_)
            texts.append(text)
        text = "\n\n".join(texts)
        open("tmp/output.txt", "w").write(text)
        evaluate_("tmp/output.txt")
        logger.info("Finish tagger")

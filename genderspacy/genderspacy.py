import spacy
from spacy import displacy
from spacy.tokens import Doc

import itertools
import pathlib
from typing import List, Union

import requests
import tqdm  # progress bar

import srsly
from . import components
import toml

import os
from pathlib import Path
from distutils.sysconfig import get_python_lib

BASE_DIR = None
if os.path.isfile(get_python_lib() + "/genderspacy"):
  BASE_DIR = get_python_lib() + "/genderspacy"
else:
  BASE_DIR = os.path.dirname(__file__)

pronoun_patterns = BASE_DIR + "/data/pronoun_patterns"
pronoun_patterns = list(srsly.read_jsonl(pronoun_patterns))

project_toml = BASE_DIR + "/data/project.toml"
project_data = toml.load(project_toml)

colors = project_data["colors"]
visualize_params = project_data["visualize_params"]
visualize_params["colors"] = colors

from allennlp.predictors.predictor import Predictor


class GenderParser:
    def __init__(self, model_name):
        coref_model = CrossLingualPredictor(model_name)
        nlp = spacy.load(model_name)

        nlp.add_pipe("pronoun_resolver")
        ruler = nlp.add_pipe("span_ruler")
        nlp.add_pipe("pronoun_id")
        nlp.add_pipe('people_and_spouse')
        ruler.add_patterns(pronoun_patterns)
        self.nlp = nlp
        self.coref_model = coref_model
    def process_doc(self, text):
        doc = self.nlp(text)

        original_spans  = list(doc.spans["ruler"])
        for ent in doc.ents:
            if ent.label_=="PERSON":
                ent.label_ = "PERSON_UNKNOWN"
                original_spans.append(ent)
        doc.spans["ruler"] = original_spans
        self.doc = doc
        return doc
    def coref_resolution(self):

        coref_res = self.coref_model.predict(self.doc.text)
        cluster_texts = []
        for cluster in coref_res:
            texts = []
            for hit in cluster:
                start, end = hit
                texts.append(self.doc[start:end+1].text)
            cluster_texts.append(texts)

        original_spans = list(self.doc.spans["ruler"])
        for span in original_spans:
            if span.label_ in ["PERSON_NEUTRAL", "PERSON_UNKNOWN", "PERSON"]:
                for cluster in cluster_texts:
                    if span.text in cluster:
                        for hit in cluster:
                            if hit.lower() in ["he", "his", "him", "himself"]:
                                span.label_ = "PERSON_MALE_COREF"
                            elif hit.lower() in ["she", "her", "hers", "herself"]:
                                span.label_ = "PERSON_FEMALE_COREF"
        self.doc.spans["ruler"] = original_spans
        return self.doc
    def visualize(self, jupyter=True):
        if jupyter==True:
            displacy.render(self.doc, style="span", options=visualize_params, jupyter=True)
        else:
            displacy.render(self.doc, style="span", options={"spans_key": "ruler"})
            
MODELS = {
    "xlm_roberta": {
        "url": "https://storage.googleapis.com/pandora-intelligence/models/crosslingual-coreference/xlm-roberta-base/model.tar.gz",  # noqa: B950
        "f1_score_ontonotes": 74,
        "file_extension": ".tar.gz",
    },
    "info_xlm": {
        "url": "https://storage.googleapis.com/pandora-intelligence/models/crosslingual-coreference/infoxlm-base/model.tar.gz",  # noqa: B950
        "f1_score_ontonotes": 77,
        "file_extension": ".tar.gz",
    },
    "minilm": {
        "url": (
            "https://storage.googleapis.com/pandora-intelligence/models/crosslingual-coreference/minilm/model.tar.gz"
        ),
        "f1_score_ontonotes": 74,
        "file_extension": ".tar.gz",
    },
    "spanbert": {
        "url": "https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz",
        "f1_score_ontonotes": 83,
        "file_extension": ".tar.gz",
    },
}
# This class comes from https://github.com/pandora-intelligence/crosslingual-coreference
# I have modified this class minimally to fit into this project and align with spaCy 3.4.1
class CrossLingualPredictor(object):
    def __init__(
        self,
        language: str,
        device: int = -1,
        model_name: str = "spanbert",
        chunk_size: Union[int, None] = None,  # determines the # sentences per batch
        chunk_overlap: int = 2,  # determines the # of overlapping sentences per chunk
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.language = language
        self.filename = None
        self.device = device
        self.model_url = MODELS[model_name]["url"]
        # self.resolver = Resolver()
        self.download_model()
        self.set_coref_model()

    def download_model(self):
        """
        It downloads the model from the url provided and saves it in the current directory
        """
        if "https://storage.googleapis.com/pandora-intelligence/" in self.model_url:
            self.filename = self.model_url.replace("https://storage.googleapis.com/pandora-intelligence/", "")
        else:
            self.filename = self.model_url.replace("https://storage.googleapis.com/allennlp-public-models/", "")
        path = pathlib.Path(self.filename)
        if path.is_file():
            pass
        else:
            path.parent.absolute().mkdir(parents=True, exist_ok=True)
            r = requests.get(self.model_url, stream=True)
            file_size = int(r.headers["Content-Length"])

            chunk_size = 1024
            num_bars = int(file_size / chunk_size)

            with open(self.filename, "wb") as fp:
                for chunk in tqdm.tqdm(
                    r.iter_content(chunk_size=chunk_size),
                    total=num_bars,
                    unit="KB",
                    desc=self.filename,
                    leave=True,
                ):
                    fp.write(chunk)

    def set_coref_model(self):
        """Initialize AllenNLP coreference model"""
        self.predictor = Predictor.from_path(self.filename, language=self.language, cuda_device=self.device)

    def predict(self, text: str) -> dict:
        """predict and rsolve
        Args:
            text (str): an input text
            uses more advanced resolve from:
            https://towardsdatascience.com/how-to-make-an-effective-coreference-resolution-model-55875d2b5f19.
        Returns:
            dict: a prediciton
        """
        # chunk text
        doc = self.predictor._spacy(text)
        if self.chunk_size:
            chunks = self.chunk_sentencized_doc(doc)
        else:
            chunks = [text]

        # make predictions for individual chunks
        json_batch = [{"document": chunk} for chunk in chunks]
        predictions = self.predictor.predict_batch_json(json_batch)

        # determine doc_lengths to resolve overlapping chunks
        doc_lengths = [
            sum([len(sent) for sent in list(doc_chunk.sents)[:-2]]) for doc_chunk in self.predictor._spacy.pipe(chunks)
        ]
        doc_lengths = [0] + doc_lengths[:-1]

        # convert cluster predictions to their original index in doc
        all_clusters = [pred["clusters"] for pred in predictions]
        corrected_clusters = []
        for idx, doc_clus in enumerate(all_clusters):
            corrected_clusters.append(
                [[[num + sum(doc_lengths[: idx + 1]) for num in span] for span in clus] for clus in doc_clus]
            )
        merged_clusters = self.merge_clusters(corrected_clusters)
        return merged_clusters

    @staticmethod
    def merge_clusters(
        clusters: List[List[List[int]]],
    ) -> List[List[List[int]]]:
        """merge overlapping cluster from different segments, based on n_overlap_sentences"""
        main_doc_clus = []
        for doc_clus in clusters:
            for clus in doc_clus:
                combine_clus = False
                for span in clus:
                    for main_clus in main_doc_clus:
                        for main_span in main_clus:
                            if main_span == span:
                                combined_clus = main_clus + clus
                                combined_clus.sort()
                                combined_clus = list(k for k, _ in itertools.groupby(combined_clus))
                                combine_clus = True
                                break
                        if combine_clus:
                            break
                    if combine_clus:
                        break
                if combine_clus:
                    main_doc_clus.append(combined_clus)
                else:
                    main_doc_clus.append(clus)

        main_doc_clus.sort()
        main_doc_clus = list(k for k, _ in itertools.groupby(main_doc_clus))
        return main_doc_clus

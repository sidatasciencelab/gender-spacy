import spacy
from spacy import displacy
from spacy.tokens import Doc, Span

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

pronouns = project_data["pronouns"]


class GenderParser:
    """
    Args:
        model_name (str): the spaCy model you wish to use, e.g. en_core_web_lg
    """
    def __init__(self, model_name):
        try:
            nlp = spacy.load(model_name)
        except:
            OSError
            print(f"Downloading {model_name}...")
            try:
                os.system(f"python -m spacy download {model_name}")
                nlp = spacy.load(model_name)
            except:
                OSError
                raise Exception(f"{model_name} is not a recognized spaCy model.")

        nlp_coref = spacy.load("en_coreference_web_trf")

        # use replace_listeners for the coref components
        nlp_coref.replace_listeners("transformer", "coref", ["model.tok2vec"])
        nlp_coref.replace_listeners("transformer", "span_resolver", ["model.tok2vec"])

        # we won't copy over the span cleaner
        nlp.add_pipe("coref", source=nlp_coref)
        nlp.add_pipe("span_resolver", source=nlp_coref)

        nlp.add_pipe("pronoun_resolver")
        ruler = nlp.add_pipe("span_ruler")
        nlp.add_pipe("pronoun_id")
        nlp.add_pipe('people_and_spouse')
        ruler.add_patterns(pronoun_patterns)
        self.nlp = nlp
    
    def process_doc(self, text):
        """
        Creates the spaCy doc container and iterates over the entities found by the spaCy NER model.
        Args:
            text (str): the text that will be processed.
        
        Returns:
            doc (spaCy Doc): the doc container that contains all the data about gender spans
        """
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
        """
        Uses the spaCy Experimental Coref Model to identify all connections between PERSON entities and pronouns.
        If there is a cluster where a PERSON entity has a gender-specific pronoun, the span labels are adjusted accordingly.
        """
        spans = list(self.doc.spans["ruler"])
        # pronouns = {"female": ["she", "her", "hers", "herself"], "male": ["he", "him", "his", "himself"]}

        def parse_gender(token, pronoun_set, gender):
            if token.text.lower() not in pronoun_set:
                span = self.doc.char_span(token.start_char, token.end_char, label=gender.upper())
                span = Span(self.doc, span.start, span.end, label=f"PERSON_{gender.upper()}_COREF")
                return span

        for key, cluster in self.doc.spans.items():
            if "head" in key:
                head_tokens = [token.text.lower() for token in cluster]
                for gender, pronoun_set in pronouns.items():
                    if any(pronoun in head_tokens for pronoun in pronoun_set):
                        for token in cluster:
                            gender_res = parse_gender(token, pronoun_set, gender.upper())
                            if gender_res != None:
                                num = key.split("_")[-1]
                                res_cluster = self.doc.spans[f"coref_clusters_{num}"]
                                for token_set in res_cluster:
                                    for token2 in token_set:
                                        if token2.pos_ in "PROPN":
                                            span = self.doc.char_span(token2.idx, token2.idx+len(token2.text), label=gender.upper())
                                            span = Span(self.doc, span.start, span.end, label=f"PERSON_{gender.upper()}_COREF")
                                            spans.append(span)
                                        # elif token2.pos_ == "NOUN":
                                        #     span = self.doc.char_span(token2.idx, token2.idx+len(token2.text), label=gender.upper())
                                        #     span = Span(self.doc, span.start, span.end, label=f"REL_{gender.upper()}_COREF")                  
                                        #     spans.append(span)
        def connect_spans(spans):
            for i, span in enumerate(spans):
                for span2 in spans:
                    if span.end == span2.start:
                        if (self.doc[span.start].pos_ and self.doc[span2.start].pos_) == "PROPN":
                            new_span = Span(self.doc, span.start, span.end+1, label=span.label_)
                            spans.append(new_span)
            return spans
        spans = connect_spans(spans)
        # spans = connect_spans(spans)
        final_spans = []
        for span in spans:
            rem = False
            if span.label_ == "PERSON_UNKNOWN":
                for span2 in spans:
                    if span2.start == span.start:
                        rem = True
            if rem == False:
                final_spans.append(span)
        merged_spans = spacy.util.filter_spans(final_spans)
        self.doc.spans["ruler"] = merged_spans
        return self.doc

    def visualize(self, jupyter=True):
        """
        visualizes the spaCy doc Container on the spans
        Args:
            jupyter (Bool): affects if the visualization loads in Jupyter or as HTML
        """
        if jupyter==True:
            displacy.render(self.doc, style="span", options=visualize_params, jupyter=True)
        else:
            displacy.render(self.doc, style="span", options={"spans_key": "ruler"})
            
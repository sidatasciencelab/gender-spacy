import pandas as pd
import spacy
from spacy.language import Language
from spacy.tokens import Token, Span, Doc
import re
import string

import toml
import srsly

import os
from pathlib import Path
from distutils.sysconfig import get_python_lib

BASE_DIR = None
if os.path.isfile(get_python_lib() + "/genderspacy"):
  BASE_DIR = get_python_lib() + "/genderspacy"
else:
  BASE_DIR = os.path.dirname(__file__)

gender_pronoun_file = BASE_DIR + "/data/gender_pronouns.csv"
project_toml = BASE_DIR + "/data/project.toml"
pronoun_patterns = BASE_DIR + "/data/pronoun_patterns"

project_data = toml.load(project_toml)

regex = project_data["regex"]
titles = project_data["titles"]
pipeline_data = project_data["pipeline_data"]


regex_patterns = {}
all_titles = ""
for title_name, title_list in titles.items():
    title_combined = "|".join(title_list)
    all_titles = all_titles+f"{title_combined}|"
    pattern = regex["individual"].replace("<GENDER_TITLES>", title_combined).replace("\\\\", "\\")
    regex_patterns[title_name] = pattern
regex_patterns["spouse"] = regex["spouse"].replace("<GENDER_TITLES>", all_titles).replace("\\\\", "\\")
all_titles = all_titles[:-1]


df = pd.read_csv(gender_pronoun_file)
pronouns = df.values.tolist()

unique_pronouns = []
for p in pronouns:
    for item in p[1:]:
        unique_pronouns.append(item)
unique_pronouns = list(set(unique_pronouns))
unique_pronouns.sort()

@Language.component("people_and_spouse")
def people_and_spouse(doc):
    original_ents = list(doc.spans["ruler"])
    text = doc.text
    for label, pattern in regex_patterns.items():
        if label == "spouse":
            label=f"COLLECTIVE_SPOUSAL"
        else:
            label=f"PERSON_{label.upper()}"
        text = doc.text
        new_ents = []
        for match in re.finditer(pattern, doc.text):
            start, end = match.span()
            span = doc.char_span(start, end, alignment_mode="expand")
            if span != None:
                if span.text[-1] in string.punctuation:
                    span.end = span.end-1
                start, end, name = span.start, span.end, span.text
                tmp_span = Span(doc, start, end, label=label)
                for i, token in enumerate(tmp_span):
                    if i > 2 and doc[(tmp_span.start+i)-2].text not in pattern.replace("\\", ""):
                        if token.is_sent_start == True:
                            tmp_span.end=tmp_span.start+i-1
                original_ents.append(tmp_span)
    doc.spans["ruler"] = original_ents
    return doc

@Language.component("pronoun_id")
def pronoun_id(doc):
    original_spans = list(doc.spans["ruler"])
    new_spans = []
    for span in doc.spans["ruler"]:
        if any(span.text.lower() in p for p in pronouns):
            for option in pronouns:
                if span.text.lower() in option:
                    span.label_ = f"{option[0].upper()}_PRONOUN"
                    new_spans.append(span)
                    break
        else:
            new_spans.append(span)
    doc.spans["ruler"] = new_spans
    return doc

@Language.component("pronoun_resolver")
def pronoun_resolver(doc):
    for i, token in enumerate(doc):
        if any(token.text.lower() in p for p in pronouns):
            if token.text.lower() == "per" and token.pos_ != "PRON":
                if doc[i-1].lemma_ != "as" and token.is_sent_start == False:
                    token.pos_ = "PRON"
                elif doc[i+1].pos_ not in ["PRON", "DET"]:
                    # print(doc[i+1].pos_)
                    token.pos_ = "PRON"
                else:
                    token.pos_ = "ADP"
            else:
                token.pos_ = "PRON"
    return doc

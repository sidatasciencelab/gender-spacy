
![gender spacy logo](https://github.com/sidatasciencelab/gender-spacy/raw/main/images/genderspacy-logo.png)

# About

Gender spaCy is a heuristic and machine learning pipeline that allows users to identify gender in an ethical way using gender-specific context. It is designed to sit alongside a standard spaCy pipeline (only English supported currently). The majority of the pipeline is rules-based, relying on titles and pronouns to identify gender as presented in the text. **It is important to note that this pipeline does not seek to assign gender to an individual, rather contextually identify an entity's gender within the context of a text.**

There are Python libraries, such as gender-resolver that assign gender based on the statistical usage of first names in a given region. This, however, gets into problematic territory and is not as reliable as gender-based context (such as titles and pronouns). As a result, this pipeline opts out of leveraging these libraries. Instead, entities identified as PERSON by the spaCy NER model are altered to the span label of PERSON_UNKNOWN. Next, this pipeline leverages the new experimental coreference resolution model from ExplosionAI. It looks at all clusters of linked tokens. If any of them align with PERSON_UNKNOWN tags *and* gender-specific pronouns are used, the entity's label is changed to a gender-specific label, e.g. PERSON_FEMALE, PERSON_MALE, PERSON_NEUTRAL. In addition, terms that are nouns that are linked to a specific person receive the tag "REL_MALE/FEMALE_COREF".

In addition to this, all gender-neutral pronouns are also identified and labeled as spans. This includes male, female, and gender neutral pronouns. Even transformer models have difficulty correctly parsing certain gender neutral pronouns due to their toponym nature, such as "per" which can function in English as an adverb (Per our discusion yesterday, I want to go to the store.) or as a gender neutral pronoun (Per went to the store yesterday). With a few extra rules, Gender spaCy corrects the POS tags for these toponyms in addition to placing all pronouns in the spans ruler.

Users can access all gender span data under doc.spans["ruler].

# Installation

Because this pipeline leverages spaCy's new experimental coreference resolution model, it is best to install Gender spaCy in a fresh environment.

First, it is good to create a new environment.

```python
conda create --name="gender-spacy" python=3.9
```

Now, activate the environment:

```python
conda activate gender-spacy
```

Next, install GenderSpaCy

```python
pip install gender-spacy
```

Finally, for the pipeline to perform coreference resolution, you should install the latest version of the spaCy experimental coreference resolution model.

```python
pip install https://github.com/explosion/spacy-experimental/releases/download/v0.6.0/en_coreference_web_trf-3.4.0a0-py3-none-any.whl
```



# Usage

```python

# import the library
from gender_spacy import gender_spacy as gs

# create the GenderParser nlp class.
# This will take one argument: the spaCy model you wish to use
nlp = gs.GenderParser("en_core_web_sm")

# create a text and pass it to the the nlp via the process_doc() method.
text = """
During the year Miss Densmore arranged in final order 245 songs to accompany her manuscript on Seminole music and revised portions of the text to conform to this arrangement of the material. 

In December 1941 Miss Densmore was appointed as consultant at The National Archives for work in connection with the Smithsonian Densmore collection of sound recordings of American Indian music, and duiing the ensuing months she was engaged in planning the organization of the collection.
"""
doc = nlp.process_doc(text)

# perform coreference resolution on the doc container
# This part of the library comes from Crosslingual Coreference
doc = nlp.coref_resolution()

# Visualize the result:
nlp.visualize()
```

## Expected Result

![result demo](https://github.com/sidatasciencelab/gender-spacy/raw/main/images/result.JPG)



# CITATIONS
Source for gender pronouns: https://uwm.edu/lgbtrc/support/gender-pronouns/

Source for Coreference Resolution: https://explosion.ai/blog/coref
Discussion for Coref Code: https://github.com/explosion/spaCy/discussions/11585
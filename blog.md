# Identifying Gender in Museum Archives with Machine Learning and Natural Language Processing

Part of the mission of the American Women's History Initiative is to understand better and more wholly the influential role women have played in the Smithsonian's history. There are many sources for this information, but in this blog we will be focusing on documents, or textual data.

Through natural language processing (NLP), we can automate the parsing of documents en masse. We can use machine learning to identify and extract relevant material in sources, such as people, dates, places, etc. These are known as named entities. The identification of named entities is known as named entity recognition (NER). 

There are many off-the-shelf machine learning models that can perform NER and find relevant information for researchers. As it stands, however, there is no reliable and ethical way to identify a person's gender within a text. This blog introduces the ethical and computational challenges to solving such a problem. It also presents a new solution to this issue that we have developed in the Smithsonian Institution's Data Science Lab.

## Background

This project stems from postdoctoral work with the American Women's History Initiative. Part of this project was a collective exploration of the role of women in science at the Smithsonian since its inception.

[The Data Science Lab team explored various solutions for identifying known women in its archives and in specimen record collections](https://womenshistory.si.edu/stories/using-data-science-uncover-work-women-science). We noticed that women's identities were frequently masked in several ways. First, many women in science at the Smithsonian were the spouses of full-time employees. The contribution of these women is sometimes masked, or hidden, by the name of her husband. In this construction, a woman would have her named associated with her husband's first and last name, e.g. *Mrs. Martha and Mr. Mark Smith*. Here, we have the woman's first name and last name. In other instances, however, the issue was more complicated with her first name being entirely removed as in the construction *Mr. and Mrs. Mark Smith*. Another way in which a woman's identity through gender-neutral titles. For example, Dr. Smith could be Dr. Martha Smith or Dr. Mark Smith. In other cases, a woman's name could be hidden behind abbreviations, such as M. Smith. Again, this could refer to either Martha or Mark Smith.

This ambiguity not only clouds the role of women at the Smithsonian, it also directly discredits their own work. In 2019, [Tiana Curry](https://datascience.si.edu/news/whatsinaname), an intern at the Smithsonian, noticed that certain specimen collection records were assigned to Mr. Charles Walcott; the problem was some of these specimen records were dated to after his death. In this case (and others like it), attribution belonged to Walcott's widow, Mary Vaux Walcott.

## The Problem

Over the past year, we have explored various solutions for identifying women in Smithsonian records. There are several Python libraries available to researchers that will use an individual's first name and check it against the country of a document to output the likely gender of the individual. This presents certain serious practical and ethical issues. First, Smithsonian data spans many continents; it is not always easy to identify the country of origin for the entity identified. Second, the museum's records cover nearly two centuries of data. Name usage has changed significantly in that time. Third, and most problematic, is the ethical implications of assigning gender based on the statistical usage of a first name. It presumes far too much about the individual with far too little evidence.

## A Potential Solution

**It is important to note in the methods below we do not presume the gender of the individual through these approaches, rather we simply identify how that individual is referenced within the context of a given text. No data generated is used without manual validation. In other words, we do not presume the gender of the individual, rather identify the gender used in a given text for that individual.**

To solve this issue, we decided to take a context-based approach to identifying women. First, women often receive gender-specific honorofics (Mrs., Miss., Ms.). One component in our pipeline looks for these occurences using Regular Expressions (RegEx) to identify any time a gender-specific honorific is used in a text and followed by a sequence of proper nouns. When an entity is found in a text, we assign a gender-specific tag to that individual. If that individual is identified with female honorifics, we assign the label `FEMALE_PERSON`.

With this same logic, we perform the same task on what we are calling `COLLECTIVE_SPOUSAL` entities, e.g. where a woman's name appears alongisde that of her spouse, e.g. Mrs. and Mr. Smith.

As noted above, there are gender-neutral honorifics, such as  "Dr.". In these cases, we flag these individuals as `PERSON_UNKNOWN`.

Next, we use a machine learning model to identify all other individuals in the text. Since we work with the [spaCy](https://spacy.io/) framework, we look for all entities labeled as `PERSON`. We then assign these entities the label of `PERSON_UNKNOWN`.

In addition to this, we identify all gender pronouns in a text and flag them with a gender-specific label, e.g. FEMALE_PRONOUN.

Finally, we use a coreference resolution model to then examine the text. Corefernece resolution is the clustering of spans, or words, in a document. It matches antecedents and postcedents to heads. Consider the following text:

```
"Anna plays the violin. She likes music."
```

In this case "she" is a pronoun that refers back to "Anna". In coreference resolution, we match these two separate words together as being a cluster of words that represent the same entity.

In our workflow, we look for the usage of a gender-specific pronoun alongside all proper nouns in these clusters. If that proper noun has a label of PERSON_UNKNOWN and aligns with a gender-specific pronoun, we assign a gender-specific label that indicates this label derived from a coreference machine learning model, e.g. `FEMALE_PERSON_COREF`. This is important because these are the attributions that require a closer look.

## Introducing Gender spaCy

In the process of designing this workflow, we also considered the broader applications of such a pipeline. The result is [Gender spaCy](https://github.com/sidatasciencelab/gender-spacy), an open-source Python library built on spaCy for identifying gender-specific data in texts. For those who do not have Python, there is even a free open-source [application in the cloud](https://gender-spacy.streamlit.app/).

![gender spacy logo](images/genderspacy-logo.png)

Gender spaCy allows users with just two lines of Python to automate the parsing of documents and identifying gender-specific data within the text. With a third line, the data can be visualized as the image below demontrates.

![example of pipeline](images/result.JPG)

By relying on gender-specific context (as opposed to assigning gender based on first names), Gender spaCy is more sophisticated than existing approaches to identifying and finding women in documents.

To get started, you can run:

```python
pip install gender-spacy
```
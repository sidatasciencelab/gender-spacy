
# ABOUT

This pipeline allows users to identify gender in an ethical way via NLP and Machine Learning. The majority of the pipeline is rules-based, relying on titles and pronouns to identify gender as presented in the text. Some libraries are available for using an entity's first name to identify gender. This, however, gets into problematic territory. As a result, this pipeline opts out of leveraging these libraries. Instead, entities identified as PERSON by the NER model are altered to the span label of PERSON_UNKNOWN. Next, this pipeline leverages the work of Crosslingual-Coreference Resolution to align AllenNLP's Coref Predictor. Next, this pipeline passes over all clusters. If any of them align with PERSON_UNKNOWN tags *and* gender-specific pronouns are used, the entity's label is changed to a gender-specific label, e.g. PERSON_FEMALE.


# CITATIONS
Source for gender pronouns: https://uwm.edu/lgbtrc/support/gender-pronouns/
Source for Coreference Resolution Class: https://github.com/pandora-intelligence/crosslingual-coreference

# Identifying Gender in Museum Archives with Machine Learning and Natural Language Processing

As it stands, there is no reliable and ethical way to identify a person's gender within a text programmatically via off-the-shelf natural language processing (NLP) solutions. This blog introduces the ethical and computational challenges to solving such a problem. It also presents a new solution to this issue that we have developed in the Smithsonian Institution's Data Science Lab.

## Background

This project stems from postdoctoral work with the American Women's History Initiative. Part of this project was a collective exploration of the role of women in science at the Smithsonian since its inception.

[The Data Science Lab team explored various solutions for identifying known women in its archives and in specimen record collections](https://womenshistory.si.edu/stories/using-data-science-uncover-work-women-science). We noticed that women's identities were frequently masked in several ways. First, many women in science at the museum were the spouses of men who were full-time employees of the Smithsonian. When their name appears in records, it often appeared as what we have come to identify as a SPOUSAL identity. In this construction, a woman would have her named associated with her husband's first and last name, e.g. *Mrs. Martha and Mr. Mark Smith*. Here, we have the woman's first name and last name. In other instances, however, the issue was more complicated with her first name being entirely removed as in the construction *Mr. and Mrs. Mark Smith*.

Another way in which a woman's identity was masked was through the use of her title and last name without clarity of a first name. For example, Dr. Smith could be Dr. Martha Smith or Dr. Mark Smith. In other cases, a woman's name could be hidden behind abbreviations, such as M. Smith. Again, this could refer to either Martha or Mark Smith.

This ambiguity not only clouds the role of women at the Smithsonian, it also directly discredits their own work. In 2019, [Tiana Curry](https://datascience.si.edu/news/whatsinaname), an intern at the Smithsonian, noticed that certain collection records were assigned to Mr. Charles Walcott; the problem was some of these specimen were dated to after his death. In this case (and others like it), attribution belonged to Walcott's widow, Mary Vaux Walcott.

## Solution
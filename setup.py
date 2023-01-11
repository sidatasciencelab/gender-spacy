from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

VERSION = '0.0.1'
DESCRIPTION = 'A spaCy component for identifying grammatical gender in English texts.'

setup(
    name="gender-spacy",
    author="WJB Mattingly",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=["pandas>=1.0.0,<2.0.0",
                     "protobuf<=3.20.0",
                     "spacy>=3.4.0",
                     "allennlp>=2.9.0",
                     "toml>=0.10.0",
                     "spacy-transformers>=1.1.0",
                     ],
    include_package_data = True
)
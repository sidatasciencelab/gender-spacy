from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

VERSION = '0.0.3'
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
                     "spacy>=3.4.0",
                     "spacy-experimental>=0.6.0",
                     "spacy-transformers>=1.1.8"
                     "toml>=0.10.0",
                    #  "en_coreference_web_trf @ git+ssh://git@/github.com/explosion/spacy-experimental/releases/download/v0.6.0/en_coreference_web_trf-3.4.0a0-py3-none-any.whl"
                     ],
    include_package_data = True
)
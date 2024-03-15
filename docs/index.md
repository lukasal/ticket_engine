This site contains the project documentation for the
`ticket engine` project 
Its aim is to give you a LLM based software, which analyzes IT tickets 
and recommends possible solutions based on known, past IT tickets. The
software comes with multiple possibilities to serve.

## Table Of Contents

The documentation consists of four separate parts:

1. [Explanation](explanation.md)
2. [Reference](reference.md)
3. [Tutorials](tutorials.md)
4. [How-To Guides](limitations.md)

Quickly find what you're looking for depending on
your use case by looking at the different pages.

## Installation

Set up a python environment with at least python 3.10, then you can install the package via:
```bash
pip install -i https://test.pypi.org/simple/ ticket_engine
```

As the package is on the test server, you will need to install the dependencies manually, in a requirements.txt file.
```
pandas>=2.2.1
statistics>=1.0.3.5
gradio>=4.19.2
openpyxl>=3.1.2
aleph_alpha_client>=7.0.1
```

```bash
conda install --file ./requirements.txt 
```

## Acknowledgements

I want to thank all collaborators for the support and opportunity to work with them.
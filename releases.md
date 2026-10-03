# Release notes

Current version: **0.2.0**

**0.3.0**, *Oct. 3, 2026*:  Adds new `notebook` extra to package install, and marimo notebook for ineractively analyzing and exploring syntax of Latin and Greek texts. Added option to turn off coloring in dot graphs. Modified utility scripts to display install instructions rather than throw error if spacy model is not install in current environment. 

**0.2.0**, *Sept. 5, 2026*: Additions:

- utility script for building dot graphs from cited references in a corpus
- improved visual formatting of `dot` graphs including coloring by clause
- documentary web site (hosted on github pages)


**0.1.0**, *Sept. 5, 2026*: Initial release. Reads CEX corpora, analyzes citable passages with `spaCy` tools, extracts syntactic data into a `SyntaxGraph` structure. Supports importing a `SyntaxGraph` into a polars dataframes, diagramming with `graphviz`, and diagramming with Mermaid.
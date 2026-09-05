# Release notes

Current version: **0.1.0**


**0.2.0**, *Sept. 5, 2026*: Additions:

- utility script for building dot graphs from cited references in a corpus
- improved visual formatting of `dot` graphs including coloring by clause
- documentary web site (hosted on github pages)


**0.1.0**, *Sept. 5, 2026*: Initial release. Reads CEX corpora, analyzes citable passages with `spaCy` tools, extracts syntactic data into a `SyntaxGraph` structure. Supports importing a `SyntaxGraph` into a polars dataframes, diagramming with `graphviz`, and diagramming with Mermaid.
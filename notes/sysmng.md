
## Activate development environment

```bash
git clone https://github.com/neelsmith/udsyntax.git
cd udsyntax
pip install -e ".[dev]"
pytest
```

The original exploratory notebook lives in `scratch/ud2syntax.py` (gitignored; open it with `marimo edit scratch/ud2syntax.py`).

### Building API docs

`scripts/build_docs.py` renders the docstrings in `src/udsyntax/` as a static HTML site with [pdoc](https://pdoc.dev/):

```bash
pip install -e ".[docs]"           # or ".[dev]", which includes it
python scripts/build_docs.py        # writes docs/udsyntax.html and docs/search.js
open docs/udsyntax.html             # or just open it in a browser
```

The API pages go into `docs/` next to the quarto-built site. pdoc always generates its own `index.html` (a redirect to `udsyntax.html`), so the script renders into a temporary directory and copies everything except that `index.html`. `docs/index.html` is left for quarto. Pass a different output directory as an argument if you'd rather build elsewhere: `python scripts/build_docs.py somewhere/else`.

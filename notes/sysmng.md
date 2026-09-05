
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
pip install -e ".[docs]"
python scripts/build_docs.py        # writes docs/api/index.html
open docs/api/index.html            # or just open it in a browser
```

`docs/api/` is a local, gitignored build -- nothing is published or committed automatically. Pass a different output directory as an argument if you'd rather build elsewhere: `python scripts/build_docs.py somewhere/else`.

# `marimo/udsyntaxer.py`

An interactive marimo notebook front end to udsyntax: choose Latin or Ancient Greek, enter text, click **Analyze**, and view the dependency graph as Graphviz or Mermaid.

## Running it

From the repo root, in the environment where udsyntax and the LatinCy pipeline(s) are installed:

```bash
python -m pip install -e ".[notebook]"   # or ".[dev]", which includes it
marimo edit marimo/udsyntaxer.py   # or `marimo run` for app view (code hidden)
```

marimo comes from the `notebook` optional extra in `pyproject.toml` (`marimo>=0.25`, the version the notebook was written and checked against); the `dev` extra pulls in `notebook` too.

## Layout

1. **Inputs:** language radio (`la` / `grc`), text area, an optional spaCy pipeline override (under "Advanced", mirrors the scripts' `--model`), and an **Analyze** run button. Parsing only runs on the button click, so typing doesn't trigger a slow model load/parse on every change.
2. **Parse:** calls `load_latin` / `load_greek` and `SyntaxGraph.from_doc`.
3. **Display controls:** diagram format (Graphviz / Mermaid), orientation (TB/BT/LR/RL, valid for both renderers), and the clause-coloring switch (dot only; same as the scripts' `--color/--no-color`). These live downstream of the parse, so changing them redraws without re-parsing.
4. **Diagram**, then **downloads** (`udsyntax.dot` or `udsyntax.mmd`, plus `udsyntax.svg` when Graphviz rendered) and the source in a collapsible accordion.

## Graceful failures

| Situation | What the notebook shows |
|---|---|
| `udsyntax` not importable | danger callout with `pip install -e .`; everything below stops |
| No text | warning with an example sentence for the chosen language |
| Pipeline not installed | the `ModelNotInstalledError` message (exact pip command for the running interpreter) |
| Any other parse error | the exception type and message |
| `dot` not on PATH | warning with install instructions and a pointer to Mermaid; source download still offered |
| `dot` exits non-zero / times out | its stderr |

Mermaid rendering happens in the browser via `mo.mermaid`, so it needs no extra install.

## Testing

Verified with marimo 0.25.1 by running harness copies of the notebook (outside the repo) via `app.run()` and `marimo export html`, with the run button forced on and a fake parse of "urbs a Romulo condita est." substituted for the model: Graphviz path (SVG produced, SVG + .dot downloads), Mermaid path, `dot` missing (warning shown, no SVG, .dot download still present), and model missing (real `ModelNotInstalledError` callout). `marimo check` reports no issues. Not tested against the real LatinCy models (they can't be downloaded in this environment).

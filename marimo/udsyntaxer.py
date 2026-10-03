import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="udsyntaxer")


@app.cell(hide_code=True)
def _():
    import shutil
    import subprocess

    import marimo as mo

    return mo, shutil, subprocess


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # udsyntaxer

    Analyze a Latin or Ancient Greek passage with a spaCy pipeline and
    view its dependency graph, drawn with Graphviz or Mermaid. Pick a
    language, enter some text, and click **Analyze**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Fail gracefully if udsyntax itself isn't importable in this kernel.
    try:
        import udsyntax
    except ImportError:
        udsyntax = None

    mo.stop(
        udsyntax is None,
        mo.callout(
            mo.md(
                "**`udsyntax` isn't installed in the Python environment running "
                "this notebook.** From the repository root, install it and "
                "restart the notebook:\n\n"
                "```bash\npython -m pip install -e .\n```"
            ),
            kind="danger",
        ),
    )
    return (udsyntax,)


@app.cell(hide_code=True)
def _(mo):
    LANGUAGES = {"Latin": "la", "Ancient Greek": "grc"}
    EXAMPLES = {
        "la": "urbs a Romulo condita est.",
        "grc": "Ἐν ἀρχῇ ἦν ὁ λόγος.",
    }

    language = mo.ui.radio(
        options=LANGUAGES, value="Latin", inline=True, label="**Language**"
    )
    text_input = mo.ui.text_area(
        placeholder="e.g. " + " / ".join(EXAMPLES.values()),
        rows=4,
        full_width=True,
        label="**Text**",
    )
    model_override = mo.ui.text(
        placeholder="default for the chosen language",
        label="spaCy pipeline (optional)",
    )
    analyze = mo.ui.run_button(label="Analyze", kind="success")

    mo.vstack(
        [
            language,
            text_input,
            mo.accordion({"Advanced": model_override}),
            analyze,
        ]
    )
    return EXAMPLES, analyze, language, model_override, text_input


@app.cell(hide_code=True)
def _(EXAMPLES, analyze, language, mo, model_override, text_input, udsyntax):
    mo.stop(
        not analyze.value,
        mo.md("_Enter some text and click **Analyze**._"),
    )

    _text = text_input.value.strip()
    mo.stop(
        not _text,
        mo.callout(
            mo.md(
                f"Enter some text first, e.g. *{EXAMPLES[language.value]}*"
            ),
            kind="warn",
        ),
    )

    _loaders = {"la": udsyntax.load_latin, "grc": udsyntax.load_greek}
    _load = _loaders[language.value]
    _model = model_override.value.strip()

    _error = None
    try:
        with mo.status.spinner(title="Loading pipeline and parsing…"):
            _nlp = _load(_model) if _model else _load()
            _doc = _nlp(_text)
            graph = udsyntax.SyntaxGraph.from_doc(_doc)
    except udsyntax.ModelNotInstalledError as exc:
        _error = mo.callout(
            mo.md(
                "**The spaCy pipeline isn't installed.**\n\n"
                + "```\n" + str(exc) + "\n```\n\n"
                "Restart the notebook after installing it."
            ),
            kind="danger",
        )
    except Exception as exc:  # anything else spaCy or udsyntax raises
        _error = mo.callout(
            mo.md(
                f"**Analysis failed:** `{type(exc).__name__}: {exc}`"
            ),
            kind="danger",
        )
    mo.stop(_error is not None, _error)

    mo.md(
        f"Parsed **{len(graph.nodes)}** tokens with "
        f"**{len(graph.edges)}** dependency edges."
    )
    return (graph,)


@app.cell(hide_code=True)
def _(graph, mo):
    # Display controls live in their own cell (downstream of the parse) so
    # changing them redraws the graph without re-running the analysis.
    fmt = mo.ui.radio(
        options={"Graphviz (dot)": "dot", "Mermaid": "mermaid"},
        value="Graphviz (dot)",
        inline=True,
        label="**Diagram**",
    )
    orientation = mo.ui.dropdown(
        options={
            "Top to bottom": "TB",
            "Bottom to top": "BT",
            "Left to right": "LR",
            "Right to left": "RL",
        },
        value="Top to bottom",
        label="Orientation",
    )
    color = mo.ui.switch(value=True, label="Color nodes by clause (dot only)")

    _ = graph  # only show the controls once there's something to draw
    mo.hstack([fmt, orientation, color], justify="start", gap=2, wrap=True)
    return color, fmt, orientation


@app.cell(hide_code=True)
def _(color, fmt, graph, orientation):
    if fmt.value == "dot":
        source = graph.to_dot(orientation.value, color_by_clause=color.value)
        source_ext, source_mime = "dot", "text/vnd.graphviz"
    else:
        source = graph.to_mermaid(orientation.value)
        source_ext, source_mime = "mmd", "text/plain"
    return source, source_ext, source_mime


@app.cell(hide_code=True)
def _(fmt, mo, shutil, source, subprocess):
    def render_dot(dot_source: str):
        """Return (svg_text or None, problem callout or None)."""
        dot_bin = shutil.which("dot")
        if dot_bin is None:
            return None, mo.callout(
                mo.md(
                    "**Graphviz's `dot` program isn't installed**, so the graph "
                    "can't be drawn here — but you can still download the DOT "
                    "source below, or switch to **Mermaid**, which needs no "
                    "extra install.\n\n"
                    "To install Graphviz: `brew install graphviz` (macOS), "
                    "`sudo apt install graphviz` (Debian/Ubuntu), or see "
                    "<https://graphviz.org/download/>. Then click **Analyze** "
                    "again."
                ),
                kind="warn",
            )
        try:
            result = subprocess.run(
                [dot_bin, "-Tsvg"],
                input=dot_source,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return None, mo.callout(
                mo.md(f"**Running `dot` failed:** `{exc}`"), kind="danger"
            )
        if result.returncode != 0:
            return None, mo.callout(
                mo.md(
                    "**`dot` rejected the graph:**\n\n```\n"
                    + result.stderr.strip()
                    + "\n```"
                ),
                kind="danger",
            )
        return result.stdout, None

    svg = None
    if fmt.value == "dot":
        svg, _problem = render_dot(source)
        # Drop the XML prolog/DOCTYPE that `dot -Tsvg` emits before inlining.
        diagram = _problem if svg is None else mo.Html(
            f'<div style="overflow:auto">{svg[svg.find("<svg"):]}</div>'
        )
    else:
        diagram = mo.mermaid(source)
    diagram
    return (svg,)


@app.cell(hide_code=True)
def _(mo, source, source_ext, source_mime, svg):
    _downloads = [
        mo.download(
            data=source.encode("utf-8"),
            filename=f"udsyntax.{source_ext}",
            mimetype=source_mime,
            label=f"Download .{source_ext} source",
        )
    ]
    if svg is not None:
        _downloads.append(
            mo.download(
                data=svg.encode("utf-8"),
                filename="udsyntax.svg",
                mimetype="image/svg+xml",
                label="Download SVG",
            )
        )
    _lang = "dot" if source_ext == "dot" else "mermaid"
    mo.vstack(
        [
            mo.hstack(_downloads, justify="start"),
            mo.accordion(
                {"Diagram source": mo.md(f"```{_lang}\n{source}\n```")}
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()

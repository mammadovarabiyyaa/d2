import base64
from PyPDF2 import PdfReader
from dash import Dash, html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)
server = app.server

QUESTIONS = {
    "Easy": ("What does AI stand for?", ["artificial intelligence"]),
    "Medium": ("What is adaptive learning?", ["personalized", "individual"]),
    "Hard": ("Why is adaptive learning effective?", ["feedback", "difficulty"]),
}

app.layout = dbc.Container([
    html.H2("AI Adaptive Learning Dashboard"),
    html.P("Upload PDF → Learn → Adapt"),

    dcc.Upload(
        id="upload",
        children=dbc.Button("Upload PDF"),
    ),

    html.Div(id="status"),
    dcc.Store(id="text"),
    dcc.Store(id="level", data="Easy"),
    dcc.Store(id="score", data=0),

    html.Hr(),

    dcc.RadioItems(
        id="mode",
        options=[
            {"label": "Summary", "value": "summary"},
            {"label": "Adaptive", "value": "adaptive"},
        ]
    ),

    html.Div(id="content"),
    html.Div(id="result")   # ⚠️ ƏVVƏLDƏN MÖVCUDDUR (vacib)
])

# ---------------- PDF LOAD ----------------
@app.callback(
    Output("text", "data"),
    Output("status", "children"),
    Input("upload", "contents"),
)
def load_pdf(contents):
    if not contents:
        return "", ""

    try:
        _, content = contents.split(",")
        reader = PdfReader(base64.b64decode(content))
        text = "".join(p.extract_text() or "" for p in reader.pages)
        return text, "PDF uploaded successfully"
    except Exception as e:
        return "", f"PDF error: {e}"

# ---------------- MAIN UI ----------------
@app.callback(
    Output("content", "children"),
    Input("mode", "value"),
    State("text", "data"),
    State("level", "data"),
    State("score", "data"),
)
def render(mode, text, level, score):
    if not text:
        return "Upload PDF first"

    if mode == "summary":
        return text[:800]

    if mode == "adaptive":
        q, _ = QUESTIONS[level]
        return html.Div([
            html.P(f"Level: {level}"),
            html.P(q),
            dcc.Input(id="answer"),
            dbc.Button("Submit", id="btn"),
            html.P(f"Score: {score}")
        ])

# ---------------- ADAPTIVE LOGIC ----------------
@app.callback(
    Output("result", "children"),
    Output("level", "data"),
    Output("score", "data"),
    Input("btn", "n_clicks"),
    State("answer", "value"),
    State("level", "data"),
    State("score", "data"),
    prevent_initial_call=True,
)
def check(_, ans, level, score):
    if not ans:
        return "Enter an answer", level, score

    if any(k in ans.lower() for k in QUESTIONS[level][1]):
        new = "Medium" if level == "Easy" else "Hard"
        return "Correct", new, score + 1

    return "Wrong", level, score

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)

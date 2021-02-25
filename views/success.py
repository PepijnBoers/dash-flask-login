import warnings
# Dash configuration
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app

warnings.filterwarnings("ignore")

# Bootstrap toast
toast = dbc.Toast(
    [html.P("This is the content of the toast", className="mb-0")],
    header="This is the header",
)
# End toast


# Bootstrap moving progress
progress = html.Div(
    [
        dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
        dbc.Progress(id="progress"),
    ]
)


@app.callback(
    [Output("progress", "value"), Output("progress", "children")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    progress = min(n % 110, 100)
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %" if progress >= 5 else ""
# End  moving progress


# Bootstrap progress bar
progress = html.Div(
    [
        dbc.Progress(value=80, id="animated-progress", striped=True),
    ]
)
# End Bootstrap progress bar


# Bootstrap form
form = dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Label("Habit", className="mr-2"),
                dbc.Input(type="text", placeholder="Enter new habit"),
            ],
            className="mr-3",
        ),
        dbc.FormGroup(
            [
                dbc.Label("Description", className="mr-2"),
                dbc.Input(type="text", placeholder="10 minute daily meditation."),
            ],
            className="mr-3",
        ),
        dbc.FormGroup(
            [
                dbc.Label("Number of days started", html_for="slider"),
                dcc.Slider(id="slider", min=0, max=23, step=1, value=0),
            ]
        ),
        dbc.Button("Submit", color="primary"),
    ],
    style={'margin-top': 10},
)
# End form


# New habit card
new_habit = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("New habit", className="new-habit-card"),
                    form
                ]
            ),
        ],
        style={"width": "100%", "margin-top": 10},
    )
# End new habit card



# Bootsrap cards
def habit_card(habit: str, text: str, progress: int, color: str):
    return dbc.Card(
        [
            dbc.CardHeader(f"{habit}"),
            dbc.CardBody(
                [
                    html.P(f"{text}",
                        className=f"card-text-{habit}",
                    ),
                    dbc.Progress(value=progress, id="animated-progress", striped=True, style={"margin-bottom": 10}, animated=True, color=color),
                    dbc.Button("Stop habit", color="danger"),
                    dbc.Button("Start over", color="info", style={"margin-left": 10}),
                    dbc.Button("Did it today!", color="success", style={"float": "right"}),
                ]
            ),
        ],
        color="success", outline=True,
        style={"width": "100%", "margin-top": 10},
    )
# End Bootstrap cards


# Create success layout
layout = dbc.Container([
    dcc.Location(id='url_login_success', refresh=True),
    html.Div([habit_card("10 min meditation", "Everyday meditation of at least 10 mins.", 10, "success")]),
    html.Div([habit_card("read 5 pages", "Reading five pages everyday.", 21, "warning")]),
    html.Div([habit_card("happy momeny", "Do something that makes you happy.", 30, "info")]),
    html.Div([new_habit])
    ], style={"width":"100%"})



# Create callbacks
@app.callback(Output('url_login_success', 'pathname'),
              [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'

import warnings
# Dash configuration
import dash
import datetime
import json
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
from flask_login import logout_user, current_user

from server import app
from users_mgt import show_habits, update_habit_count, add_habit, reset_habit, del_habit

#warnings.filterwarnings("ignore")

# Global list of habits
habits = []


def print_context(ctx):
    if not ctx.triggered:
        print('No clicks yet')
    else:
        print(ctx.triggered[0]['prop_id'].split('.'))

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
                dbc.Input(id="habit", type="text", placeholder="Enter new habit"),
            ],
            className="mr-3",
        ),
        dbc.FormGroup(
            [
                dbc.Label("Description", className="mr-2"),
                dbc.Input(id="description", type="text", placeholder="10 minute daily meditation."),
            ],
            className="mr-3",
        ),
        dbc.FormGroup(
            [
                dbc.Label("Number of days started", html_for="slider"),
                dcc.Slider(id="slider", min=0, max=23, step=1, value=0),
            ]
        ),
        dbc.Button("Submit", id="submit-button", color="primary"),
        html.P(id="output"),
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
def habit_card(habit: str, created:datetime.datetime, updated:datetime.datetime, text: str, progress: int, color: str):
    return html.Div([dbc.Card(
        [
            dbc.CardHeader(f"{habit}"),
            dbc.CardBody(
                [
                    html.P(f"{text}",
                        className=f"card-text-{habit}",
                    ),
                    dbc.Progress(value=progress, id={'type': 'progress-bar', 'index': habit}, striped=True, style={"margin-bottom": 10}, animated=True, color=color, max=23),
                    dbc.Button("Stop habit", id={'type': 'stop-habit-button', 'index': habit}, color="danger"),
                    dbc.Button("Start over", id={'type': 'restart-button', 'index': habit}, color="info", style={"margin-left": 10}),
                    dbc.Button("Did it today!", id={'type': 'increment-button', 'index': habit}, color="success", style={"float": "right"}),
                    html.P(f"created: {type(created)} {created.day}, last update: {updated}"),
                ]
            ),
        ],
        id={
                'type': 'habit-card',
                'index': habit
            },
        #color="success", outline=True,
        style={"width": "100%", "margin-top": 10},
    )])
# End Bootstrap cards



# Dynamic callbacks!!

@app.callback(
    Output({'type': 'habit-card', 'index': MATCH}, 'children'),
    Input({'type': 'stop-habit-button', 'index': MATCH}, 'n_clicks'),
    [State({'type': 'stop-habit-button', 'index': MATCH}, 'id'),
    State({'type': 'habit-card', 'index': MATCH}, 'children')]
)
def stop_habit(n_clicks, id, children):
    if n_clicks:
        del_habit(current_user.username, id['index'])
        return []
    else:
        return children

    
@app.callback(
    Output({'type': 'progress-bar', 'index': MATCH}, 'value'),
    [Input({'type': 'increment-button', 'index': MATCH}, 'n_clicks'),
    Input({'type': 'restart-button', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'increment-button', 'index': MATCH}, 'id'),
    State({'type': 'progress-bar', 'index': MATCH}, 'value')]
)
def increment_habit_chain(n_clicks_increment, n_clicks_restart, id, progress):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = 'No clicks yet'
        return progress
    else:
        button_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        print(type(button_id))

        if button_id['type'] == 'increment-button':
            update_habit_count(current_user.username, id['index'])
            return progress + 1

        elif button_id['type'] == 'restart-button':
            reset_habit(current_user.username, id['index'])
            return 0
        
        else:
            return progress
        

# End dynamic callbacks!

def stored_habits():
    print('refresh page (calling stored_habits)')
    if not current_user:
        return ""

    habits = show_habits(current_user.username)
    print(f'We found the following habits: {habits} for user: {current_user.username}')
    container = [dcc.Location(id='url_login_success', refresh=True)]
    for habit in habits:
        # ('pep', 'Meditating 33', 'Meditate for 33 minutes')
        container.append(html.Div([habit_card(habit[0], habit[4], habit[3], habit[1], habit[2], "success")]),)

    container.append(html.Div([new_habit]))
    return container
# Create success layout
def layoutje():
    return dbc.Container(stored_habits(), id="habits-cont", style={"width":"100%"})



@app.callback(
    Output('habits-cont', 'children'),
    [Input("submit-button", "n_clicks")], 
    [State('habits-cont', 'children'),
    State("habit","value"),
    State("description", "value"),
    State("slider", "value")])
def output_text(submit, content, habit, description, slider):
    ctx = dash.callback_context
    if not ctx.triggered:
        return content
    else:
        if not habit:
            habit = "Undefined"
        add_habit(current_user.username, habit, description, slider)
        return stored_habits()
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import pyodbc
from dash import no_update
import sqlalchemy
from urllib.parse import quote_plus
from urllib.parse import quote as urlquote
import dateutil.parser as dp
import base64
import io
import os
from uuid import uuid4
from dateutil.relativedelta import relativedelta



params = f'Driver={{{os.getenv("SQL_DRIVER")}}};'\
         f'Server={os.getenv("SQL_HOST")};'\
         f'Port=1433;'\
         f'Database={os.getenv("SQL_SCHEMA")};'\
         f'Uid={os.getenv("SQL_USER")};'\
         f'Pwd={os.getenv("SQL_PWD")};'\
         f'Trusted_Connection={os.getenv("SQL_TRUSTED")};'\
         f'{os.getenv("TDS_CONFIG")}'

sa_conn_string = quote_plus(params)

sa_conn = pyodbc.connect(params)

engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % sa_conn_string, fast_executemany=True)


columns_dict = [
    {'name': 'DOFP', 'id': 'DOFP', 'type': 'datetime'},
    {'name': 'Well Name', 'id': 'wellName', 'type': 'text'},
    {'name': 'Project', 'id': 'project', 'type': 'text'},
    {'name': 'Production Area', 'id': 'prodArea', 'type': 'text'},
    {'name': 'Bench', 'id': 'bench', 'type': 'text'},
    {'name': 'Type Curve', 'id': 'typeCurve', 'type': 'text', 'presentation': 'dropdown'},
]


#############################################################
#                Data Manipulation / Model
#############################################################



########   Create Graph DataFrame   ########




########   Create initial Map DataFrame   ########




########   Initial Datatable & Dropdown DataFrames   ########




#############################################################
#                Dashboard Components
#############################################################


schedule_dropdown = dbc.FormGroup(
    dcc.Dropdown(id='schedule-selector',
                 options=[{'label': x, 'value': x} for x in fetch_schedules()], value='Current Frac Schedule'
    ), className='dash-bootstrap'
)

primary_dropdown = dbc.FormGroup(
    dcc.Dropdown(id='primary-selector',  placeholder='Primary Filter',
        options=[
             {'label': 'Area', 'value': 'prodArea'},
             {'label': 'Project', 'value': 'project'},
         ],
    ), className='dash-bootstrap'
)

secondary_dropdown = dbc.FormGroup(
    dcc.Dropdown(id='secondary-selector',  placeholder='Secondary Filter', multi=True), className='dash-bootstrap'
)

prod_dropdown = dbc.FormGroup(
    dcc.Dropdown(id='prod-selector',  placeholder='Select Existing Production Curves',
                 options=[{'label': x, 'value': x} for x in get_existing_prod()], multi=True
    ), className='dash-bootstrap'
)

graph_card = dbc.Card(dcc.Graph(id='item-graph'), color="light", outline=True)

data_table = dbc.Card(
    dash_table.DataTable(
        id='results-table',
        editable=True,
        sort_action='native',
        sort_mode='multi',
        filter_action='native',
        row_selectable='multi',
        columns=columns_dict,
        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        style_cell={
        'backgroundColor': 'rgb(50, 50, 50)',
        'color': 'white',
        'textAlign': 'left'
        },
        style_data_conditional=[{
            'if': {'column_id': 'typeCurve'},
            'backgroundColor': '#D0CECE',
            'border': '1px solid black',
        }],
        dropdown={'typeCurve':
                      {'options':
                           [
                               {'label': x, 'value': x} for x in fetch_type_curves()
                           ]
                      }
        },

    ),
    color='dark', outline=True, body=True
)

map_card = dbc.Card(dcc.Graph(id='item-map'), color="dark", outline=True,)

database_alert = dbc.FormGroup(dbc.Alert('Database Updated Successfully', id='db-alert', is_open=False, dismissable=True, duration=5000))

updateDB_button = dbc.FormGroup(dbc.Button("Update Database", id='update-button', color="secondary", n_clicks=0))

refresh_graph_button = dbc.FormGroup(dbc.Button("Refresh Graph", id='refresh-button'))

row_count_badge = dbc.FormGroup(dbc.Button(["Rows", dbc.Badge(id='row-badge', color="light", className="ml-1")], id='row-button', color="secondary",))

graph_checklist = dbc.FormGroup(
    [
    dbc.Checklist(
        options=[
            {"label": "Oil", "value": 'Oil'},
            {"label": "Gas", "value": 'Gas'},
            {"label": "Water", "value": 'Water'}],
        value=['Oil', 'Gas', 'Water'],
        id='check-input'),
    ],
)

graph_radio = dbc.FormGroup(
    [
    dbc.RadioItems(
        options=[
            {"label": "Logarithmic", "value": 'log'},
            {"label": "Linear", "value": 'linear'},
        ],
        value='log',
        id='radio-input'),
    ],
)

daily_upload = dbc.FormGroup(
    dcc.Upload(
        id='daily-upload',
        children=html.Div([
            html.A('Upload Daily Production')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
    )
)

monthly_upload = dbc.FormGroup(
    dcc.Upload(
        id='monthly-upload',
        children=html.Div([
            html.A('Upload Monthly Production')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
    )
)

file_alert = dbc.FormGroup(dbc.Alert('File Uploaded Successfully', id='file-alert', is_open=False, dismissable=True, duration=5000))

monthly_alert = dbc.FormGroup(dbc.Alert('File Uploaded Successfully', id='monthly-alert', is_open=False, dismissable=True, duration=5000))

delete_prod_button = dbc.FormGroup(dbc.Button("Delete Production Curve", id='delete-button'))

refresh_prod_button = dbc.FormGroup(dbc.Button("Refresh Existing Production", id='prod-button'))

delete_alert = dbc.FormGroup(dbc.Alert('Files Deleted Successfully', id='delete-alert', is_open=False, dismissable=True, duration=5000))

export_link = dbc.FormGroup(
    html.A(
        dbc.Button("Download CSV", color="secondary"),
        id='csv-link',
        download=f"{uuid4()}.csv",
        href="",
        target="_blank"
    )
)

open_modal_button = dbc.FormGroup(dbc.Button("Add Trace", id='open-modal'))

trace_modal = dbc.Modal([
    dbc.ModalHeader('Select Projects to Add to Graph'),
    dbc.ModalBody([
        dbc.FormGroup(dcc.Dropdown(id='project-selector', multi=True), className='dash-bootstrap'),
        html.Hr(),
    ]),
], id='trace-modal')


hidden_div = dbc.FormGroup(
        html.Div(id='hidden-div')
)

open_variables_modal = dbc.Button('Forecast Variables', id='open-variables')

variables_modal = dbc.Modal([
    dbc.ModalBody([
        dbc.FormGroup([
            dbc.Row([
                dbc.Col([dbc.Label('IP'), dbc.Input(id='ip-input', type='number', debounce=True, value=100)]),
                dbc.Col([dbc.Label('Initial Decline %'), dbc.Input(id='di-input', type='number', debounce=True, value=.0025)]),
                dbc.Col([dbc.Label('B Factor'), dbc.Input(id='b-input', type='number', debounce=True, value=1.35)]),
            ]),
            dbc.Row([
                dbc.Col([dbc.Label('Forecast Days'), dbc.Input(id='days-input', type='number', debounce=True, value=365)]),
                dbc.Col([dbc.Label('Days of Imperical Data'), dbc.Input(id='show-input', type='number', debounce=True, value=365)])
            ]),
            dbc.Row([
                dbc.Col(dbc.Input(id='lid-input', placeholder='Type Load ID Here...', type='text', debounce=True)),
                dbc.Col(dbc.Button('Upload to Sparky', id='sparky-button', n_clicks=0), className='ml-3'),
            ], className='mt-3'),
            dbc.Row([
                dbc.Col(width=3),
                dbc.Col(dbc.Alert('Upload Successful', id='db-alert', is_open=False, dismissable=True, duration=5000)),
                dbc.Col(width=3)
            ])
        ])
    ]),
], id='variables-modal')



#############################################################
#                Dashboard Layout / View
#############################################################


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

server = app.server

app.layout = dbc.Container(
    [

    # Navbar Row
    dbc.Row([
        dbc.Col(html.H2('CQ Seabee'), className='ml-5', style={'color': '#adb5bd'}),
        dbc.Col(dbc.Form(monthly_alert), width=2),
        dbc.Col(dbc.Form(file_alert), width=2),
        dbc.Col(dbc.Form(delete_alert), width=2),
        dbc.Col(width=2),
        dbc.Col(dbc.Form(schedule_dropdown), width=2, className='mt-3 mr-3')
    ], align='center', style={'border-bottom-style': 'solid', 'border-bottom-color': '#adb5bd', 'border-bottom-width': '2px', 'background-color': '#303030'}, no_gutters=True
    ),

    # Graph & Filter Row
    dbc.Row([
        dbc.Col(map_card, width=6),
        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Row(dbc.Form([delete_prod_button]), justify='end')),
                dbc.Col(dbc.Form([refresh_prod_button])),
            ], className='mt-3'
            ),
            dbc.Row(
                dbc.Col(dbc.Form([daily_upload, monthly_upload])),
            ),
            dbc.Row([
                dbc.Col(dbc.Form([prod_dropdown, primary_dropdown, secondary_dropdown]))
            ], className='mt-5'),
        ]),
    ]),

    # Graph Row
    dbc.Row([
        dbc.Col([
           dbc.Row(dbc.Form([open_modal_button, trace_modal])),
           dbc.Row(dbc.Form([graph_radio]), className='mt-5'),
           dbc.Row(dbc.Form([graph_checklist]), className='mt-5'),
        ], width=1, align='center'
        ),
        dbc.Col(
            graph_card,
            width=11,
            )
        ], className='ml-5 mt-3',
    ),

    # Button Row
    dbc.Row(
        [
            dbc.Col(
                row_count_badge, width=1
            ),
            dbc.Col(width=1),
            dbc.Col(
                updateDB_button, width="auto"
            ),
            dbc.Col(
                refresh_graph_button, width="auto"
            ),
            dbc.Col(width=2),
            dbc.Col(
                export_link, width="auto"
            ),
            dbc.Col(
                database_alert, width="auto"
            ),
        ],
        align='center', className='mt-3'
    ),

    # Table Row
    dbc.Row(
        [
            # Table
            dbc.Col(
                data_table,
            ),
        ],
        align='center',
    ),
    ],
    fluid=True,
)


#############################################################
#         Interaction Between Components / Controller
#############################################################


# Load Items in Item Dropdown
@app.callback(
    Output(component_id='secondary-selector', component_property='options'),
    [Input(component_id='primary-selector', component_property='value'),
     Input(component_id='schedule-selector', component_property='value')]
)
def populate_item_selector(selected_filter, selected_schedule):
    if selected_filter is not None:
        items_list = get_items(selected_schedule, selected_filter)
        items_dict = [{'label': items_list, 'value': items_list} for items_list in items_list]
        return items_dict

    else:
        return no_update


# Update Graph
@app.callback(
    [Output(component_id='results-table', component_property='data'),
     Output(component_id='item-graph', component_property='figure'),
     Output(component_id='csv-link', component_property='href')],
    [Input(component_id='schedule-selector', component_property='value'),
     Input(component_id='primary-selector', component_property='value'),
     Input(component_id='secondary-selector', component_property='value'),
     Input(component_id='prod-selector', component_property='value'),
     Input(component_id='item-map', component_property='selectedData'),
     Input(component_id='refresh-button', component_property='n_clicks'),
     Input(component_id='check-input', component_property='value'),
     Input(component_id='radio-input', component_property='value'),
     Input(component_id='project-selector', component_property='value')],
)
def load_item_points_graph(selected_schedule, selected_filter, selected_items, selected_prod, selectedData, a, check_selection, radio_selection, project_selection):
    if selected_filter is not None and selected_items is not None:
        graphdf = get_graphdf(selected_schedule, selected_filter, selected_items)
        proddf = get_proddf(selected_prod)
        total_df = add_graph_prod(graphdf, proddf)
        final_df = add_traces_to_totaldf(selected_schedule, total_df, project_selection)
        figure = draw_graph(final_df, check_selection, radio_selection)
        table_df = calculate_table(selected_schedule, selected_filter, selected_items)
        table_dict = table_df.to_dict('records')
        csv_string = final_df.to_csv(index=False, encoding='utf-8')
        csv_string = 'data:text/csv;charset=utf-8,' + urlquote(csv_string)

        return table_dict, figure, csv_string

    if selectedData is not None:
        lasso_df = pd.json_normalize(selectedData['points'])
        lasso_list = list(lasso_df['text'])
        wid_list = get_gps_wids(selected_schedule, lasso_list)
        graphdf = get_lasso_graphdf(selected_schedule, wid_list)
        proddf = get_proddf(selected_prod)
        total_df = add_graph_prod(graphdf, proddf)
        final_df = add_traces_to_totaldf(selected_schedule, total_df, project_selection)
        figure = draw_graph(final_df, check_selection, radio_selection)
        table_df = calculate_lasso_table(selected_schedule, wid_list)
        table_dict = table_df.to_dict('records')
        csv_string = final_df.to_csv(index=False, encoding='utf-8')
        csv_string = 'data:text/csv;charset=utf-8,' + urlquote(csv_string)

        return table_dict, figure, csv_string

    else:
        return no_update


# Update Database
@app.callback(
    [Output(component_id='db-alert', component_property='is_open')],
    [Input(component_id='update-button', component_property='n_clicks'),
     Input(component_id='update-button', component_property='n_clicks_timestamp'),
     Input(component_id='results-table', component_property='data'),
     Input(component_id='results-table', component_property='data_timestamp'),
     Input(component_id='results-table', component_property='selected_rows')],
    [State(component_id='schedule-selector', component_property='value')]
)
def update_database_from_table(n_clicks, click_time, data, data_time, selected_rows, selected_schedule):
    if selected_rows is not None:
        df = pd.DataFrame(data)
        index_list = [int(x) for x in selected_rows]
        change_list = get_wid_list(index_list, df)
        changed_df = get_df_from_changes(change_list, df)
        changed_df.reset_index(drop=True, inplace=True)
        new_graphdf = recalculate_prod(changed_df)

        if n_clicks > 0 and click_time > data_time:
            changed_df['DOFP'] = pd.to_datetime(changed_df['DOFP'])
            new_graphdf['DOFP'] = pd.to_datetime(new_graphdf['DOFP'])

            delete_wids_from_wells(selected_schedule, change_list)
            delete_wids_from_graph(selected_schedule, change_list)

            graph = selected_schedule + '_graph'
            changed_df.to_sql(name=selected_schedule, con=engine, schema='dbo', index=False, if_exists='append')
            new_graphdf.to_sql(name=graph, con=engine, schema='dbo', index=False, if_exists='append')

            return True,

        return False,

    else:
        return no_update


@app.callback(
    Output(component_id='update-button', component_property='n_clicks'),
    [Input(component_id='results-table', component_property='selected_rows')]
)
def reset_clicks_on_button(selected_rows):
    return 0


@app.callback(
    Output(component_id='results-table', component_property='selected_rows'),
    [Input(component_id='refresh-button', component_property='n_clicks'),
     Input(component_id='row-button', component_property='n_clicks')],
    [State(component_id='results-table', component_property='data'),
     State(component_id='results-table', component_property='derived_virtual_data')],
)
def select_all_rows(refresh_click, row_click, table_data, derived_data):
    if refresh_click or row_click is not None:
        df = pd.DataFrame(table_data)
        df_filtered = pd.DataFrame(derived_data)

        df['copy_index'] = df.index
        new_df = df.merge(df_filtered, on='wellName')

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        if 'refresh-button' in changed_id:
            return []
        elif 'row-button' in changed_id:
            return list(new_df['copy_index'])

    else:
        return no_update


@app.callback(
    Output(component_id='row-badge', component_property='children'),
    [Input(component_id='results-table', component_property='data')]
)
def count_rows(data):
    df = pd.DataFrame(data)
    return len(df.index)


@app.callback(
    [Output(component_id='file-alert', component_property='is_open')],
    [Input(component_id='daily-upload', component_property='contents'),
     Input(component_id='daily-upload', component_property='filename')],
)
def upload_data_from_user(daily_contents, daily_filename):
    if daily_contents is not None:
        upload_df = parse_data(daily_contents, daily_filename)
        upload_name = daily_filename.split(".")[0]
        upload_df['PID'] = [upload_name] * len(upload_df.index)
        upload_df['DOFP'] = pd.to_datetime(upload_df['DOFP'])

        upload_df.to_sql(name="existingprod", con=engine, schema='dbo', index=False, if_exists='append')

        return True,

    else:
        return no_update


@app.callback(
    [Output(component_id='monthly-alert', component_property='is_open')],
    [Input(component_id='monthly-upload', component_property='contents'),
     Input(component_id='monthly-upload', component_property='filename')],
)
def upload_data_from_user(monthly_contents, monthly_filename):
    if monthly_contents is not None:
        upload_df = parse_data(monthly_contents, monthly_filename)
        upload_name = monthly_filename.split(".")[0]
        upload_df = interpolate_monthly_data(upload_df)
        upload_df['PID'] = [upload_name] * len(upload_df.index)

        upload_df.to_sql(name="existingprod", con=engine, schema='dbo', index=False, if_exists='append')

        return True,

    else:
        return no_update


@app.callback(
    [Output(component_id='delete-alert', component_property='is_open')],
    [Input(component_id='delete-button', component_property='n_clicks')],
    [State(component_id='prod-selector', component_property='value')],
)
def delete_existing_curves(n_clicks, selected_prods):
    if n_clicks is not None:
        delete_pids_from_existingprod(selected_prods)
        return True,

    else:
        return no_update


@app.callback(
    Output(component_id='prod-selector', component_property='options'),
    [Input(component_id='prod-button', component_property='n_clicks')]
)
def refresh_prod_dropdown(n_clicks):
    return [{'label': x, 'value': x} for x in get_existing_prod()]


# Open Modal
@app.callback(
    Output(component_id='trace-modal', component_property='is_open'),
    [Input(component_id='open-modal', component_property='n_clicks')],
    [State(component_id='trace-modal', component_property='is_open')]
)
def open_modal(n, is_open):
    if n:
        return True
    return False


# Load Items in Project dropdown
@app.callback(
    Output(component_id='project-selector', component_property='options'),
    [Input(component_id='primary-selector', component_property='value'),
     Input(component_id='secondary-selector', component_property='value'),
     Input(component_id='item-map', component_property='selectedData')],
    [State(component_id='schedule-selector', component_property='value')]
)
def populate_item_selector(selected_filter, selected_items, selectedData, selected_schedule):
    if selected_filter is not None:
        project_list = get_project_list_from_dropdown(selected_schedule, selected_filter, selected_items)
        return [{'label': project_list, 'value': project_list} for project_list in project_list]

    if selected_filter is None and selectedData is not None:
        lasso_df = pd.json_normalize(selectedData['points'])
        lasso_list = list(lasso_df['text'])
        wid_list = get_gps_wids(selected_schedule, lasso_list)
        project_list = get_project_list_from_map(selected_schedule, wid_list)
        return [{'label': project_list, 'value': project_list} for project_list in project_list]

    else:
        return no_update


@app.callback(
    Output(component_id='item-map', component_property='figure'),
    [Input(component_id='schedule-selector', component_property='value')]
)
def refresh_prod_dropdown(selected_schedule):
    return create_map(selected_schedule)


# start Flask server
if __name__ == '__main__':
    app.run_server(
        #host='0.0.0.0',
        #port=5000,
        debug=True
    )
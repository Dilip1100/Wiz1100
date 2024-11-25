import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data (replace with the correct CSV file path)
try:
    full_df = pd.read_csv('FullInp.csv')
except FileNotFoundError:
    full_df = pd.DataFrame(columns=['SERVER', 'DB', 'SCHEMA', 'DATA MART'])  # Empty dataframe for fallback

# Clean the data: Remove rows where any of the relevant columns are null
full_df_cleaned = full_df.dropna(subset=['SERVER', 'DB', 'SCHEMA', 'DATA MART'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout with slicers (dropdowns) and tabs
app.layout = html.Div([
    html.H1("WSS SSRS CATALOG", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Select Server:"),
            dcc.Dropdown(
                id='server_selector',
                options=[{'label': i, 'value': i} for i in full_df_cleaned['SERVER'].unique()],
                value=None,
                placeholder="Select Server"
            )
        ], className="dropdown-container"),

        html.Div([
            html.Label("Select Database:"),
            dcc.Dropdown(
                id='db_selector',
                placeholder="Select Database"
            )
        ], className="dropdown-container"),

        html.Div([
            html.Label("Select Schema:"),
            dcc.Dropdown(
                id='schema_selector',
                placeholder="Select Schema"
            )
        ], className="dropdown-container"),

        html.Div([
            html.Label("Select Data Mart:"),
            dcc.Dropdown(
                id='data_mart_selector',
                placeholder="Select Data Mart"
            )
        ], className="dropdown-container")
    ], style={'display': 'flex', 'gap': '20px'}),

    html.Br(),

    dcc.Tabs([
        dcc.Tab(label='Report Table', children=[
            html.Div(id='report_table_tab')
        ]),
        dcc.Tab(label='Histogram by Data Mart', children=[
            html.Div(id='histogram_tab')
        ]),
    ])
])

# Callback to update cascading dropdowns
@app.callback(
    [Output('db_selector', 'options'),
     Output('schema_selector', 'options'),
     Output('data_mart_selector', 'options')],
    [Input('server_selector', 'value'),
     Input('db_selector', 'value'),
     Input('schema_selector', 'value')]
)
def update_cascading_dropdowns(server, db, schema):
    filtered_df = full_df_cleaned.copy()

    # Apply filters for cascading effect
    if server:
        filtered_df = filtered_df[filtered_df['SERVER'] == server]
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]

    # Update options dynamically based on filtered data
    db_options = [{'label': i, 'value': i} for i in filtered_df['DB'].unique()]
    schema_options = [{'label': i, 'value': i} for i in filtered_df['SCHEMA'].unique()]
    data_mart_options = [{'label': i, 'value': i} for i in filtered_df['DATA MART'].unique()]

    return db_options, schema_options, data_mart_options

# Callback to update the Report Table tab
@app.callback(
    Output('report_table_tab', 'children'),
    [Input('server_selector', 'value'),
     Input('db_selector', 'value'),
     Input('schema_selector', 'value'),
     Input('data_mart_selector', 'value')]
)
def update_report_table(server, db, schema, data_mart):
    filtered_df = full_df_cleaned.copy()

    if server:
        filtered_df = filtered_df[filtered_df['SERVER'] == server]
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]
    if data_mart:
        filtered_df = filtered_df[filtered_df['DATA MART'] == data_mart]

    if filtered_df.empty:
        return html.Div([html.H3("No data found for the selected filters.")])

    return html.Div([
        html.H3("Filtered Report Table"),
        dash_table.DataTable(
            data=filtered_df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in filtered_df.columns],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'}
        )
    ])

# Callback to update the Histogram tab
@app.callback(
    Output('histogram_tab', 'children'),
    [Input('server_selector', 'value'),
     Input('db_selector', 'value'),
     Input('schema_selector', 'value'),
     Input('data_mart_selector', 'value')]
)
def update_histogram(server, db, schema, data_mart):
    filtered_df = full_df_cleaned.copy()

    if server:
        filtered_df = filtered_df[filtered_df['SERVER'] == server]
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]
    if data_mart:
        filtered_df = filtered_df[filtered_df['DATA MART'] == data_mart]

    if filtered_df.empty:
        return html.Div([html.H3("No data found for the selected filters.")])

    histogram_data = filtered_df['DATA MART'].value_counts().reset_index()
    histogram_data.columns = ['Data Mart', 'Record Count']

    histogram = px.bar(histogram_data, x='Data Mart', y='Record Count',
                       title="Record Count per Data Mart",
                       labels={'Record Count': 'Count of Records', 'Data Mart': 'Data Mart'})

    return html.Div([
        html.H3("Histogram of Record Count by Data Mart"),
        dcc.Graph(figure=histogram)
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
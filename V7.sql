import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data (replace with the correct CSV file path)
full_df = pd.read_csv('CMP_DATA.csv', encoding='latin1')
# Clean the data: Remove rows where any of the relevant columns are null

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define a Grey-White theme
theme = {
    "background": "#f7f7f7",
    "card_background": "#ffffff",
    "text_color": "#333333",
    "border_color": "#d3d3d3",
    "dropdown_background": "#ffffff",
    "dropdown_hover": "#e6e6e6",
    "table_header_background": "#f0f0f0",
    "table_header_text": "#333333",
    "table_cell_background": "#ffffff",
    "table_cell_border": "#e0e0e0"
}

# Define the layout
app.layout = html.Div(
    style={"backgroundColor": theme["background"], "padding": "20px", "fontFamily": "Arial, sans-serif"},
    children=[
        html.H1(
            "WSS SSRS CATALOG",
            style={"textAlign": "center", "color": theme["text_color"], "marginBottom": "30px"}
        ),

        # Dropdown filters (slicers) - increased size of dropdowns
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"},
            children=[
                # Server dropdown
                html.Div([
                    dcc.Dropdown(
                        id='server_selector',
                        options=[{'label': i, 'value': i} for i in full_df['SERVER'].unique()],
                        placeholder='Select Server',
                        multi=False,
                        style={"width": "220px", "fontSize": "16px", "backgroundColor": theme["dropdown_background"]}
                    )
                ], style={"flex": "1"}),

                # Database dropdown
                html.Div([
                    dcc.Dropdown(
                        id='db_selector',
                        options=[],
                        placeholder='Select DB',
                        multi=False,
                        style={"width": "220px", "fontSize": "16px", "backgroundColor": theme["dropdown_background"]}
                    )
                ], style={"flex": "1"}),

                # Schema dropdown
                html.Div([
                    dcc.Dropdown(
                        id='schema_selector',
                        options=[],
                        placeholder='Select Schema',
                        multi=False,
                        style={"width": "220px", "fontSize": "16px", "backgroundColor": theme["dropdown_background"]}
                    )
                ], style={"flex": "1"}),

                # Data Mart dropdown
                html.Div([
                    dcc.Dropdown(
                        id='data_mart_selector',
                        options=[],
                        placeholder='Select Data Mart',
                        multi=False,
                        style={"width": "220px", "fontSize": "16px", "backgroundColor": theme["dropdown_background"]}
                    )
                ], style={"flex": "1"}),
            ]
        ),

        # Tabs for Report Table and Graphs
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Report Table', children=[
                html.Div(id='report_table_tab', style={"padding": "20px"})
            ]),
            dcc.Tab(label='Statistical Graphs', children=[
                html.Div(id='stats_graphs_tab', style={"padding": "20px"})
            ])
        ])
    ]
)

# Callback for cascading dropdowns and dynamic options
@app.callback(
    [Output('db_selector', 'options'),
     Output('schema_selector', 'options'),
     Output('data_mart_selector', 'options'),
     Output('report_table_tab', 'children'),
     Output('stats_graphs_tab', 'children')],
    [Input('server_selector', 'value'),
     Input('db_selector', 'value'),
     Input('schema_selector', 'value'),
     Input('data_mart_selector', 'value')]
)
def update_slicers_and_table(server, db, schema, data_mart):
    filtered_df = full_df.copy()

    # Filter based on selections
    if server:
        filtered_df = filtered_df[filtered_df['SERVER'] == server]
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]
    if data_mart:
        filtered_df = filtered_df[filtered_df['DATA MART'] == data_mart]

    # Generate dynamic options for DB, Schema, Data Mart dropdowns
    db_options = [{'label': i, 'value': i} for i in filtered_df['DB'].unique()]
    schema_options = [{'label': i, 'value': i} for i in filtered_df['SCHEMA'].unique()]
    data_mart_options = [{'label': i, 'value': i} for i in filtered_df['DATA MART'].unique()]

    # Generate table for filtered data
    table = dash_table.DataTable(
        data=filtered_df.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in filtered_df.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={
            "backgroundColor": theme["table_header_background"],
            "color": theme["table_header_text"],
            "fontWeight": "bold"
        },
        style_cell={
            "backgroundColor": theme["table_cell_background"],
            "color": theme["text_color"],
            "border": f"1px solid {theme['table_cell_border']}",
            "textAlign": "left"
        }
    )

    # Generate statistical graphs
    graphs = []
    if not filtered_df.empty:
        count_per_data_mart = filtered_df['DATA MART'].value_counts().reset_index()
        count_per_data_mart.columns = ['DATA MART', 'Count']
        fig_data_mart = px.bar(count_per_data_mart, x='DATA MART', y='Count', title='Count of Reports per Data Mart')

        count_per_db = filtered_df['DB'].value_counts().reset_index()
        count_per_db.columns = ['DB', 'Count']
        fig_db = px.bar(count_per_db, x='DB', y='Count', title='Count of Reports per Database')

        count_per_server = filtered_df['SERVER'].value_counts().reset_index()
        count_per_server.columns = ['SERVER', 'Count']
        fig_server = px.bar(count_per_server, x='SERVER', y='Count', title='Count of Reports per Server')

        count_per_schema = filtered_df['SCHEMA'].value_counts().reset_index()
        count_per_schema.columns = ['SCHEMA', 'Count']
        fig_schema = px.bar(count_per_schema, x='SCHEMA', y='Count', title='Count of Reports per Schema')

        graphs = [
            dcc.Graph(figure=fig_data_mart),
            dcc.Graph(figure=fig_db),
            dcc.Graph(figure=fig_server),
            dcc.Graph(figure=fig_schema)
        ]

    # Return dynamic options, the updated table, and graphs
    return db_options, schema_options, data_mart_options, table, graphs

# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8052, debug=False)

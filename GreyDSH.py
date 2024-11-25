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

        # Dropdown filters
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
            children=[
                html.Div([
                    html.Label("Select Server:", style={"color": theme["text_color"]}),
                    dcc.Dropdown(
                        id='server_selector',
                        options=[{'label': i, 'value': i} for i in full_df_cleaned['SERVER'].unique()],
                        value=None,
                        placeholder="Select Server",
                        style={
                            "backgroundColor": theme["dropdown_background"],
                            "color": theme["text_color"],
                            "borderColor": theme["border_color"]
                        }
                    )
                ], style={"flex": "1"}),

                html.Div([
                    html.Label("Select Database:", style={"color": theme["text_color"]}),
                    dcc.Dropdown(
                        id='db_selector',
                        placeholder="Select Database",
                        style={
                            "backgroundColor": theme["dropdown_background"],
                            "color": theme["text_color"],
                            "borderColor": theme["border_color"]
                        }
                    )
                ], style={"flex": "1"}),

                html.Div([
                    html.Label("Select Schema:", style={"color": theme["text_color"]}),
                    dcc.Dropdown(
                        id='schema_selector',
                        placeholder="Select Schema",
                        style={
                            "backgroundColor": theme["dropdown_background"],
                            "color": theme["text_color"],
                            "borderColor": theme["border_color"]
                        }
                    )
                ], style={"flex": "1"}),

                html.Div([
                    html.Label("Select Data Mart:", style={"color": theme["text_color"]}),
                    dcc.Dropdown(
                        id='data_mart_selector',
                        placeholder="Select Data Mart",
                        style={
                            "backgroundColor": theme["dropdown_background"],
                            "color": theme["text_color"],
                            "borderColor": theme["border_color"]
                        }
                    )
                ], style={"flex": "1"}),
            ]
        ),

        # Tabs
        dcc.Tabs(
            style={"backgroundColor": theme["card_background"], "borderRadius": "5px", "boxShadow": "0px 2px 5px #cccccc"},
            children=[
                dcc.Tab(
                    label='Report Table',
                    style={"backgroundColor": theme["card_background"], "borderColor": theme["border_color"]},
                    selected_style={"backgroundColor": theme["dropdown_hover"], "borderColor": theme["border_color"]},
                    children=[html.Div(id='report_table_tab', style={"padding": "20px"})]
                ),
                dcc.Tab(
                    label='Histogram by Data Mart',
                    style={"backgroundColor": theme["card_background"], "borderColor": theme["border_color"]},
                    selected_style={"backgroundColor": theme["dropdown_hover"], "borderColor": theme["border_color"]},
                    children=[html.Div(id='histogram_tab', style={"padding": "20px"})]
                )
            ]
        )
    ]
)

# Callback for cascading dropdowns
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

    if server:
        filtered_df = filtered_df[filtered_df['SERVER'] == server]
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]

    db_options = [{'label': i, 'value': i} for i in filtered_df['DB'].unique()]
    schema_options = [{'label': i, 'value': i} for i in filtered_df['SCHEMA'].unique()]
    data_mart_options = [{'label': i, 'value': i} for i in filtered_df['DATA MART'].unique()]

    return db_options, schema_options, data_mart_options

# Callback for report table
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
        return html.Div([html.H3("No data found for the selected filters.", style={"color": theme["text_color"]})])

    return html.Div([
        dash_table.DataTable(
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
    ])

# Callback for histogram
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
        return html.Div([html.H3("No data found for the selected filters.", style={"color": theme["text_color"]})])

    histogram_data = filtered_df['DATA MART'].value_counts().reset_index()
    histogram_data.columns = ['Data Mart', 'Record Count']

    histogram = px.bar(
        histogram_data, x='Data Mart', y='Record Count',
        title="Record Count per Data Mart",
        labels={'Record Count': 'Count of Records', 'Data Mart': 'Data Mart'}
    )

    return dcc.Graph(figure=histogram)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import io
import base64

# Load the data (replace with the correct CSV file path)
try:
    full_df = pd.read_csv('FullInp.csv')
except FileNotFoundError:
    full_df = pd.DataFrame(columns=['SERVER', 'DB', 'SCHEMA', 'DATA MART'])  # Empty dataframe for fallback

# Clean the data: Remove rows where any of the relevant columns are null
full_df_cleaned = full_df.dropna(subset=['SERVER', 'DB', 'SCHEMA', 'DATA MART'])

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

        # Dropdown filters (slicers) with search box and increased size
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"},
            children=[
                # Server dropdown
                html.Div([
                    dcc.Dropdown(
                        id='server_selector',
                        options=[{'label': i, 'value': i} for i in full_df_cleaned['SERVER'].unique()],
                        placeholder='Select Server',
                        multi=False,
                        searchable=True,  # Enable search in dropdown
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
                        searchable=True,  # Enable search in dropdown
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
                        searchable=True,  # Enable search in dropdown
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
                        searchable=True,  # Enable search in dropdown
                        style={"width": "220px", "fontSize": "16px", "backgroundColor": theme["dropdown_background"]}
                    )
                ], style={"flex": "1"}),
            ]
        ),

        # Report Table and CSV Download Button
        html.Div(id='report_table_tab', style={"padding": "20px"}),

        # CSV Download Button
        html.Div([
            html.A(
                "Download CSV",
                id="download-link",
                download="filtered_data.csv",
                href="",
                target="_blank",
                style={
                    "display": "inline-block",
                    "padding": "10px 20px",
                    "background-color": "#007BFF",
                    "color": "white",
                    "text-align": "center",
                    "border-radius": "5px",
                    "text-decoration": "none"
                }
            ),
        ], style={"textAlign": "center", "marginTop": "20px"})
    ]
)

# Callback for cascading dropdowns and dynamic options
@app.callback(
    [Output('db_selector', 'options'),
     Output('schema_selector', 'options'),
     Output('data_mart_selector', 'options'),
     Output('report_table_tab', 'children'),
     Output('download-link', 'href')],
    [Input('server_selector', 'value'),
     Input('db_selector', 'value'),
     Input('schema_selector', 'value'),
     Input('data_mart_selector', 'value')]
)
def update_slicers_and_table(server, db, schema, data_mart):
    # Allowed schemas
    allowed_schemas = ['dbo', 'mer', 'AADUtilUser', 'WSS\\lcacho2']

    # Start with a copy of the cleaned dataframe
    filtered_df = full_df_cleaned.copy()

    # Filter by SERVER, case-insensitive
    if server:
        filtered_df = filtered_df[filtered_df['SERVER'].str.lower() == server.lower()]

    # Filter by DB
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]

    # Filter by SCHEMA
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]

    # Filter by DATA MART
    if data_mart:
        filtered_df = filtered_df[filtered_df['DATA MART'] == data_mart]

    # Restrict schema options to allowed schemas
    schema_options = [
        {'label': schema, 'value': schema}
        for schema in filtered_df['SCHEMA'].unique()
        if schema in allowed_schemas
    ]

    # Generate dynamic options for DB and Data Mart dropdowns
    db_options = [{'label': db, 'value': db} for db in filtered_df['DB'].unique()]
    data_mart_options = [{'label': dm, 'value': dm} for dm in filtered_df['DATA MART'].unique()]

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

    # Create CSV download link
    csv_string = filtered_df.to_csv(index=False, sep=",")
    csv_bytes = io.BytesIO(csv_string.encode())
    csv_base64 = base64.b64encode(csv_bytes.getvalue()).decode()

    # Return dynamic options, the updated table, and the CSV download link
    return db_options, schema_options, data_mart_options, table, f"data:text/csv;base64,{csv_base64}"



# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

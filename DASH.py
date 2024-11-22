import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data (replace with the correct CSV file path)
full_df = pd.read_csv('FullInp.csv')

# Clean the data: Remove rows where any of the relevant columns are null
full_df_cleaned = full_df.dropna(subset=['SERVER', 'DB', 'SCHEMA', 'DATA MART'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout with slicers (dropdowns) and tabs
app.layout = html.Div([
    html.H1("WSS SSRS CATALOG"),

    # Dropdown for SERVER Selection
    dcc.Dropdown(
        id='server_selector',
        options=[{'label': i, 'value': i} for i in full_df_cleaned['SERVER'].dropna().unique()],
        value=None,
        placeholder="Select Server"
    ),

    # Dropdown for DB Selection
    dcc.Dropdown(
        id='db_selector',
        options=[{'label': i, 'value': i} for i in full_df_cleaned['DB'].dropna().unique()],
        value=None,
        placeholder="Select Database"
    ),

    # Dropdown for SCHEMA Selection
    dcc.Dropdown(
        id='schema_selector',
        options=[{'label': i, 'value': i} for i in full_df_cleaned['SCHEMA'].dropna().unique()],
        value=None,
        placeholder="Select Schema"
    ),

    # Dropdown for DATA MART Selection
    dcc.Dropdown(
        id='data_mart_selector',
        options=[{'label': i, 'value': i} for i in full_df_cleaned['DATA MART'].dropna().unique()],
        value=None,
        placeholder="Select Data Mart"
    ),

    # Tabs for Report Table and Histogram
    dcc.Tabs([
        dcc.Tab(label='Report Table', children=[
            html.Div(id='report_table_tab')
        ]),
        dcc.Tab(label='Histogram by Data Mart', children=[
            html.Div(id='histogram_tab')
        ]),
    ])
])

# Callback to update the Report Table tab based on slicer selections
@app.callback(
    Output('report_table_tab', 'children'),
    [Input('server_selector', 'value'),
     Input('db_selector', 'value'),
     Input('schema_selector', 'value'),
     Input('data_mart_selector', 'value')]
)
def update_report_table(server, db, schema, data_mart):
    # Filter the dataframe based on the selected slicers
    filtered_df = full_df_cleaned.copy()

    if server:
        filtered_df = filtered_df[filtered_df['SERVER'] == server]
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]
    if data_mart:
        filtered_df = filtered_df[filtered_df['DATA MART'] == data_mart]

    # If no data matches, return a message
    if filtered_df.empty:
        return html.Div([html.H3("No data found for the selected filters.")])

    # Return the filtered data in a table
    return html.Div([
        html.H3("Filtered Report Table"),
        dash_table.DataTable(
            data=filtered_df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in filtered_df.columns],
            page_size=10,  # Display 10 rows per page
            style_table={'overflowX': 'auto'}  # Add horizontal scroll for wide tables
        )
    ])

# Callback to update the Histogram tab based on slicer selections (Data Mart context)
@app.callback(
    Output('histogram_tab', 'children'),
    [Input('server_selector', 'value'),
     Input('db_selector', 'value'),
     Input('schema_selector', 'value'),
     Input('data_mart_selector', 'value')]
)
def update_histogram(server, db, schema, data_mart):
    # Filter the dataframe based on the selected slicers
    filtered_df = full_df_cleaned.copy()

    if server:
        filtered_df = filtered_df[filtered_df['SERVER'] == server]
    if db:
        filtered_df = filtered_df[filtered_df['DB'] == db]
    if schema:
        filtered_df = filtered_df[filtered_df['SCHEMA'] == schema]
    if data_mart:
        filtered_df = filtered_df[filtered_df['DATA MART'] == data_mart]

    # If no data matches, return a message
    if filtered_df.empty:
        return html.Div([html.H3("No data found for the selected filters.")])

    # Create a histogram of records based on Data Mart counts
    # Count how many records exist for each Data Mart (grouped by 'DATA MART')
    histogram_data = filtered_df['DATA MART'].value_counts().reset_index()
    histogram_data.columns = ['Data Mart', 'Record Count']

    # Create a Plotly histogram
    histogram = px.bar(histogram_data, x='Data Mart', y='Record Count', 
                       title="Record Count per Data Mart",
                       labels={'Record Count': 'Count of Records', 'Data Mart': 'Data Mart'})

    # Return the plot
    return html.Div([
        html.H3("Histogram of Record Count by Data Mart"),
        dcc.Graph(figure=histogram)
    ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

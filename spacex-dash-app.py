# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# Create a dash application
app = dash.Dash(__name__)


# Task 1: Dropdown options generated dynamically from the dataframe
launch_sites = spacex_df['Launch Site'].unique().tolist()
options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    options.append({'label': site, 'value': site})


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                               dcc.Dropdown(id='site-dropdown',
                                    options=options,
                                    value='ALL',
                                    placeholder="Select a Launch Site here",
                                    searchable=True),
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),


                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                value=[min_payload, max_payload]),


                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                            ])
                                # TASK 2: Pie Chart Callback
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches By Site')
    else:
        # Filter for the specific site selected
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Calculate success vs failure counts
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        fig = px.pie(site_counts, values='count',
                     names='class',
                     title=f'Total Success Launches for site {entered_site}')
    return fig


# TASK 4: Scatter Chart Callback
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
) # Added missing parenthesis here
def update_scatter(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
   
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category",
                         title="Correlation between Payload and Success for all Sites")
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color="Booster Version Category",
                         title=f"Correlation between Payload and Success for {entered_site}")
    return fig # Return the figure object, not a dcc.Graph


if __name__ == '__main__':
    app.run()


# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
launch_sites = [{'label': 'All Sites', 'value': 'All Sites'}] + \
               [{'label': site, 'value': site} for site in spacex_df["Launch Site"].unique()]

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=launch_sites,
                 value='All Sites',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    value=[min_payload, max_payload],
                    marks={2500: '2500 (Kg)', 5000: '5000 (Kg)', 7500: '7500 (Kg)'}),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output('success-pie-chart', 'figure'),
              Input('site-dropdown', 'value'))
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(df, values='class', names='Launch Site', title='Total Success Launches by Site')
    else:
        df = spacex_df[spacex_df['Launch Site'] == selected_site]['class'].value_counts().reset_index()
        df.columns = ['Outcome', 'Count']
        fig = px.pie(df, values='Count', names='Outcome', title=f'Total Success Launches for {selected_site}')
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('payload-slider', 'value')])
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if selected_site != 'All Sites':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title='Payload vs. Outcome for Selected Site',
                     labels={'class': 'Launch Outcome'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

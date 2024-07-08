# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
# List of sites 

launch_sites_list = spacex_df[['Launch Site']].groupby(['Launch Site'], as_index=False).first()['Launch Site'].tolist()
launch_sites_label = launch_sites_list.copy()
launch_sites_list.append('ALL')
launch_sites_label.append('All sites')

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),
                                html.Div([
                                    html.Label("Select Site:"),
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=[                                                
                                                {'label': l, 'value': s} for l, s in zip(launch_sites_label, launch_sites_list)                                                
                                                ],
                                        value='ALL',
                                        placeholder='Select a Launch Site here',
                                        searchable=True)
                                    ]),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                html.Div(dcc.RangeSlider(
                                            id='payload-slider',
                                            min=0, max=10000, step=1000,
                                            marks={0:'0', 2500:'2500', 5000:'5000',7500:'7500', 10000:'10000'},
                                            value=[0, 10000]
                                            )),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):    
    if entered_site == 'ALL':
        filtered_df = spacex_df
        data = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(data, values='class', 
            names='Launch Site',
            title='Total Success Launches By Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        data = filtered_df.groupby('class')['Launch Site'].count().reset_index()
        data = data.sort_values('class',ascending=True)
        data.columns=['Launch result', 'Count']
        fig = px.pie(data, values='Count', 
            names='Launch result',
            title='Total Success Launches for site {s}'.format(s=entered_site))
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
    Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0],payload_range[1])]        
        fig = px.scatter(filtered_df, y="class", x="Payload Mass (kg)", color="Booster Version Category")
        #fig.update_traces(marker_size=10)
        #fig.update_layout(scattermode="group", scattergap=0.75)
        fig.update_layout(title='Correlation between Payload and Success for all Sites', xaxis_title='Payload Mass (kg)', yaxis_title='class')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = filtered_df[spacex_df['Payload Mass (kg)'].between(payload_range[0],payload_range[1])]
        fig = px.scatter(filtered_df, y="class", x="Payload Mass (kg)", color="Booster Version Category")
        fig.update_layout(title='Correlation between Payload and Success for site {s}'.format(s=entered_site), xaxis_title='Payload Mass (kg)', yaxis_title='class')
        return fig        

# Run the app
if __name__ == '__main__':
    app.run_server()

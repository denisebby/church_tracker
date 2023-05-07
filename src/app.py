import dash
from dash import dcc, html, clientside_callback
from dash.dependencies import  Output, Input, State
import dash_breakpoints
import plotly.express as px
import plotly.graph_objects as go

import dash_bootstrap_components as dbc

import pandas as pd

import os



########## UTILITY FUNCTIONS ###########################################################

def read_data():
    print("reading in data")
    df = pd.read_csv("gs://gcf-sources-134756275535-us-central1/church/videos.csv")
    df = df.sort_values(by="publish_time", ascending=False)

    locations_df = pd.read_csv("gs://gcf-sources-134756275535-us-central1/church/locations.csv")
    merged_df = pd.merge(locations_df, df, left_on='church', right_on='channel_title', how='inner')
    # only keep locations that show up for the recent weekend time period
    locations_df = merged_df[list(locations_df.columns) + ["live_status"]]

    update_date = pd.read_csv("gs://gcf-sources-134756275535-us-central1/church/update_date.csv").iloc[0,0]
    
    return df, locations_df, update_date

def generate_map(lat: float=20.5994, lon: float=20.6731, zoom: float=1.5):
    print(f"lat={lat}, lon={lon}, zoom={zoom}")
    fig = go.Figure(go.Choroplethmapbox()) # here you set all attributes needed for a Choroplethmapbox

    fig.add_scattermapbox(lat = locations_df["latitude"],
                        lon = locations_df["longitude"],
                        mode = 'markers+text',
                        text = locations_df["church"],  #a list of strings, one  for each geographical position  (lon, lat)              
                        below='',                 
                        # marker_size=10, 
                        # marker_color='rgb(235, 0, 100)',
                        marker=dict(
                            size=9,
                            color=locations_df["color"],
                            opacity=0.75
                        ),
                        hovertemplate='<b>%{text}</b><br>' +
                        'Recording %{customdata[0]}' +
                        '<br>Latitude: %{lat:.2f}' +
                        '<br>Longitude: %{lon:.2f}<extra></extra>',
                        customdata=[[status] for status in locations_df["live_status"]]
                  )

    fig.update_layout(mapbox = dict(center= dict(lat=lat, lon=lon),  #change to the center of your map,
                                    style="open-street-map",
                                    zoom=zoom, #change this value correspondingly, for your map
                                    # style="carto-positron",  # set your prefered mapbox style
                                    ))

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


def generate_card(index: int):
    cols = []
    for i in [index, index+1]:
        if i < data.shape[0]:
            row = data.iloc[i]
            image_url = row["image_url"]
            title = row["title"]
            publish_time = row["formatted_est_publish_time"]
            channel_title = row["channel_title"]
            live_status = row["live_status"]

            if live_status == "live":
                live_class = "well-live"
                live_message = dcc.Markdown("Live", style={"color": "red", "font-weight": "bold", 
                                                               '-webkit-text-stroke': '0.75px black',
                                                               '-webkit-text-fill-color': 'red',  
                                                            #    'padding': '10px'
                                                        })
            elif live_status == "upcoming":
                live_class = "well-upcoming"
                live_message = dcc.Markdown("Upcoming", style={"color": "gold", "font-weight": "bold", 
                                                               '-webkit-text-stroke': '0.75px black',
                                                               '-webkit-text-fill-color': 'gold',  
                                                            #    'padding': '10px'
                                                        })
            else:
                live_class = "well"
                live_message = None

            video_url = "https://www.youtube.com/watch?v=" + row["video_id"]

            cols.append(
                dbc.Col(
                dbc.Card([
                    dbc.CardImg(src=image_url, top=True, style={"height":"55%", "object-fit":"contain", "textAlign":"center"}, className="align-self-center"),
                    # style = {"font-size": "2vw"}
                    dbc.CardBody([
                    html.A(title, href = video_url, className="card-title",),
                    live_message,
                    dcc.Markdown(f"**Date Uploaded**: {publish_time}\n", className="card-text"),
                    dcc.Markdown(f"{channel_title}", className="card-text"),                    
                    ], style = {}
                    )
                    ],
                    className=f"{live_class} poll-name text-responsive",
                    style={"height":"21rem", "font-family": "Lato, -apple-system, sans-serif"}
                   
                    
                )
                , className="col-8 col-md-4 my-2 mx-2",
                # style={"height":"60%"}
                
                ),
                
            )


    return dbc.Row(cols, align="center", justify="center")

def app_layout():
    LOGO = "https://www.sehionmtcdallas.org/images/favicon/faviconTransparent_180X180.ico"

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=LOGO, className = "ms-2-img"), className="img-fluid"),
                            dbc.Col(
                                dbc.NavbarBrand("Mar Thoma Church English Holy Communion",
                                                    style={
                                                           "white-space": "nowrap"},
                                                    id = "navbar-text",
                                                    className="ms-2 d-flex align-items-center col-9"
                                            )
                                        ),
                                    ],
                        justify="start",
                        align="center",
                        className="g-0",
                    ),
                    style={"textDecoration": "none"},
                ),          
            ]
        ),
        color="dark",
        dark=True,
        id = "navbar",
        style={"width":"100%"}
    )

    fig = generate_map()

    # app.layout = [navbar, dbc.Container()]
    return html.Div([navbar,
                     
                    dcc.Store(id="screen-size"),
                    dash_breakpoints.WindowBreakpoints(
                        id = "breakpoints",
                        widthBreakpointThresholdsPx=[576,768,992,1200,1400],
                        widthBreakpointNames=["xs","sm","md","lg","xl","xxl"]
                    
                    ),

                    html.Center(
                    dcc.Graph(id= "world-map", className="col-12"),
                    style={
                        "width": "100%",
                        "text-align":"center",
                        "justify-content":"center",
                        # "display": "inline-block",
                        "border": "0.2rem aqua solid",
                        # "padding-top": "5px",
                        # "padding-left": "1px",
                        "overflow": "hidden"
                        }
                    ),


                    html.P(f"Last Updated: {update_date}", style={
                                "font-family": "Lato, -apple-system, sans-serif",
                                "padding-left": "5%"
                            }),
                    dbc.Container([
                        generate_card(index) for index in range(0,data.shape[0],2)  
                    ],
                    style = {"width": "100%",  "box-sizing": "border-box"}
                    )

    ])

########################################################################################
########## DEFINE APP ##################################################################

# Define app

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;1,100&family=Montserrat:wght@300&family=Roboto+Mono&display=swap",
]

# VAPOR, LUX, QUARTZ
# external_stylesheets=[dbc.themes.QUARTZ]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])
app.title = "MTC English Services"
server = app.server

print("hi from global")
data, locations_df, update_date = read_data()
# for choropleth
locations_df["color"] = locations_df["live_status"].replace(to_replace={
    "live": "red", "upcoming": "#e6b800", "completed": "#021691"
    })

clientside_callback(
    """(wBreakpoint, w) => {
        console.log("Only updating when crossing the threshold")
        return `${wBreakpoint},${w}`
       
    }""",
    Output("screen-size", "data"),
    Input("breakpoints", "widthBreakpoint"),
    State("breakpoints", "width"),
)

# app.layout = [navbar, dbc.Container()]
app.layout = app_layout


########################################################################################
####### Callbacks ######################################################################
@app.callback(
    Output("world-map", "figure"),
    [Input("screen-size", "data"),
    ],
    # , 
    
)
def update_world_map_view(breakpoint_str):
    breakpoint_name = breakpoint_str.split(",")[0]
    width = int(breakpoint_str.split(",")[1])
    if breakpoint_name in ["sm", "xs"]:
        lat = 30.5994
        lon = 10.6731
        zoom = 0
    elif breakpoint_name in ["md", "lg"]:
        lat = 20.5994
        lon = 20.6731
        zoom = 0.75
    else:
        lat = 20.5994
        lon = 20.6731
        zoom = 1.35 # 1.5

    # print(breakpoint_name, lat, lon, zoom)

    # fig.update_layout(mapbox = dict(center= dict(lat=lat, lon=lon),  #change to the center of your map          
    #                                 zoom=zoom, #change this value correspondingly, for your map
    #                                 style="carto-positron"  # set your prefered mapbox style
    #                             ))


    fig = generate_map(lat=lat, lon=lon, zoom=zoom)
    
    return fig

########################################################################################

    
if __name__=='__main__':
    # app.run_server(debug=True, port=8080)
    app.run_server(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
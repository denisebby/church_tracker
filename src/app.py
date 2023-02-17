import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.express as px
import dash_bootstrap_components as dbc

import pandas as pd

import pickle

from datetime import date, datetime, timedelta
# from dateutil.relativedelta import relativedelta, FR

import os


########## UTILITY FUNCTIONS ###########################################################

def read_data():
    print("reading in data")
    return pd.read_pickle("../data/recent_services.pickle")

def generate_card(index: int):
    cols = []
    for i in [index, index+1]:
        if i < len(data):
            image_url = data["items"][i]["snippet"]["thumbnails"]["medium"]["url"]
            title = data["items"][i]["snippet"]["title"]
            publish_time = data["items"][i]["snippet"]["publishTime"]
            if i == 1:
                publish_time += "A"*100
            channel_title = data["items"][i]["snippet"]["channelTitle"]
            video_url = "https://www.youtube.com/watch?v=" + data["items"][i]["id"]["videoId"]

            cols.append(
                dbc.Col(
                dbc.Card([
                    dbc.CardImg(src=image_url, top=True, style={"height":"12rem", "textAlign":"center"}, className="align-self-center"),
                    # style = {"font-size": "2vw"}
                    dbc.CardBody([dcc.Link(title, href = video_url, className="card-title",),
                    html.P(f"{publish_time}\n", className="card-text",),
                    html.P(f"{channel_title}\n", className="card-text",),
                    
                    ], style = {}
                    )
                    ],
                    className="well poll-name text-responsive",
                    style={"height":"21rem"}
                   
                    
                )
                , className="col-8 col-md-4 my-2 mx-2",
                # style={"height":"60%"}
                
                ),
                
            )


    return dbc.Row(cols, align="center", justify="center")

def app_layout():
    PLOTLY_LOGO = "https://www.sehionmtcdallas.org/images/favicon/faviconTransparent_180X180.ico"

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=PLOTLY_LOGO, height="60rem")),
                            dbc.Col(dbc.NavbarBrand("Mar Thoma Church English Services", className="ms-2")),
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
        id = "navbar"
    )

    df = px.data.gapminder().query("year==2007")
    fig = px.scatter_geo(df, locations="iso_alpha", color="continent",
                        hover_name="country", size="pop",
                        projection="natural earth")



    # app.layout = [navbar, dbc.Container()]
    return html.Div([navbar,
            
                    html.Center(
                    dcc.Graph(figure=fig, className="col-3"),
                    style={
                            # "text-align":"center",
                            # "justify-content":"center"
                            
                            # "display": "inline-block",
                            # "border": "3px #5c5c5c solid",
                            # "padding-top": "5px",
                            # "padding-left": "1px",
                            # "overflow": "hidden"
                        }
                    ),


         
                    dbc.Container([
                        generate_card(index) for index in range(0,len(data),2)  
                    ],
                    )

    ])

########################################################################################
########## DEFINE APP ##################################################################

# Define app

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;1,100&display=swap',
    'https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;1,100&family=Roboto+Mono&display=swap'
]

# VAPOR, LUX, QUARTZ
# external_stylesheets=[dbc.themes.QUARTZ]
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])
app.title = "MTC English Services"
server = app.server

print("hi from global")
data = read_data()



# app.layout = [navbar, dbc.Container()]
app.layout = app_layout


########################################################################################
####### Callbacks ######################################################################

########################################################################################

    
if __name__=='__main__':
    app.run_server(debug=True, port=8080)
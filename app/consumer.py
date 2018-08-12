# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 23:54:13 2018

@author: WeiHan
"""

import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from pymongo import MongoClient
import plotly.graph_objs as go
import numpy as np

client = MongoClient('mongodb://dataset1:rGyFkd7VFzoLzTBSXo1P4WpDowmWkjeURjCCCKw6TKuwz3AoVtw6SBeARoxEzbXgxmCemFSskAJuq4Y78rdjVA==@dataset1.documents.azure.com:10255/?ssl=true&replicaSet=globaldb')
db = client.pdsca2
collection = db.consumerind    
dfc = pd.DataFrame(list(collection.find())).drop(columns = ['_id'])

dfc = dfc.drop(['level_1'], axis=1)
dfc = dfc.set_index('year').loc['2000':'2016'].reset_index()
totalNumof3 = len(list(dfc['level_3'].unique()))
lvl2List = list(dfc['level_2'].unique())
lvl3Lists = []
for i in lvl2List:
    dfct = dfc.set_index('level_2').loc[i]
    lvl3Lists.append(list(dfct['level_3'].unique()))

dfc1 = dfc.set_index('year').drop(['level_2'], axis=1)
lvl3List = list(dfc1['level_3'].unique())
allYear = np.arange(2000, 2017, 1)
dfc1 = dfc1.replace("na",0)
disp = np.linspace(0, 5, num=11)


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div(id='rad', children=[html.Div('Selector'),
            dcc.RadioItems(
                id='views',
                options=[{'label': 'Index', 'value': 'ind'},{'label': 'Frequency of index rise', 'value': 'frq'}],
                value = 'ind'
            )
        ]),html.Br(),
        html.Div(id='l2', children=[html.Div('Division'),
            dcc.Dropdown(
                id='lvl2',
                options=[{'label': i, 'value': i} for i in lvl2List],
                value='Food Excl Food Servicing Services'
            )
        ],
        style={'width': '40%', 'display': 'inline-block'}),
        html.Div(id='div3', children = [html.Div('Index Change'),
            dcc.Slider(
                id='slider',
                min=0,
                max=5,
                value=1,
                step=None,
                marks={str(a) : str(a) for a in disp},
            )
        ],
        style={'display': 'none'}),
    ]),html.Br(),
    dcc.Graph(id='graph')
    
])
@app.callback(Output('l2', 'style'), [Input('views', 'value')])
def toggle_container9(toggle_value):
    if toggle_value == 'frq':
        return {'display': 'none'}
    else:
        return {'width': '40%', 'display': 'inline-block'}
@app.callback(Output('div3', 'style'), [Input('views', 'value')])
def toggle_container10(toggle_value):
    if toggle_value == 'ind':
        return {'display': 'none'}
    else:
        return {'width': '80%', 'display': 'block', 'padding-left': '10em'}

@app.callback(
        dash.dependencies.Output('graph', 'figure'),
        [dash.dependencies.Input('lvl2', 'value'),
         dash.dependencies.Input('slider', 'value'),
         dash.dependencies.Input('views', 'value')])

def update_graph(lvl2, slider, view):
    if(view == 'ind'):
        dfcs = dfc.set_index(['level_2']).loc[lvl2].reset_index().drop(['level_2'], axis=1).set_index('level_3')
        lvl3Plots = lvl3Lists[lvl2List.index(lvl2)]
        trace = []
        for j in lvl3Plots:
            dfcs = dfcs.loc[lvl3Plots]
            trace.append(go.Scatter(x=list(dfcs['year'].loc[j]),y = list(dfcs['value'].loc[j]), name = j, mode = 'lines+markers'))
        
        layout = go.Layout(xaxis={'title': 'year'}, yaxis={'title': 'Price Index'},title="{}".format(lvl2))
        return {'data': trace, 'layout': layout}
    
    elif(view == 'frq'):
        freqofInc = []
        for j in range(1,len(allYear)):
            freqsum = 0;
            for k in lvl3List:
                dfc2 = dfc1.loc[allYear[j-1]:allYear[j]].reset_index().set_index('level_3').loc[k].reset_index().drop(['level_3','year'], axis = 1)
                change = float(dfc2.iloc[1])-float(dfc2.iloc[0])
                if(change > slider):
                    freqsum += 1
            freqofInc.append(freqsum)
        histData = []
        for l in range(0,len(freqofInc)):
            for m in range(0, freqofInc[l]):
                histData.append(allYear[l])
        data = go.Histogram(x=histData)
        layout = go.Layout(xaxis={'title': 'year'}, yaxis={'title': 'Frequency over max of {}'.format(totalNumof3)},title="Frequency of index increase at least by {} at the end of year".format(slider))
        
        return {'data': [data], 'layout': layout}
    else:
        return 0

if __name__ == '__main__':
    app.run_server(debug=True) 
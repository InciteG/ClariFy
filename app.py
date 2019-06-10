# -*- coding: utf-8 -*
import numpy as np
import pandas as pd 
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.graph_objs as go

app = dash.Dash()
dfw2vggk = pd.read_csv('data/w2vggk.csv')
dfldat = pd.read_csv('data/ldat20.csv')
dfldaw = pd.read_csv('data/ldaw20.csv')
dfldatm = pd.read_csv('data/ldatmallet.csv')
dfldawm = pd.read_csv('data/ldawmallet.csv')

# def generate_table(dataframe, max_rows=10):
#     return html.Table(
#         # Header
#         [html.Tr([html.Th(col) for col in dataframe.columns])] +

#         # Body
#         [html.Tr([
#             html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#         ]) for i in range(min(len(dataframe), max_rows))]
#     )
app.layout = html.Div([
    html.H1('Clustering Graphs'),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='TF-IDF K-Means', value='tab-1'),
        dcc.Tab(label='TF-IDF Ward', value='tab-2'),
        dcc.Tab(label='Word2Vec', value='tab-3'),
        dcc.Tab(label='LDA TF-IDF', value='tab-4'),
        dcc.Tab(label='LDA W2V Space', value='tab-5'),
        dcc.Tab(label='LDA Mallet TF-IDF', value='tab-6'),
        dcc.Tab(label='LDA Mallet W2V', value='tab-7'),
    ]),
    html.Div(id='tab-content')
])

@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        df = pd.read_csv('data/tfkm.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':800, 'width': 800, 'margin':"auto"},
                figure={
                    'data': [
                        go.Scattergl(
                            x=df[df['Cluster Label'] == i]['Dim-1'],
                            y=df[df['Cluster Label'] == i]['Dim-2'],
                            text=df[df['Cluster Label'] == i]['Job Title'],
                            mode='markers',
                            opacity=0.8,
                            marker={
                                'size': 10,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name = 'Cluster ' + str(i)
                        ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
                    ],
                    'layout': go.Layout(
                        title = 'TF-IDF Kmeans Clusters',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
    elif tab == 'tab-2':
        df = pd.read_csv('data/tfw.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':800, 'width': 800, 'margin':"auto"},
                figure={
                    'data': [
                        go.Scattergl(
                            x=df[df['Cluster Label'] == i]['Dim-1'],
                            y=df[df['Cluster Label'] == i]['Dim-2'],
                            text=df[df['Cluster Label'] == i]['Job Title'],
                            mode='markers',
                            opacity=0.8,
                            marker={
                                'size': 10,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name = 'Cluster ' + str(i)
                        ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
                    ],
                    'layout': go.Layout(
                        title = 'TF-IDF Kmeans Clusters',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
    elif tab == 'tab-3':
        df = pd.read_csv('data/w2vggk.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':800, 'width': 800, 'margin':"auto"},
                figure={
                    'data': [
                        go.Scattergl(
                            x=df[df['Cluster Label'] == i]['Dim-1'],
                            y=df[df['Cluster Label'] == i]['Dim-2'],
                            text=df[df['Cluster Label'] == i]['Job Title'],
                            mode='markers',
                            opacity=0.8,
                            marker={
                                'size': 10,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name = 'Cluster ' + str(i)
                        ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
                    ],
                    'layout': go.Layout(
                        title = 'TF-IDF Kmeans Clusters',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
    elif tab == 'tab-4':
        df = pd.read_csv('data/ldat20.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':800, 'width': 800, 'margin':"auto"},
                figure={
                    'data': [
                        go.Scattergl(
                            x=df[df['Cluster Label'] == i]['Dim-1'],
                            y=df[df['Cluster Label'] == i]['Dim-2'],
                            text=df[df['Cluster Label'] == i]['Job Title'],
                            mode='markers',
                            opacity=0.8,
                            marker={
                                'size': 10,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name = 'Cluster ' + str(i)
                        ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
                    ],
                    'layout': go.Layout(
                        title = 'TF-IDF Kmeans Clusters',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
    elif tab == 'tab-5':
        df = pd.read_csv('data/ldaw20.csv')

        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':800, 'width': 800, 'margin':"auto"},
                figure={
                    'data': [
                        go.Scattergl(
                            x=df[df['Cluster Label'] == i]['Dim-1'],
                            y=df[df['Cluster Label'] == i]['Dim-2'],
                            text=df[df['Cluster Label'] == i]['Job Title'],
                            mode='markers',
                            opacity=0.8,
                            marker={
                                'size': 10,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name = 'Cluster ' + str(i)
                        ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
                    ],
                    'layout': go.Layout(
                        title = 'TF-IDF Kmeans Clusters',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
    elif tab == 'tab-6':
        df= pd.read_csv('data/ldatmallet.csv')

        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':800, 'width': 800, 'margin':"auto"},
                figure={
                    'data': [
                        go.Scattergl(
                            x=df[df['Cluster Label'] == i]['Dim-1'],
                            y=df[df['Cluster Label'] == i]['Dim-2'],
                            text=df[df['Cluster Label'] == i]['Job Title'],
                            mode='markers',
                            opacity=0.8,
                            marker={
                                'size': 10,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name = 'Cluster ' + str(i)
                        ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
                    ],
                    'layout': go.Layout(
                        title = 'TF-IDF Kmeans Clusters',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])
    elif tab == 'tab-7':
        df = pd.read_csv('data/ldawmallet.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':800, 'width': 800, 'margin':"auto"},
                figure={
                    'data': [
                        go.Scattergl(
                            x=df[df['Cluster Label'] == i]['Dim-1'],
                            y=df[df['Cluster Label'] == i]['Dim-2'],
                            text=df[df['Cluster Label'] == i]['Job Title'],
                            mode='markers',
                            opacity=0.8,
                            marker={
                                'size': 10,
                                'line': {'width': 0.5, 'color': 'white'}
                            },
                            name = 'Cluster ' + str(i)
                        ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
                    ],
                    'layout': go.Layout(
                        title = 'TF-IDF Kmeans Clusters',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            )
        ])

if __name__ == '__main__':
    app.run_server(port = 4051, debug=True)
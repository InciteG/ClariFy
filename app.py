# -*- coding: utf-8 -*
import numpy as np
import pandas as pd 
import dash
import json
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash
import dash_table
import plotly.graph_objs as go
from textwrap import dedent as d
import dash_bootstrap_components as dbc 
import base64
from process import set_stop, gg_tokenize, wp_tokenize
from ffscraperdemo import indeedca_scrape
from fullrun import pipe
import re
import numpy as np 

app = dash.Dash()
app.config['suppress_callback_exceptions']=True
# navbar = dbc.NavbarSimple(
#     children=[
#         dbc.NavItem(dbc.NavLink("Page 1", href="#")),
#         dbc.DropdownMenu(
#             children=[
#                 dbc.DropdownMenuItem("More pages", header=True),
#                 dbc.DropdownMenuItem("Page 2", href="#"),
#                 dbc.DropdownMenuItem("Page 3", href="#"),
#             ],
#             nav=True,
#             in_navbar=True,
#             label="More",
#         ),
#     ],
#     brand="NavbarSimple",
#     brand_href="#",
#     color="primary",
#     dark=True,
# )

#home page
index_page = html.Div([
    dcc.Link('Text Processing', href='/process'),
    html.Br(),
    dcc.Link('Full Pipeline', href='/pipeline'),
    html.Br(),
    dcc.Link('Cluster and Topic Model Results', href='/results'),
    html.Br(),
])

#overall app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Nav(className = "nav nav-pills", children=[
        html.A('Home', className="nav-item nav-link btn", href='/home'),
        html.A('Text Processing', className="nav-item nav-link btn", href='/process'),
        html.A('Full Pipeline', className="nav-item nav-link btn", href='/pipeline') ,
        html.A('Cluster/LDA Results', className="nav-item nav-link btn", href='/results'),
    ]), 
    html.Div(id='page-content')
], style={'background-image': r'\assets\greenfence.jpeg'})

#results page
results_layout = html.Div([
    html.H1('Clustering Graphs', style={'margin':'auto'}),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='TF-IDF K-Means', value='tab-1'),
        dcc.Tab(label='TF-IDF Ward', value='tab-2'),
        dcc.Tab(label='Word2Vec', value='tab-3'),
        dcc.Tab(label='LDA TF-IDF', value='tab-4'),
        dcc.Tab(label='LDA W2V Space', value='tab-5'),
        dcc.Tab(label='LDA Mallet TF-IDF', value='tab-6'),
        dcc.Tab(label='LDA Mallet W2V', value='tab-7'),
    ]),
    html.Div(id='tab-content', style={'margin-top':25}),
     html.Div([
            dcc.Markdown(("""
                **Click Data**

                Click on points in the graph.
            """)),
            html.Pre(id='click-data'),
        ]),
])

#processing page
process_layout = html.Div([
    dcc.Input(id='input-1-state', type='text', value='', placeholder='Enter a job posting...'),
    dcc.Checklist(id = 'checklist-1',
    options=[
        {'label': 'Add-on stop words', 'value': 'ADD'},
        {'label': 'Punctuation', 'value': 'PUC'},
        {'label': 'Number', 'value': 'NUM'}
    ],
    values=['ADD', 'PUC','NUM'],
    labelStyle={'display': 'inline-block'}
), 
    dcc.Checklist(id = 'checklist-2',
    options=[
        {'label': 'Part of Speech', 'value': 'POS'},
        {'label': 'Stop Word Removal', 'value': 'STP'},
        {'label': 'Stemming', 'value': 'STM'}
    ],
    values=['POS', 'STP','STM'],
    labelStyle={'display': 'inline-block'}
), 
    html.Button(id='submit-button', n_clicks=0, children='Submit'),
    html.Div(id='output-submit'),
])
@app.callback(Output('output-submit', 'children'),
              [Input('submit-button', 'n_clicks'), Input('checklist-1','values'), Input('checklist-2','values')],
              [State('input-1-state', 'value')])

def update_output(n_clicks, input1, input2, input3):
    stop = ['ADD','PUC','NUM']
    stop_in = []
    for item in stop:
        if item in input1:
            x = True
        else:
            x = False
        stop_in.append(x)
    stop_words = set_stop(add=stop_in[0],punc=stop_in[1],num=stop_in[2])

    proc = ['POS','STP','STM']
    proc_in = []
    for item in proc:
        if item in input2:
            x = True
        else:
            x = False
        proc_in.append(x)
    tokenize = gg_tokenize(input3, stop_words, pos=proc_in[0], stop=proc_in[1], stem=proc_in[2])
    out = ', '.join(tokenize)
    wptokenize = wp_tokenize(input3, stop_words, pos=proc_in[0], stop=proc_in[1], stem=proc_in[2])
    out1 = ', '.join(wptokenize)
    return html.Div([
        html.H2('Custom Tokenizer'),
        dcc.Textarea(placeholder = 'Enter a job posting...', value=out,    style={'width': '100%'}),
        html.H2('NLTK Word Punc Tokenizer'),
        dcc.Textarea(placeholder = 'Enter a job posting...', value=out1,    style={'width': '100%'}),
    ])


pipeline_layout = html.Div([
    html.Div([
        html.H3('Job title input:'),    
        dcc.Input(id='inpipe-1', type='text', value='', placeholder='Job titles'),
        html.Button(id='submit-button', n_clicks=0, children='Submit'),
    ],
),
    html.Div([
        html.Hr(),
        # dcc.Tabs(id="tabp", value='tabp-1', children=[
        # dcc.Tab(label='Word2Vec', value='tabp-1'),
        # dcc.Tab(label='LDA Topic Modeling', value='tabp-2'),
        html.Div(id = 'graph-output'),
        html.Table(id='table'),
    ]),
    html.Div(id='tabp-content', style={'margin-top':25}),
    html.Div(id='hidden', style={'display':'none'}),
    html.Div(id='inter'),
    html.Div(id='inter-1'),
    ])

@app.callback([Output('inter', 'children'), Output('hidden','children')],
              [Input('submit-button', 'n_clicks')],
              [State('inpipe-1', 'value')])

def scrape_cont(n_clicks, input1):
    hold = str(input1)
    tok = re.split(r"[.|\/,;)(\\_-]", hold.lower()) #tokenize based on any left over punctuation or spaces
    input_list = []
    for item in tok[0:5]:
        x = re.sub(r"[ ]", "+", item.strip()) #tokenize based on any left over punctuation or spaces
        input_list.append(x)
    df = indeedca_scrape(input_list)
    df = df.sample(frac=1).reset_index(drop=True)
    return dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'), 
     css=[{
        'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
    }],
    style_cell={
        'whiteSpace': 'no-wrap',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
        'textAlign': 'center'
    },
    style_cell_conditional=[
        {'if': {'column_id': 'Job Title'},
         'width': '10%'},
        {'if': {'column_id': 'Company'},
         'width': '10%'},
        {'if': {'column_id': 'URL'},
         'width': '10%'},
        {'if': {'column_id': 'Location'},
         'width': '10%'},
    ], 
    filtering=True,
    sorting=True,
    sorting_type="multi",
    row_selectable="multi",
    selected_rows=[],
    pagination_mode="fe",
    pagination_settings={
        "current_page": 0,
        "page_size": 10,
    },
), df.to_json()

@app.callback(Output('inter-1','children'), [Input('hidden','children')])
def pipe_out(jsonified_df):
    df = pd.read_json(jsonified_df)
    df.head(5)
    dfw2v, dflda = pipe(df)
    return dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'), 
)

# @app.callback(Output('graph-output', 'children'),[Input('inter','children')])
# def graph_up(jsondata):
#     df = pd.read_json(jsondata)
#     return html.Div([
#             dcc.Graph(
#                 id='w2vnew',
#                 style = {'height':800, 'width': 800, 'margin':"auto"},
#                 figure={
#                     'data': [
#                         go.Scattergl(
#                             x=df[df['Cluster Label'] == i]['Dim-1'],
#                             y=df[df['Cluster Label'] == i]['Dim-2'],
#                             text=df[df['Cluster Label'] == i]['Job Title'],
#                             mode='markers',
#                             opacity=0.8,
#                             marker={
#                                 'size': 10,
#                                 'line': {'width': 0.5, 'color': 'white'}
#                             },
#                             name = 'Cluster ' + str(i)
#                         ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
#                     ],
#                     'layout': go.Layout(
#                         title = 'New Generated Word2Vec',
#                         xaxis={'title': 'Dim-1'},
#                         yaxis={'title': 'Dim-2'},
#                         margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
#                         legend={'x': 0, 'y': 1},
#                         hovermode='closest'
#                     )
#                 }
#             ),
#             html.Div(
#                 [
#                 html.H1('Cluster Information'),
#                 html.H2('Cluster 0'),
#                 html.P(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0]),
#                 html.H2('Cluster 1'),
#                 html.P(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0]),
#                 html.H2('Cluster 2'),
#                 html.P(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0]),
#                 html.H2('Cluster 3'),
#                 html.P(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0]),
#                 html.H2('Cluster 4'),
#                 html.P(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0]),
#                 html.H2('Cluster 5'),
#                 html.P(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0]),
#                 html.H2('Cluster 6'),
#                 html.P(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0]),
#                 html.H2('Cluster 7'),
#                 html.P(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0]),
#         ])
#     ])



    # if tabp =='tabp-1':
    #     df = pd.read_json('dfw2v.json')
    #     return html.Div([
    #         dcc.Graph(
    #             id='w2vnew',
    #             style = {'height':800, 'width': 800, 'margin':"auto"},
    #             figure={
    #                 'data': [
    #                     go.Scattergl(
    #                         x=df[df['Cluster Label'] == i]['Dim-1'],
    #                         y=df[df['Cluster Label'] == i]['Dim-2'],
    #                         text=df[df['Cluster Label'] == i]['Job Title'],
    #                         mode='markers',
    #                         opacity=0.8,
    #                         marker={
    #                             'size': 10,
    #                             'line': {'width': 0.5, 'color': 'white'}
    #                         },
    #                         name = 'Cluster ' + str(i)
    #                     ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
    #                 ],
    #                 'layout': go.Layout(
    #                     title = 'New Generated Word2Vec',
    #                     xaxis={'title': 'Dim-1'},
    #                     yaxis={'title': 'Dim-2'},
    #                     margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
    #                     legend={'x': 0, 'y': 1},
    #                     hovermode='closest'
    #                 )
    #             }
    #         ),
    #         html.Div(
    #             [
    #             html.H1('Cluster Information'),
    #             html.H2('Cluster 0'),
    #             html.P(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0]),
    #             html.H2('Cluster 1'),
    #             html.P(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0]),
    #             html.H2('Cluster 2'),
    #             html.P(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0]),
    #             html.H2('Cluster 3'),
    #             html.P(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0]),
    #             html.H2('Cluster 4'),
    #             html.P(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0]),
    #             html.H2('Cluster 5'),
    #             html.P(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0]),
    #             html.H2('Cluster 6'),
    #             html.P(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0]),
    #             html.H2('Cluster 7'),
    #             html.P(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0]),
    #     ])
    # ])
    # elif tabp =='tabp-2':
    #     df = pd.read_json('dflda.json')
    #     return html.Div([
    #         dcc.Graph(
    #             id='ldanew',
    #             style = {'height':800, 'width': 800, 'margin':"auto"},
    #             figure={
    #                 'data': [
    #                     go.Scattergl(
    #                         x=df[df['Cluster Label'] == i]['Dim-1'],
    #                         y=df[df['Cluster Label'] == i]['Dim-2'],
    #                         text=df[df['Cluster Label'] == i]['Job Title'],
    #                         mode='markers',
    #                         opacity=0.8,
    #                         marker={
    #                             'size': 10,
    #                             'line': {'width': 0.5, 'color': 'white'}
    #                         },
    #                         name = 'Cluster ' + str(i)
    #                     ) for i in sorted(df['Cluster Label'].unique(), reverse=False)
    #                 ],
    #                 'layout': go.Layout(
    #                     title = 'Newly Generated LDA',
    #                     xaxis={'title': 'Dim-1'},
    #                     yaxis={'title': 'Dim-2'},
    #                     margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
    #                     legend={'x': 0, 'y': 1},
    #                     hovermode='closest'
    #                 )
    #             }
    #         ),
    #         html.H1('Cluster Information'),
    #         html.H2('Topic 0'),
    #         html.P(df.loc[df['Cluster Label']==0]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 1'),
    #         html.P(df.loc[df['Cluster Label']==1]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 2'),
    #         html.P(df.loc[df['Cluster Label']==2]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 3'),
    #         html.P(df.loc[df['Cluster Label']==3]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 4'),
    #         html.P(df.loc[df['Cluster Label']==4]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 5'),
    #         html.P(df.loc[df['Cluster Label']==5]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 6'),
    #         html.P(df.loc[df['Cluster Label']==6]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 7'),
    #         html.P(df.loc[df['Cluster Label']==7]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 8'),
    #         html.P(df.loc[df['Cluster Label']==8]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 9'),
    #         html.P(df.loc[df['Cluster Label']==9]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 10'),
    #         html.P(df.loc[df['Cluster Label']==10]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 11'),
    #         html.P(df.loc[df['Cluster Label']==11]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 12'),
    #         html.P(df.loc[df['Cluster Label']==12]['Topic_Keywords'].values[0]),
    #         html.H2('Topic 13'),
    #         html.P(df.loc[df['Cluster Label']==13]['Topic_Keywords'].values[0]),
    #     ])


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
                        margin={'l': 40, 'b': 40, 't': 50, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            ),
            html.Div(
                [
                html.H1('Cluster Information'),
                html.H2('Cluster 0'),
                html.Img(src=r'static\tfkm0.png'),
                html.P(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0]),
                html.H2('Cluster 1'),
                html.Img(src=r'static\tfkm1.png'),
                html.P(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0]),
                html.H2('Cluster 2'),
                html.Img(src=r'static\tfkm2.png'),
                html.P(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0]),
                html.H2('Cluster 3'),
                html.Img(src=r'static\tfkm3.png'),
                html.P(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0]),
                html.H2('Cluster 4'),
                html.Img(src=r'static\tfkm4.png'),
                html.P(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0]),
                html.H2('Cluster 5'),
                html.Img(src=r'static\tfkm5.png'),
                html.P(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0]),
                html.H2('Cluster 6'),
                html.Img(src=r'static\tfkm6.png'),
                html.P(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0]),
                html.H2('Cluster 7'),
                html.Img(src=r'static\tfkm7.png'),
                html.P(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0]),
                html.H2('Cluster 8'),
                html.Img(src=r'static\tfkm8.png'),
                html.P(df.loc[df['Cluster Label']==8]['Top Vectors'].values[0]),
                html.H2('Cluster 9'),
                html.Img(src=r'static\tfkm9.png'),
                html.P(df.loc[df['Cluster Label']==9]['Top Vectors'].values[0]),])
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
            ),
            html.H1('Cluster Information'),
            html.H2('Cluster 0'),
            html.Img(src=r'static\tfwh0.png'),
            html.P(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0]),
            html.H2('Cluster 1'),
            html.Img(src=r'static\tfwh1.png'),
            html.P(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0]),
            html.H2('Cluster 2'),
            html.Img(src=r'static\tfwh2.png'),
            html.P(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0]),
            html.H2('Cluster 3'),
            html.Img(src=r'static\tfwh3.png'),
            html.P(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0]),
            html.H2('Cluster 4'),
            html.Img(src=r'static\tfwh4.png'),
            html.P(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0]),
            html.H2('Cluster 5'),
            html.Img(src=r'static\tfwh5.png'),
            html.P(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0]),
            html.H2('Cluster 6'),
            html.Img(src=r'static\tfwh6.png'),
            html.P(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0]),
            html.H2('Cluster 7'),
            html.Img(src=r'static\tfwh7.png'),
            html.P(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0]),
            html.H2('Cluster 8'),
            html.Img(src=r'static\tfwh8.png'),
            html.P(df.loc[df['Cluster Label']==8]['Top Vectors'].values[0]),
            html.H2('Cluster 9'),
            html.Img(src=r'static\tfwh9.png'),
            html.P(df.loc[df['Cluster Label']==9]['Top Vectors'].values[0]),
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
            ),
            html.H1('Cluster Information'),
            html.H2('Cluster 0'),
            html.Img(src=r'static\w2vg0.png'),
            html.P(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0]),
            html.H2('Cluster 1'),
            html.Img(src=r'static\w2vg1.png'),
            html.P(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0]),
            html.H2('Cluster 2'),
            html.Img(src=r'static\w2vg2.png'),
            html.P(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0]),
            html.H2('Cluster 3'),
            html.Img(src=r'static\w2vg3.png'),
            html.P(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0]),
            html.H2('Cluster 4'),
            html.Img(src=r'static\w2vg4.png'),
            html.P(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0]),
            html.H2('Cluster 5'),
            html.Img(src=r'static\w2vg5.png'),
            html.P(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0]),
            html.H2('Cluster 6'),
            html.Img(src=r'static\w2vg6.png'),
            html.P(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0]),
            html.H2('Cluster 7'),
            html.Img(src=r'static\w2vg7.png'),
            html.P(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0]),
            html.H2('Cluster 8'),
            html.Img(src=r'static\w2vg8.png'),
            html.P(df.loc[df['Cluster Label']==8]['Top Vectors'].values[0]),
            html.H2('Cluster 9'),
            html.Img(src=r'static\w2vg9.png'),
            html.P(df.loc[df['Cluster Label']==9]['Top Vectors'].values[0]),
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
            ),
            html.H1('Topic Information'),
            html.H2('Topic 0'),
            html.Img(src=r'static\ldat0.png'),
            html.P(df.loc[df['Cluster Label']==0]['Topic_Keywords'].values[0]),
            html.H2('Topic 1'),
            html.Img(src=r'static\ldat1.png'),
            html.P(df.loc[df['Cluster Label']==1]['Topic_Keywords'].values[0]),
            html.H2('Topic 2'),
            html.Img(src=r'static\ldat2.png'),
            html.P(df.loc[df['Cluster Label']==2]['Topic_Keywords'].values[0]),
            html.H2('Topic 3'),
            html.Img(src=r'static\ldat3.png'),
            html.P(df.loc[df['Cluster Label']==3]['Topic_Keywords'].values[0]),
            html.H2('Topic 4'),
            html.Img(src=r'static\ldat4.png'),
            html.P(df.loc[df['Cluster Label']==4]['Topic_Keywords'].values[0]),
            html.H2('Topic 5'),
            html.Img(src=r'static\ldat5.png'),
            html.P(df.loc[df['Cluster Label']==5]['Topic_Keywords'].values[0]),
            html.H2('Topic 6'),
            html.Img(src=r'static\ldat6.png'),
            html.P(df.loc[df['Cluster Label']==6]['Topic_Keywords'].values[0]),
            html.H2('Topic 7'),
            html.Img(src=r'static\ldat7.png'),
            html.P(df.loc[df['Cluster Label']==7]['Topic_Keywords'].values[0]),
            html.H2('Topic 8'),
            html.Img(src=r'static\ldat8.png'),
            html.P(df.loc[df['Cluster Label']==8]['Topic_Keywords'].values[0]),
            html.H2('Topic 9'),
            html.Img(src=r'static\ldat9.png'),
            html.P(df.loc[df['Cluster Label']==9]['Topic_Keywords'].values[0]),
            html.H2('Topic 10'),
            html.Img(src=r'static\ldat10.png'),
            html.P(df.loc[df['Cluster Label']==10]['Topic_Keywords'].values[0]),
            html.H2('Topic 11'),
            html.Img(src=r'static\ldat11.png'),
            html.P(df.loc[df['Cluster Label']==11]['Topic_Keywords'].values[0]),
            html.H2('Topic 12'),
            html.Img(src=r'static\ldat12.png'),
            html.P(df.loc[df['Cluster Label']==12]['Topic_Keywords'].values[0]),
            html.H2('Topic 13'),
            html.Img(src=r'static\ldat13.png'),
            html.P(df.loc[df['Cluster Label']==13]['Topic_Keywords'].values[0]),
            html.H2('Topic 14'),
            html.Img(src=r'static\ldat14.png'),
            html.P(df.loc[df['Cluster Label']==14]['Topic_Keywords'].values[0]),
            html.H2('Topic 15'),
            html.Img(src=r'static\ldat15.png'),
            html.P(df.loc[df['Cluster Label']==15]['Topic_Keywords'].values[0]),
            html.H2('Topic 16'),
            html.Img(src=r'static\ldat16.png'),
            html.P(df.loc[df['Cluster Label']==16]['Topic_Keywords'].values[0]),
            html.H2('Topic 17'),
            html.Img(src=r'static\ldat17.png'),
            html.P(df.loc[df['Cluster Label']==17]['Topic_Keywords'].values[0]),
            html.H2('Topic 18'),
            html.Img(src=r'static\ldat18.png'),
            html.P(df.loc[df['Cluster Label']==18]['Topic_Keywords'].values[0]),
            html.H2('Topic 19'),
            html.Img(src=r'static\ldat19.png'),
            html.P(df.loc[df['Cluster Label']==19]['Topic_Keywords'].values[0]),
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
            ),
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
            ),
            html.H1('Cluster Information'),
            html.H2('Topic 0'),
            html.Img(src=r'static\ldam0.png'),
            html.P(df.loc[df['Cluster Label']==0]['Topic_Keywords'].values[0]),
            html.H2('Topic 1'),
            html.Img(src=r'static\ldam1.png'),
            html.P(df.loc[df['Cluster Label']==1]['Topic_Keywords'].values[0]),
            html.H2('Topic 2'),
            html.Img(src=r'static\ldam2.png'),
            html.P(df.loc[df['Cluster Label']==2]['Topic_Keywords'].values[0]),
            html.H2('Topic 3'),
            html.Img(src=r'static\ldam3.png'),
            html.P(df.loc[df['Cluster Label']==3]['Topic_Keywords'].values[0]),
            html.H2('Topic 4'),
            html.Img(src=r'static\ldam4.png'),
            html.P(df.loc[df['Cluster Label']==4]['Topic_Keywords'].values[0]),
            html.H2('Topic 5'),
            html.Img(src=r'static\ldam5.png'),
            html.P(df.loc[df['Cluster Label']==5]['Topic_Keywords'].values[0]),
            html.H2('Topic 6'),
            html.Img(src=r'static\ldam6.png'),
            html.P(df.loc[df['Cluster Label']==6]['Topic_Keywords'].values[0]),
            html.H2('Topic 7'),
            html.Img(src=r'static\ldam7.png'),
            html.P(df.loc[df['Cluster Label']==7]['Topic_Keywords'].values[0]),
            html.H2('Topic 8'),
            html.Img(src=r'static\ldam8.png'),
            html.P(df.loc[df['Cluster Label']==8]['Topic_Keywords'].values[0]),
            html.H2('Topic 9'),
            html.Img(src=r'static\ldam9.png'),
            html.P(df.loc[df['Cluster Label']==9]['Topic_Keywords'].values[0]),
            html.H2('Topic 10'),
            html.Img(src=r'static\ldam10.png'),
            html.P(df.loc[df['Cluster Label']==10]['Topic_Keywords'].values[0]),
            html.H2('Topic 11'),
            html.Img(src=r'static\ldam11.png'),
            html.P(df.loc[df['Cluster Label']==11]['Topic_Keywords'].values[0]),
            html.H2('Topic 12'),
            html.Img(src=r'static\ldam12.png'),
            html.P(df.loc[df['Cluster Label']==12]['Topic_Keywords'].values[0]),
            html.H2('Topic 13'),
            html.Img(src=r'static\ldam13.png'),
            html.P(df.loc[df['Cluster Label']==13]['Topic_Keywords'].values[0]),
            html.H2('Topic 14'),
            html.Img(src=r'static\ldam14.png'),
            html.P(df.loc[df['Cluster Label']==14]['Topic_Keywords'].values[0]),
            html.H2('Topic 15'),
            html.Img(src=r'static\ldam15.png'),
            html.P(df.loc[df['Cluster Label']==15]['Topic_Keywords'].values[0]),
            html.H2('Topic 16'),
            html.Img(src=r'static\ldam16.png'),
            html.P(df.loc[df['Cluster Label']==16]['Topic_Keywords'].values[0]),
            html.H2('Topic 17'),
            html.Img(src=r'static\ldam17.png'),
            html.P(df.loc[df['Cluster Label']==17]['Topic_Keywords'].values[0]),
            html.H2('Topic 18'),
            html.Img(src=r'static\ldam18.png'),
            html.P(df.loc[df['Cluster Label']==18]['Topic_Keywords'].values[0]),
            html.H2('Topic 19'),
            html.Img(src=r'static\ldam19.png'),
            html.P(df.loc[df['Cluster Label']==19]['Topic_Keywords'].values[0]),
        ])

@app.callback(
    Output('click-data', 'children'),
    [Input('basic-interactions', 'clickData')])
def display_click_data(clickData):
    return html.Div([
        html.H1('WOO')
    ])
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/results':
        return results_layout
    elif pathname == '/process':
        return process_layout
    elif pathname == '/pipeline':
        return pipeline_layout
    else:
        return index_page
if __name__ == '__main__':
    app.run_server(port = 4051, debug=True)
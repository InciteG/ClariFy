# -*- coding: utf-8 -*
import numpy as np
import os
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
import dash_dangerously_set_inner_html

app = dash.Dash(__name__)
server = app.server
app.config['suppress_callback_exceptions']=True

app.index_string= """

<!DOCTYPE html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    {%metas%}
    <title> {%title%}</title>
    {%favicon%}
    {%css%}
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

    <link href="https://fonts.googleapis.com/css?family=Oswald&display=swap" rel="stylesheet">

    <style>
    body {
    background-image: url("app/assets/images/bluepaint.jpeg");
    background-repeat: no-repeat;
    background-attachment: fixed;
    font-family: 'Oswald', sans-serif;
    font-size: 'large';
    color: #000D7F
    }
    .nav-item {
        font-size: medium
    }
    .navbar-bran{
        margin:0;
        padding: 0;
    }
    .logo{
        height: 50px;
    }
    </style>
   
  </head>
  <body>
      
    
        <div id ="container">
            <div id="site-head" class="container">
                  <nav class="navbar navbar-expand-lg navbar-light bg-light">
                      <div class="navbar-header">
                            <a class="navbar-brand" href="#"><img src=url("assets/images/Clarify.png") class="img-responsive logo" ></a>
                      </div>
                      <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                          <li class="nav-item active">
                            <a class="nav-link" href="/home">Home<span class="sr-only">(current)</span></a>
                          </li>
                          <li class="nav-item">
                            <a class="nav-link" href="/pipeline">Web Scraper</a>
                          </li>
                          <li class="nav-item">
                            <a class="nav-link" href="/process">Text Processing</a>
                          </li> 
                          <li class="nav-item">
                            <a class="nav-link" href="/results">Results</a>
                          </li>
                        </ul>
                      </div>
                    </nav>
            </div>
        </div>
            

            <div id="page-content"> 
              <div class="container">
                  <div class= "page-specific-content">
                       {%app_entry%}
                       <footer>
                            {%config%}
                            {%scripts%}
                            {%renderer%}
                        </footer>
                    </div>
                </div>
            </div>
                

            
            
        </div>
    <!-- Optional JavaScript -->
    <!-- jQuery first, then Popper.js, then Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
  </body>
</html>
"""

#home page
index_page = html.Div([
        html.Iframe(srcDoc='''<iframe src="https://onedrive.live.com/embed?cid=2EBAC92E97C3DDB4&amp;resid=2EBAC92E97C3DDB4%21110&amp;authkey=ALTldgYcxhlgulU&amp;em=2&amp;wdAr=1.7777777777777777" 
        width="100%" height="470px" padding=5px margin='auto' frameborder="0">This is an embedded <a target="_blank" href="https://office.com">Microsoft Office</a> presentation, 
        powered by <a target="_blank" href="https://office.com/webapps">Office Online</a>.</iframe>''', style={'width':'100%', 'height':'500px', 'margin': 'auto'}), 
        html.Div([
            html.Br(),
            html.H1('Bringing Clarity to the Job Hunt', style={'font-size':'x-large'}),
            html.Br(),

        ], style={'width':'100%', 'margin':'auto'}),
        html.A(html.Img(src='/assets/images/ln.png', style={'height':'60px','width':'70px'}), href='https://www.linkedin.com/in/garygjg/',),
        html.A(html.Img(src='/assets/images/github.png', style={'height':'60px','width':'60px'}), href='https://github.com/InciteG',),
        html.Br(),
        html.Br(),
        html.A('Resume', className='btn btn-primary', href='/assets/images/Gary_Guo_Resume_617.pdf',role='button', style={'font-size':'medium'}),
        
        ], style={ 'width':'75%', 'margin': 'auto'})


#overall app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={'padding':'20px 50px 20px'})
],)

pipeline_layout = html.Div([
    html.Div([
        html.H2('Web-Scraper', style={'font-size':'x-large'}),   
        dcc.Input(id='inpipe-1', type='text', value='', placeholder='Job titles', style={'font-size':'medium'}),
        html.Button(id='submit-button', n_clicks=0, children='Submit', style={'font-size':'medium'}),
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
    html.Div(id='inter'),
    ])

@app.callback(Output('inter', 'children'),
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
)


#processing page
process_layout = html.Div([ 
    html.H1('Text Processing'),
    dcc.Input(id='input-1-state', type='text', value='', placeholder='Enter a job posting...', style={'height':'30px', 'width':'180px', 'font-size':'medium'}),
    dcc.Checklist(id = 'checklist-1',
    options=[
        {'label': 'Add-on stop words', 'value': 'ADD'},
        {'label': 'Punctuation', 'value': 'PUC'},
        {'label': 'Number', 'value': 'NUM'}
    ],
    values=['ADD', 'PUC','NUM'],
    labelStyle={'display': 'inline-block'},
    style={'font-size':'medium'}
), 
    dcc.Checklist(id = 'checklist-2',
    options=[
        {'label': 'Part of Speech', 'value': 'POS'},
        {'label': 'Stop Word Removal', 'value': 'STP'},
        {'label': 'Stemming', 'value': 'STM'}
    ],
    values=['POS', 'STP','STM'],
    labelStyle={'display': 'inline-block'},
    style={'font-size':'medium'}
), 
    html.Button(id='submit-button', n_clicks=0, children='Submit', style={'font-size':'medium'}),
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
        dcc.Textarea(placeholder = 'Output here...', value=out,    style={'width': '100%', 'height':'300px', 'font-size':'medium'}),
        html.H2('NLTK Word Punc Tokenizer'),
        dcc.Textarea(placeholder = 'Output here...', value=out1,    style={'width': '100%', 'height':'300px', 'font-size':'medium'}),
    ])




#results page
results_layout = html.Div([
    html.H1('Unsupervised Learning Results', style={'margin':'auto'}),
    html.Br(),
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
])

@app.callback(Output('tab-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        df = pd.read_csv('data/tfkm.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':900, 'width': 900, 'margin':"auto"},
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
                        title = 'TF-IDF K-Means Clustering',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            ),
            html.Div(
                [
                html.Br(),
                html.Br(),
                html.H1('Cluster Information'),
                html.Hr(style={'size':'30px',  'display':'block', 'margin-before':'0.5em','margin-after':'0.5em','margin-start':'auto','margin-end':'auto','overflow':'hidden',
                'border-style':'insert','border-width':'4px', 'background-color':'#000DF7'}),
                html.Div([html.H2('Cluster 0', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm0.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 1', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm1.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 2', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm2.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 3', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm3.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 4', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm4.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 5', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm5.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 6', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm6.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 7', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm7.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 8', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm8.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==8]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 9', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfkm9.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==9]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),])
        ])
    elif tab == 'tab-2':
        df = pd.read_csv('data/tfw.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':900, 'width': 900, 'margin':"auto"},
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
                        title = 'TF-IDF Ward Clustering',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            ),
            html.Div(
                [
                html.Br(),
                html.Br(),
                html.H1('Cluster Information'),
                html.Hr(style={'size':'30px',  'display':'block', 'margin-before':'0.5em','margin-after':'0.5em','margin-start':'auto','margin-end':'auto','overflow':'hidden',
                'border-style':'insert','border-width':'4px', 'background-color':'#000DF7'}),
                html.Div([html.H2('Cluster 0', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh0.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 1', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh1.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 2', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh2.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 3', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh3.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 4', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh4.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 5', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh5.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 6', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh6.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 7', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh7.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 8', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh8.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==8]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 9', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\tfwh9.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==9]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),])
        ])
    elif tab == 'tab-3':
        df = pd.read_csv('data/w2vggk.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':900, 'width': 900, 'margin':"auto"},
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
                        title = 'Word2Vec K-Means',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            ),
            html.Div(
                [
                html.Br(),
                html.Br(),
                html.H1('Cluster Information'),
                html.Hr(style={'size':'30px',  'display':'block', 'margin-before':'0.5em','margin-after':'0.5em','margin-start':'auto','margin-end':'auto','overflow':'hidden',
                'border-style':'insert','border-width':'4px', 'background-color':'#000DF7'}),
                html.Div([html.H2('Cluster 0', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg0.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==0]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 1', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg1.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==1]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 2', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg2.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==2]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 3', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg3.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==3]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 4', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg4.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==4]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 5', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg5.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==5]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 6', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg6.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==6]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 7', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg7.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==7]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 8', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg8.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==8]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Cluster 9', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\w2vg9.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==9]['Top Vectors'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),])
        ])
    elif tab == 'tab-4':
        df = pd.read_csv('data/ldat20.csv')
        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':900, 'width': 900, 'margin':"auto"},
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
                        title = 'LDA in TF-IDF Space',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
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
                style = {'height':900, 'width': 900, 'margin':"auto"},
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
                        title = 'LDA in W2V Space',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            ),
            html.Div(
                [
                html.Br(),
                html.Br(),
                html.H1('Topic Information'),
                html.Hr(style={'size':'30px',  'display':'block', 'margin-before':'0.5em','margin-after':'0.5em','margin-start':'auto','margin-end':'auto','overflow':'hidden',
                'border-style':'insert','border-width':'4px', 'background-color':'#000DF7'}),
                html.Div([html.H2('Topic 0', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat0.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==0]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Top 1', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat1.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==1]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 2', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat2.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==2]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 3', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat3.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==3]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 4', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat4.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==4]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 5', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat5.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==5]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 6', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat6.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==6]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 7', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat7.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==7]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 8', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat8.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==8]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 9', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat9.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==9]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 10', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat10.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==10]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 11', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat11.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==11]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 12', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat12.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==12]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 13', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat13.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==13]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 14', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat14.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==14]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 15', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat15.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==15]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 16', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat16.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==16]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 17', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat17.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==17]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 18', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat18.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==18]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 19', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldat19.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==19]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                
                ])
        ])
    elif tab == 'tab-6':
        df= pd.read_csv('data/ldatmallet.csv')

        return html.Div([
            dcc.Graph(
                id='tfkm',
                style = {'height':900, 'width': 900, 'margin':"auto"},
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
                        title = 'LDA Mallet in TF-IDF Space',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
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
                style = {'height':900, 'width': 900, 'margin':"auto"},
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
                        title = 'LDA Mallet in Word2Vec Space',
                        xaxis={'title': 'Dim-1'},
                        yaxis={'title': 'Dim-2'},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
                    )
                }
            ),
            html.Div(
                [
                html.Br(),
                html.Br(),
                html.H1('Topic Information'),
                html.Hr(style={'size':'30px',  'display':'block', 'margin-before':'0.5em','margin-after':'0.5em','margin-start':'auto','margin-end':'auto','overflow':'hidden',
                'border-style':'insert','border-width':'4px', 'background-color':'#000DF7'}),
                html.Div([html.H2('Topic 0', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam0.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==0]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Top 1', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam1.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==1]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 2', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam2.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==2]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 3', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam3.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==3]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 4', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam4.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==4]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 5', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam5.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==5]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 6', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam6.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==6]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 7', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam7.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==7]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 8', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam8.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==8]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 9', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam9.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==9]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 10', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam10.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==10]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 11', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam11.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==11]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 12', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam12.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==12]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 13', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam13.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==13]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 14', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam14.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==14]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 15', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam15.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==15]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 16', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam16.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==16]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 17', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam17.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==17]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 18', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam18.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==18]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                html.Div([html.H2('Topic 19', style={'font-weight':'bold'}),
                html.Br(),
                html.Div([html.H3('Job Title - Bigrams and Trigrams:', style={"text-decoration":"underline"}),
                html.Img(src=r'assets\images\ldam19.png'),
                html.Br(),
                html.Br(),
                html.Br(),
                html.H3('Most Defining Words:', style={"text-decoration":"underline"}),
                html.H2(df.loc[df['Cluster Label']==19]['Topic_Keywords'].values[0])])], style={'padding':'10px', 'border-style':'solid'}),
                html.Br(),
                
                ])
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
import copy

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

# FIXME: switch to using a signle copy
from controls import (EMISSION_LINES, layout, layout_BPT, layout_count,
                      layout_HeII, layout_stellar)

# Multi-dropdown options
emission_line_options = [
    {'label': str(line), 'value': str(EMISSION_LINES[line])} for line in EMISSION_LINES]

# Data read in
df = pd.read_hdf('data.h5', 'table')
df['PrettyPercent'] = ('P(AGN): ' + df['BPT:P(AGN)'].map('{:.02%}'.format) +
                       ' P(SF): ' + df['BPT:P(SF)'].map('{:.02%}'.format))

# Parameters of each object type
OBJECT_TYPES = {

    'SF': {'verboseName': 'Starforming',
           'color': 'rgba(0, 0, 152, .8)',
           'booleanMask': (df['BPT:P(AGN)'] == 0) & (df['BPT:P(SF)'] > 0),
           },
    'MXD': {'verboseName': 'Mixed',
            'color': 'rgba(127, 63, 191, 0.8)',
            'booleanMask': (df['BPT:P(AGN)'] > 0) & (df['BPT:P(SF)'] > 0),
            },
    'AGN': {'verboseName': 'Active Galactic Nuclei',
            'color': 'rgba(152, 0, 0, .8)',
            'booleanMask': (df['BPT:P(AGN)'] > 0) & (df['BPT:P(SF)'] == 0),
            },

}


app = dash.Dash('__name__')
server = app.server

# For simplicty I used dash's oil and gas demo as a template
app.css.append_css(
    {'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1(children='Active Galactic Nuclei Distributions',
                        className='five columns',),

                html.Img(
                    src="https://brand.uconn.edu/wp-content/uploads/sites/1060/2014/12/uconn-blue-side.jpg",
                    className='six columns',
                    style={
                        'height': '50',
                        'width': '500',
                        'float': 'right',
                        'position': 'relative',
                    },
                ),
            ],
            style={'margin-top': '20'},
            className='row',

        ),
        html.Div(
            [
                html.P(children='This demo app is an interactive comparison of the BPT and HeII diagnostic classifiers of galaxies found in SDSS 13 data release.',
                       className='five columns',)

            ],
            style={'margin-top': '0'},
            className='row',
        ),
        html.Div(
            [
                html.H5(
                    '',
                    id='obj_text',
                    className='three columns'
                ),
                html.H5(
                    '',
                    id='percent_text',
                    className='five columns',
                    style={'text-align': 'center'}
                ),
                html.H5(
                    '',
                    id='redshift_text',
                    className='four columns',
                    style={'text-align': 'right'}
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.P('Signal to noise cutoff:'),

                dcc.Slider(
                    id='signal-noise-slider',
                    min=0,
                    max=3,
                    value=0,
                    step=1,
                    marks={str(snr): str(snr) for snr in np.arange(0, 4)},
                    className='five columns'
                ),
                html.P(' ', className='two columns'),
                dcc.RangeSlider(
                    id='redshift_range',
                    min=0.04,
                    max=0.1,
                    step=0.001,
                    value=[0.04, 0.1],
                    marks={str(snr / 100): str(snr / 100)
                           for snr in range(4, 11)},
                    className='five columns'
                ),
            ],
            className='row'
        ),
        html.Div(
            [
                html.P('Lines to filter:'),
                dcc.Dropdown(
                    id='emission-line-check-list',
                    options=emission_line_options,
                    multi=True,
                    value=[],
                ),

            ],
            style={'margin-top': '20'},
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='main_graph')
                    ],
                    className='six columns',
                    style={'margin-top': '20'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='heII_graph')
                    ],
                    className='six columns',
                    style={'margin-top': '20'}
                ),

            ],
            className='row'
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='stellar_mass_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '10'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='pie_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '10'}
                ),
                html.Div(
                    [
                        dcc.Graph(id='redshift_graph')
                    ],
                    className='four columns',
                    style={'margin-top': '10'}
                ),
            ],
            className='row'
        ),

    ],
    className='ten columns offset-by-one'
)

# Helper Functions


def filter_dataframe(df, emission_line_list, selected_snr, redshift_range, group_subsets=None):
    # TODO: Find a way to cache this, remove all old calls to this function
    dff = df[(df[emission_line_list].gt(selected_snr).all(1))
             & (df['redshift'] > redshift_range[0])
             & (df['redshift'] < redshift_range[1])]
    return dff


# Create callbacks

# Slider -> count graph
@app.callback(Output('redshift_range', 'value'),
              [Input('redshift_graph', 'selectedData')])
def update_redshift_slider(redshift_graph_selected_data):
    if redshift_graph_selected_data is None:
        return [0.04, 0.1]
    else:
        nums = []
        for point in redshift_graph_selected_data['points']:
            nums.append(int(point['pointNumber']))
        return [min(nums) * 0.001 + 0.04, max(nums) * 0.001 + 0.04]


# Selectors -> obj text
@app.callback(Output('obj_text', 'children'),
              [Input('emission-line-check-list', 'value'),
               Input('signal-noise-slider', 'value'),
               Input('redshift_range', 'value')])
def update_obj_text(emission_line_list, selected_snr, redshift_range):
    dff = filter_dataframe(df, emission_line_list,
                           selected_snr, redshift_range)
    return ("No of Objects: {}".format(dff.shape[0]))


# Selectors -> percent text
@app.callback(Output('percent_text', 'children'),
              [Input('emission-line-check-list', 'value'),
               Input('signal-noise-slider', 'value'),
               Input('redshift_range', 'value')])
def update_percent_text(emission_line_list, selected_snr,  redshift_range):
    dff = filter_dataframe(df, emission_line_list,
                           selected_snr, redshift_range)
    total = dff.shape[0]
    number_of_agn = dff[(dff['BPT:P(AGN)'] > 0) &
                        (dff['BPT:P(SF)'] == 0)].shape[0]
    number_of_sf = dff[(dff['BPT:P(AGN)'] == 0) &
                       (dff['BPT:P(SF)'] > 0)].shape[0]
    number_of_mixed = total - (number_of_agn + number_of_sf)
    return ("AGN: {:.0%} | Mixed: {:.0%} |Starforming: {:.0%} ".format(
        (number_of_agn / total),
        (number_of_mixed / total),
        (number_of_sf / total))
    )


# Slider -> histogram text
@app.callback(Output('redshift_text', 'children'),
              [Input('redshift_range', 'value')])
def update_redshift_text(redshift_range):
    return "Redshift range: {:.3f} | {:.3f}".format(redshift_range[0], redshift_range[1])


# main graph -> figure
@app.callback(
    Output('main_graph', 'figure'),
    [Input('emission-line-check-list', 'value'),
     Input('signal-noise-slider', 'value'),
     Input('redshift_range', 'value')],
)
def make_main_graph(emission_line_list, selected_snr,
                    redshift_range):
    # Pull only rows which meet all conditions
    dff = filter_dataframe(df, emission_line_list,
                           selected_snr, redshift_range)
    traces = []
    for objName, objDic in OBJECT_TYPES.items():
        traces.append(go.Scattergl(
            x=dff.loc[(objDic['booleanMask'])]['Log(N_II/H_Alpha)'],
            y=dff.loc[(objDic['booleanMask'])]['Log(O_III/H_Beta)'],
            text=dff.loc[objDic['booleanMask']]['PrettyPercent'],
            mode='markers',
            opacity=0.8,
            name=str(objName),
            marker={
                'size': 4,
                'color': objDic['color'],
                'opacity': 1,
                'line': {'width': 0.5, 'color': objDic['color']}
            })
        )
    figure = dict(data=traces, layout=layout_BPT)
    return figure


# options -> HeII Graph
@app.callback(
    Output('heII_graph', 'figure'),
    [Input('emission-line-check-list', 'value'),
     Input('signal-noise-slider', 'value'),
     Input('redshift_range', 'value')],
)
def make_HeII_graph(emission_line_list, selected_snr,
                    redshift_range):
    dff = filter_dataframe(df, emission_line_list,
                           selected_snr, redshift_range)
    traces = []
    for objName, objDic in OBJECT_TYPES.items():
        traces.append(go.Scattergl(
            x=dff.loc[(objDic['booleanMask'])]['Log(N_II/H_Alpha)'],
            y=dff.loc[(objDic['booleanMask'])]['Log(He_II/H_Beta)'],
            text=dff.loc[objDic['booleanMask']]['PrettyPercent'],
            mode='markers',
            opacity=0.8,
            name=str(objName),
            marker={
                'size': 4,
                'color': objDic['color'],
                'opacity': 1,
                'line': {'width': 0.5, 'color': objDic['color']}
            })
        )
    figure = dict(data=traces, layout=layout_HeII)
    return figure


# Selectors -> stellar mass graph
@app.callback(Output('stellar_mass_graph', 'figure'),
              [Input('emission-line-check-list', 'value'),
               Input('signal-noise-slider', 'value'),
               Input('redshift_range', 'value')])
def make_stellar_mass_graph(emission_line_list, selected_snr,
                            redshift_range):
    # Pull only rows which meet all conditions
    dff = filter_dataframe(df, emission_line_list,
                           selected_snr, redshift_range)
    traces = []
    for objName, objDic in OBJECT_TYPES.items():
        traces.append(go.Scattergl(
            x=dff.loc[(objDic['booleanMask'])]['logmass'],
            y=dff.loc[(objDic['booleanMask'])]['H_Alpha'].apply(np.log10),
            text=dff.loc[objDic['booleanMask']]['PrettyPercent'],
            mode='markers',
            opacity=0.8,
            name=str(objName),
            marker={
                'size': 4,
                'color': objDic['color'],
                'opacity': 0.6,
                'line': {'width': 0.5, 'color': objDic['color']}
            })
        )
    figure = dict(data=traces, layout=layout_stellar)
    return figure


# Selectors -> redshift graph
@app.callback(Output('redshift_graph', 'figure'),
              [Input('emission-line-check-list', 'value'),
               Input('signal-noise-slider', 'value'),
               Input('redshift_range', 'value')])
def make_redshift_graph(emission_line_list, selected_snr,
                        redshift_range):

    dff = filter_dataframe(df, emission_line_list,
                           selected_snr, [0.04, 0.1])
    dff['redshift'] = dff['redshift'].round(3)
    g = dff.groupby(['redshift']).size()
    colors = []
    for i in np.linspace(0.04, 0.1, num=62):
        if i >= redshift_range[0] and i < redshift_range[1]:
            colors.append('rgb(192, 255, 245)')
        else:
            colors.append('rgba(192, 255, 245, 0.2)')
    data = [
        dict(
            type='scatter',
            mode='markers',
            x=g.index,
            y=g.values / 2,
            name='test',
            opacity=0,
            hoverinfo='skip'
        ),
        dict(
            type='bar',
            x=g.index.values,
            y=g.values,
            name='redshift',
            marker=dict(
                color=colors
            ),
        ),
    ]
    layout_count['title'] = 'Redshift'
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    figure = dict(data=data, layout=layout_count)
    return figure


@app.callback(Output('pie_graph', 'figure'),
              [Input('emission-line-check-list', 'value'),
               Input('signal-noise-slider', 'value'),
               Input('redshift_range', 'value')])
def make_venn_diagram(emission_line_list, selected_snr,
                      redshift_range):
    # TODO: Preprocess these boolean masks to clean up this code, insure that selection will work here
    # FIXME: layouts are a mess
    layout_pie = copy.deepcopy(layout)
    dff = filter_dataframe(df, emission_line_list,
                           selected_snr, redshift_range)

    n_bpt_agn = dff[(dff['BPT:P(AGN)'] > 0) & (dff['BPT:P(SF)'] == 0) &
                    (dff['He_II:P(AGN)'] == 0)].shape[0]
    n_heII_agn = dff[(dff['He_II:P(AGN)'] > 0) & (dff['He_II:P(SF)'] == 0) &
                     (dff['BPT:P(AGN)'] == 0)].shape[0]
    n_both_agn = dff[(dff['BPT:P(AGN)'] > 0) & (
        dff['He_II:P(AGN)'] > 0)].shape[0]

    n_bpt_sf = dff[(dff['BPT:P(SF)'] > 0) & (dff['BPT:P(AGN)'] == 0) &
                   (dff['He_II:P(SF)'] == 0)].shape[0]
    n_heII_sf = dff[(dff['He_II:P(SF)'] > 0) & (dff['He_II:P(AGN)'] == 0) &
                    (dff['BPT:P(SF)'] == 0)].shape[0]
    n_both_sf = dff[(dff['BPT:P(SF)'] > 0) & (
        dff['He_II:P(SF)'] > 0)].shape[0]
    data = [
        dict(
            type='pie',
            labels=['BPT', 'Both', 'HeII'],
            values=[n_bpt_agn, n_both_agn, n_heII_agn],
            name='AGN Classification Breakdown',
            text=['Total BPT classified AGN',
                  'Total BPT + HeII classified AGN', 'Total HeII classified AGN'],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(
                colors=['#fac1b7', '#a9bb95', '#92d8d8']
            ),
            domain={"x": [0, .44], 'y':[0.2, 0.8]},
        ),

        dict(
            type='pie',
            labels=['BPT', 'Both', 'HeII'],
            values=[n_bpt_sf, n_both_sf, n_heII_sf],
            name='Starforming Classification Breakdown',
            text=['Total BPT classified SF',
                  'Total BPT + HeII classified SF', 'Total HeII classified SF'],
            hoverinfo="label+text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(
                colors=['#fac1b7', '#a9bb95', '#92d8d8']
            ),
            domain={"x": [0.55, 1], 'y':[0.2, 0.8]},
            title='test',
        )
    ]
    layout_pie['title'] = 'Diagnostic classifiers comparison: BPT and HeII'
    layout_pie['font'] = dict(color='#777777')
    layout_pie['legend'] = dict(
        font=dict(color='#CCCCCC', size='14'),
        orientation='h',
        bgcolor='rgba(0,0,0,0)'
    )
    layout_pie['annotations'] = [
        {
            "font": {
                "size": 20,
                "color": '#CCCCCC',
            },
            "showarrow": False,
            "text": "AGN",
            "x": 0.17,
            "y": .9
        },
        {
            "font": {
                "size": 20,
                "color": '#CCCCCC',
            },
            "showarrow": False,
            "text": "SF",
            "x": 0.8,
            "y": 0.9
        }
    ]
    figure = dict(data=data, layout=layout_pie)
    return figure


# In[]:
# Main

if __name__ == '__main__':
    app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from plotly.subplots import make_subplots
import numpy as np


instr_dict = {}
year_list = []
month_list = []
start_year = []
start_month = []
labels = []
year_month = []
colors = ['#6A0101','#b60b06','#FAA8A8','#CDCDCD','#ABDFE9','#0B8DA6','#0B48A6']

df = pd.read_csv('new_order_data.csv')

run_df = pd.read_csv('ManGO_KPI_runs_20200221.csv')

months_dict = {1:'Jan',
               2:'Feb',
               3:'Mar',
               4:'Apr',
               5:'May',
               6:'Jun',
               7:'Jul',
               8:'Aug',
               9:'Sept',
               10:'Oct',
               11:'Nov',
               12:'Dec'}



for elt in run_df['date']:
    year_list.append(int(str(elt)[0:4]))
    month_list.append(int(str(elt)[5:7]))
    year_month.append(str(elt)[0:7])

run_df['start_year'] = year_list
run_df['start_month'] = month_list
run_df['year_month'] = year_month

for elt in df['start_date']:
    start_year.append(int(str(elt)[-4:]))
    start_month.append(int((str(elt).split('/'))[0]))

df['start_year'] = start_year
df['start_month'] = start_month

outliers = df[df['days_to_complete'] > 180].index
unknown = df[df['library_category']=='Unknown'].index

df.drop(outliers, inplace=True)
df.drop(unknown, inplace=True)

for elt in df['library_category'].unique():
    labels.append(elt)

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[

                html.P(html.Div(children=[html.H1('FGCZ',style={'color':'rgba(0,0,0,0)','background-image':'url(/assets/Background.png)','margin-top':'0'})])),

                html.P(html.H1('Performance Statistics', style={'fontFamily':'serif',
                                                        'padding-left':'5%'
                                                        })),

                html.Div(children=[

                    html.Div(children=[
                        html.Div(children=[
                            html.P(dcc.Graph(id='days_to_complete_by_lib_type',
                                            style={
                                            'width':'100%'
                                            }))
                    ]),

                    html.Div(children=[
                        html.P(html.P(dcc.Graph(id='number_orders_in_house',
                                        style={
                                        'width':'100%'
                                        })))
                    ])
                ], style={'columnCount':2})]),

                html.Div(children=[
                    html.P(dcc.RangeSlider(
                        id = 'year_picker',
                        marks = {i: str(i) for i in range(2014, 2021)},
                        min = 2014,
                        max = 2020,
                        value = [2014,2020]

                        ))],
                        style = {'padding-left':'30%',
                                'width':'40%',
                                }
                        ),
                html.H2('FGCZ Transcriptomics',style={'color':'rgba(0,0,0,0)'}),
                html.Div(children=[
                    html.Div(children=[dcc.Dropdown(id='library_selector',
                                                    options=[
                                                    {'label': 'Single Cell', 'value': 'SC'},
                                                    {'label': 'RNA Seq', 'value': 'RNA'},
                                                    {'label': 'DNA Seq', 'value': 'DNA'},
                                                    {'label': 'Exome Seq', 'value': 'Ex'},
                                                    {'label': 'Sequencing Only', 'value': 'RML'},
                                                    {'label': 'Others', 'value': 'Others'},
                                                    {'label': 'Low input RNA Seq', 'value': 'LI_RNA'},
                                                    {'label': 'All', 'value': 'All'},
                                                    ],
                                                    value='All',
                                                    style={
                                                    'width':'60%',
                                                    'padding-left':'30%',
                                                    'padding-top':'1%'
                                                            }
                                                    ),
                                    dcc.RadioItems(id = 'my_checkbox',
                                                    options=[
                                                        {'label': 'Mean Line', 'value': 'Line'},
                                                        {'label': 'Full Description', 'value': 'Box'}
                                                    ],
                                                    value='Box'
                                                ),

                                    dcc.Graph(id='overall_metrics',
                                                style={

                                    })])


                ], style={'border-style':'solid','width':'90%','margin':'auto','backgroundColor':'#2C394B'}),
                html.H1('By Griffin White',style={'color':'rgba(0,0,0,0)'}),
                html.Div(children=[
                    html.Div(children=[dcc.Dropdown(id='instrument_selector',
                                                    options=[
                                                    {'label': 'NovaSeq', 'value': 'NovaSeq'},
                                                    {'label': 'NextSeq', 'value': 'NextSeq'},
                                                    {'label': 'MiSeq', 'value': 'MiSeq'},
                                                    {'label': 'HiSeq2500', 'value': 'HiSeq2500'},
                                                    {'label': 'HiSeq4000', 'value': 'HiSeq4000'},
                                                    {'label': 'All', 'value':'All'}
                                                    ],
                                                    value='All',
                                                    style={
                                                    'width':'60%',
                                                    'padding-left':'30%',
                                                    'padding-top':'1%'
                                                            }
                                                    ),
                                                    dcc.RadioItems(id = 'my_checkbox_2',
                                                                    options=[
                                                                        {'label': 'Mean Line', 'value': 'Line'},
                                                                        {'label': 'Full Description', 'value': 'Box'}
                                                                    ],
                                                                    value='Box'
                                                                ),

                                    dcc.Graph(id='throughput',
                                                style={

                                    })])


                ], style={'border-style':'solid','width':'90%','margin':'auto','backgroundColor':'#2C394B'})
], style={'backgroundColor':'#3C4E66','fontFamily':'arial','border-style':'solid','border-color':'black'})

@app.callback(Output('overall_metrics','figure'),[Input('library_selector','value'),
                                                  Input('year_picker','value'),
                                                  Input('my_checkbox','value')])
def update_box(lib_type,years,display):

    our_df = df
    data = []

    if lib_type == 'SC':
        our_df = df[df['library_category']=='Single cell RNA Seq']
    elif lib_type == 'RNA':
        our_df = df[df['library_category']=='RNA Seq']
    elif lib_type == 'DNA':
        our_df = df[df['library_category']=='DNA Seq']
    elif lib_type == 'Ex':
        our_df = df[df['library_category']=='Exome Seq']
    elif lib_type == 'RML':
        our_df = df[df['library_category']=='Sequencing only']
    elif lib_type == 'Others':
        our_df = df[df['library_category']=='Others']
    elif lib_type == 'LI_RNA':
        our_df = df[df['library_category']=='Low input RNA Seq ']
    elif lib_type == 'All':
        our_df = df

    filtered_df = our_df
    scatterplot=[]
    xs = []

    fig = go.Figure()

    if display == 'Box':
        for year in range(years[0],years[1]+1):
            for month in range(1,13):
                if len(our_df[(our_df['start_year']==year)&(our_df['start_month']==month)]['start_month']) > 0:
                    filtered_df = our_df[(our_df['start_year']==year)&(our_df['start_month']==month)]
                    data = filtered_df['days_to_complete']
                    fig.add_trace(go.Box(y=data,
                                         name=str(months_dict[month]+' '+str(year)),
                                         marker_color=colors[year-2014]))
                else:
                    fig.add_trace(go.Box(y=[0],
                                         name=str(months_dict[month]+' '+str(year)),
                                         marker_color=colors[year-2014]
                                         ))
    if display == 'Line':
        data=int(0)

        for year in range(years[0],years[1]+1):
            for month in range(1,13):

                if len(our_df[(our_df['start_year']==year)&(our_df['start_month']==month)]['start_month']) > 0:
                    filtered_df = our_df[(our_df['start_year']==year)&(our_df['start_month']==month)]
                    data = filtered_df['days_to_complete'].mean()
                    scatterplot.append(data)
                    xs.append(str(months_dict[month]+' '+str(year)))

                else:
                    continue
        fig.add_trace(go.Scatter(x=xs,y=scatterplot,marker_color='yellow',mode='lines'))

    return fig.update_layout(template='plotly_dark',
                             paper_bgcolor='rgba(0,0,0,0)',
                             showlegend=False,
                             title='Number of Days to Complete Orders by Month',
                             yaxis={'title':'Number of Days'}
                            )


@app.callback(Output('number_orders_in_house','figure'),[Input('year_picker','value')])
def update_pie(selected_years):

    figure = []
    values = []
    final_labels = []
    temp_dict = dict({})

    if selected_years[0] != selected_years[1]:
        final_df = df[(df['start_year']>=selected_years[0]) & (df['start_year']<=selected_years[1])]

    else:
        final_df = df[df['start_year']==selected_years[0]]

    for elt in labels:
        if elt in final_df['library_category'].unique():
            temp_dict[str(elt)]=len(final_df[final_df['library_category']==elt]['library_category'])

# This unfortunate way of building the graph is necessary to garuntee that both graphs are built with items in the same order.

    for x in range(len(labels)):
        if str(labels[x]) in temp_dict.keys():
            values.append(temp_dict[labels[x]])
            final_labels.append(labels[x])

    return go.Figure(data=[go.Pie(labels=final_labels,
                                  values=values,
                                  sort=False)]).update_layout(template='plotly_dark',
                                                              title='Total Number of Orders by Library Type',
                                                              paper_bgcolor='rgba(0,0,0,0)',
                                                              font={'family':'arial'}
                                                              ).update_traces(marker=dict(colors=colors)
                                                                                )
#Calback updating the 'Number of Days to Complete Order by Month' barchart

@app.callback(Output('days_to_complete_by_lib_type', 'figure'),[Input('year_picker', 'value')])
def update_figure(selected_years):

    figure = []
    temp_dict = dict({})

    if selected_years[0] != selected_years[1]:
        final_df = df[(df['start_year']>=selected_years[0]) & (df['start_year']<=selected_years[1])]

    else:
        final_df = df[df['start_year']==selected_years[0]]

    for elt in labels:
        if elt in final_df['library_category'].unique():
            temp_dict[str(elt)]=[final_df[final_df['library_category']==elt]['days_to_complete'].mean()]

    for x in range(len(labels)):
        if str(labels[x]) in temp_dict.keys():
            figure.append(go.Bar(name=labels[x],y=temp_dict[labels[x]],marker_color=colors[x]))

    return go.Figure(figure).update_layout(template='plotly_dark',
                                            barmode='group',
                                            title = 'Mean Days to Complete Order by Library Type',
                                            xaxis={'title':str(selected_years[0])+' through '+str(selected_years[1])},
                                            yaxis={'title':'Days'},
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            showlegend=False,
                                            font={'family':'arial'}
                                            )

#Callback updating the throughput graph

@app.callback(Output('throughput', 'figure'), [Input('year_picker','value'),
                                               Input('instrument_selector','value'),
                                               Input('my_checkbox_2','value')])
def update_throughput(year, instrument, selection):

    fig = go.Figure()
    months = []
    vals = []

    if year[0] != year[1]:
        filtered1 = run_df[run_df['start_year']>=year[0]]
        filtered2 = filtered1[filtered1['start_year']<=year[1]]
        if instrument != 'All':
            filtered3 = filtered2[filtered2['instrument_name']==instrument]
        else:
            filtered3 = filtered2

    else:
        if instrument != 'All':
            filtered3 = run_df[(run_df['start_year']==year[0])&(run_df['instrument_name']==instrument)]
        else:
            filtered3 = run_df[run_df['start_year']==year[0]]

    if selection == 'Line':
        for yr in range(year[0], year[1]+1):
            for mon in range(1,13):
                if len(str(mon))==1:
                    tmp_df = filtered3[filtered3['year_month'] == str(yr)+'-0'+str(mon)]
                else:
                    tmp_df = filtered3[filtered3['year_month'] == str(yr)+'-'+str(mon)]
                vals.append(tmp_df['total_gigabases'].sum())
                months.append(str(str(months_dict[mon]) + ' ' + str(yr)))
        fig.add_trace(go.Scatter(x=months,y=vals,marker_color='yellow',mode='lines'))
        fig.update_layout(showlegend=False)

    if selection == 'Box':

        col = 0
        ys = []

        for instr in np.intersect1d(filtered3['instrument_name'].unique(),np.array(['NovaSeq', 'NextSeq','MiSeq', 'HiSeq2500', 'HiSeq4000'])):
            filtered4 = filtered3[filtered3['instrument_name'] == instr]
            for yr in range(year[0], year[1]+1):
                for mon in range(1,13):
                    if len(str(mon))==1:
                        tmp_df = filtered4[filtered4['year_month'] == str(yr)+'-0'+str(mon)]
                    else:
                        tmp_df = filtered4[filtered4['year_month'] == str(yr)+'-'+str(mon)]
                    tmp_date = str(str(months_dict[mon]) + ' ' + str(yr))
                    months.append(tmp_date)
                    ys.append(tmp_df['total_gigabases'].sum())

            vals.append(go.Bar(name=instr, x=months, y=ys,marker_color = colors[col]))
            ys = []
            col += 1

        fig = go.Figure(data=vals)
        fig.update_layout(barmode='stack',showlegend=True)


    return fig.update_layout(template='plotly_dark',
                         paper_bgcolor='rgba(0,0,0,0)',
                         title='Total Throughput',
                         yaxis={'title':'Total Throughput in Gb'}
                        )





if __name__ == '__main__':
    app.run_server(debug = True)

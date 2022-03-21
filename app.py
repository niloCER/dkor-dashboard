import dash
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.express as px
import pandas as pd
from pyvis.network import Network
import os
import dkor_nlp
import dkor_adjacency
import dkor_graph
import networkx as nx
from pyvis.network import Network
import networkx.algorithms.approximation as analysis
from networkx.algorithms import tree
import networkx.algorithms.dominating as dominating
import networkx.algorithms.centrality.degree_alg as dg_centrality
import networkx.algorithms.centrality.eigenvector as ev_centrality
import networkx.algorithms.assortativity.correlation as assortativity
import networkx.algorithms.efficiency_measures as efficiency
import networkx.algorithms.connectivity.connectivity as connectivity
import copy
from operator import itemgetter


"""
- Details
    - Degree of centrality
    - Number of mentions
    - strongest common ally
- Most likly to share position
- Dominating Set start with selected ms

Analysis - Button
- Maximum edged spanning tree

"""

ms = ['BEL','BGR','DNK','DEU','EST','FIN','FRA','GBR','GRC','IRL','ITA','HRV','LAT','LTU','LUX','MLT','NLD','AUT','POL','PRT','ROU','SWE','SVK','SVN','ESP','CZE','HUN','CYP']
ms_unsorted = copy.deepcopy(ms)
ms.sort()

# ms dictionary
ms_dict = {'BEL': 'Belgium','BGR': 'Bulgaria','DNK': 'Denmark','DEU': 'Germany','EST': 'Estonia','FIN': 'Finland','FRA': 'France','GBR': 'Great Britain','GRC': 'Greece','IRL': 'Ireland','ITA': 'Italy','HRV': 'Croatia','LAT': 'Latvia','LTU': 'Lithuania','LUX': 'Luxembourg','MLT': 'Malta','NLD': 'The Netherlands','AUT': 'Austria','POL': 'Poland','PRT': 'Portugal','ROU': 'Romania','SWE': 'Sweden','SVK': 'Slovakia','SVN': 'Slovenia','ESP': 'Spain','CZE': 'Czech Republic','HUN': 'Hungary','CYP': 'Cyprus'}

# dkor paths
directory_name = "./DKOR/DKORs_clean"
directory = os.fsencode(directory_name)
dkor_list = []
    
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".txt"): 
         dkor_list.append(filename)
         continue
     else:
         continue

# nx graph
nx_graph = nx.Graph()

# like-minded table
like_minded_table_data = {'Member State': ms, 'Degree of like-mindedness': [0]*len(ms)}
like_minded_table = pd.DataFrame(data=like_minded_table_data)
like_minded_table_dict = {}

# n_clicks_count
n_clicks_count = 0
dominating_set_n_clicks_count = 0
spanning_tree_button_n_clicks_count = 0
intermediary_n_clicks_counts = {}
for m in ms:
    intermediary_n_clicks_counts[m] = 0

def find_secondary(intermediary_dict):

    global intermediary_n_clicks_counts
    return_secondary = ""

    for m in ms:
        if intermediary_dict[m] == None:
            continue
        elif(intermediary_dict[m]>intermediary_n_clicks_counts[m]):
            return_secondary = m
            intermediary_n_clicks_counts[m] = intermediary_dict[m]

    return return_secondary

def find_intermediary(primary_id, secondary_id):
    primary_table = like_minded_table_dict[primary_id]
    secondary_table = like_minded_table_dict[secondary_id]
    intermediary_dict_list = []
    intermediary_ids = []

    for prim_index in range(0,len(ms)-1):
        for sec_index in range(prim_index,len(ms)):
            if primary_table.at[prim_index, 'Member State'] == secondary_table.at[sec_index, 'Member State'] and primary_table.at[prim_index, 'Degree of like-mindedness']!=0 and secondary_table.at[sec_index, 'Degree of like-mindedness']!=0:
                intermediary_dict_list.append({
                    'intermediary': primary_table.at[prim_index, 'Member State'], 
                    'sum': (int(primary_table.at[prim_index, 'Degree of like-mindedness']) + int(secondary_table.at[sec_index, 'Degree of like-mindedness']))})

    if intermediary_dict_list != []:
            intermediary_dict_list = sorted(intermediary_dict_list, key=itemgetter('sum'), reverse=True)

            if intermediary_dict_list[0]['sum'] != 0:
                intermediary_ids.append(intermediary_dict_list[0]['intermediary'])
                i = 1
                while(intermediary_dict_list[0]['sum'] == intermediary_dict_list[i]['sum']):
                    intermediary_ids.append(intermediary_dict_list[i]['intermediary'])
                    i+=1

    return intermediary_ids

def build_graph(directory_name,dkor_list):

    global like_minded_table_dict
    global nx_graph

    adjacency = dkor_adjacency.dkor_adjacency_preloaded_with_node_weights(directory_name, dkor_list)
    table = pd.DataFrame(data=like_minded_table_data)

# build networkx graph for analysis
    nx_adjacency = dkor_adjacency.dkor_adjacency_preloaded_without_node_weights(directory_name, dkor_list)
    nx_graph = nx.from_pandas_adjacency(nx_adjacency)
    nx_graph = nx_graph.to_undirected()
    nx.draw(nx_graph, with_labels = True)
    nt = Network('500px', '500px')
    nt.from_nx(nx_graph)
    nt.show('nx.html')

    #print(list(nx_graph.nodes(data=True)))
    #print(list(nx_graph.edges(data=True)))

    #print(list(analysis.maximum_independent_set(nx_graph)))
    #print(list(tree.maximum_spanning_edges(nx_graph, algorithm="kruskal", data=False)))
    #print(dominating.dominating_set(nx_graph, start_with='DEU'))
    #print(assortativity.degree_assortativity_coefficient(nx_graph)) # The assortativity ranges from –1 to +1, positive values meaning a tendency for nodes of similar degrees to connect to each other, negative values means that large-degree nodes tend to attach to low- degree nodes.
    #print(efficiency.global_efficiency(nx_graph)) # In network science, the efficiency of a network is a measure of how efficiently it exchanges information and it is also called communication efficiency. The underlying idea (and main assumption) is that the more distant two nodes are in the network, the less efficient their communication will be.
    #print(connectivity.average_node_connectivity(nx_graph))

# build like_minded_table_dic
    for m_primary in ms: 
        for m_secondary in ms:
            if adjacency.at[m_primary, m_primary] > 0:
                if m_primary == m_secondary:
                    table.at[table.index[table['Member State'] == m_secondary], 'Degree of like-mindedness'] = 0        
                elif m_primary > m_secondary:
                    table.at[table.index[table['Member State'] == m_secondary], 'Degree of like-mindedness'] = int(float(adjacency.at[m_secondary,m_primary])/float(adjacency.at[m_primary, m_primary])*100)
                else:
                    table.at[table.index[table['Member State'] == m_secondary], 'Degree of like-mindedness'] = int(float(adjacency.at[m_primary, m_secondary])/float(adjacency.at[m_primary, m_primary])*100)
            else:
                continue

        table = table.sort_values(by=['Degree of like-mindedness'], ascending=False)
        like_minded_table_dict[m_primary] = table
        table = pd.DataFrame(data=like_minded_table_data)

    #print(adjacency)
    #print(like_minded_table_dict['DEU'])

    return dkor_graph.dkor_graph_dict_preloaded(directory_name,dkor_list)

app = dash.Dash(
    external_stylesheets=[dbc.themes.SUPERHERO]
)


app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([


    html.Div([
        dbc.Row([
            html.H1(
            children='Master Thesis',
            style={'margin-top': 20, 'margin-left': 10}
            ),
        ]),

        dbc.Row([
            html.H6(
                children='Dash: A web application framework for your data.',
                style={'margin-left': 10}
            )
        ]),
    ], style={'background-color': '#0b69aa', 'margin-bottom': "5px"}),

    dbc.Row([

        dbc.Col([
            dbc.Row([
                html.Div([
                    html.H5(
                        children="About the project",
                        style={'margin-top': 10, 'margin-left': 5}),
                    html.P(
                        children="This is some card content that we'll reuse",
                        style={'margin-top': 10, 'margin-left': 5}),
                        
                ],style={"height": "100%", "background-color": "#2c3f53", 'border-style': 'solid', 'border-width': '1px', 'border-color': '#445462'}), 

            ],style={"height": "50%", "padding": 5}),

            dbc.Row([

                html.Div([
                    html.Div([
                        html.H5(
                        children='Diplomatic Correspondance',
                        style={'margin-bottom': 5, 'padding-bottom': 5, 'margin-top': 10, 'margin-left': 5}
                        ),
                    ]),

                    html.Div([
                        dcc.Checklist(
                            options=dkor_list, 
                            value=dkor_list,
                            id="dkor_checklist",
                            labelStyle=dict(display='block'),
                            style={'display': 'inline-block', 'margin-left': 10}
                        ),
                    ],style={'height': '65%', "overflow": "scroll"}),

                    html.Div([
                        dbc.Button(
                            "Build Graph", 
                            id="build_button", 
                            n_clicks=0, 
                            size="sm",
                            style={'margin-left': 10, 'margin-top': 15}
                        )
                    ]),

                ],style={"height": "100%", "background-color": "#2c3f53", 'border-style': 'solid', 'border-width': '1px', 'border-color': '#445462'}), 
            ],style={"height": "50%", "padding": 5})
        ],width={"size": 3}, style={"height": '650px'}),

        dbc.Col([
            html.Div([
                cyto.Cytoscape(
                    id='dkor_graph',
                    elements=build_graph(directory_name,dkor_list),
                    style={'width': '100%', 'height': '635px','display': 'inline-block'},
                    layout={
                        'name': 'cose',
                        'nodeRepulsion': 100000000,             # 'idealEdgeLength': 1000, 'nodeOverlap': 1000, 'nodeRepulsion': 100000, 'edgeElasticity': 600, 'gravity': 10
                        'nodeOverlap': 100000
                        },
                    stylesheet=[
                        {
                            'selector': 'label',                # as if selecting 'node' :/
                            'style': {'content': 'data(label)', 'color': '#ffffff', 'background-color': '#ffffff'}
                        },
                        {
                            'selector': '.node_not_selected',
                            'style': {'content': 'data(label)','background-color': '#109dff'}
                        },
                        {
                            # 'label': 'data(weight)',
                            'selector': '.edge_not_selected',
                            'style': {'line-color': '#0b69aa', 'width': 'data(weight)'}
                        },
                        {
                            'selector': '.node_primary',
                            'style': {'content': 'data(label)','background-color': '#84e6cb'} 
                        },
                        {
                            'selector': '.node_secondary',
                            'style': {'content': 'data(label)','background-color': '#08cc96'}
                        },
                        {
                            'selector': '.edge_primary',
                            'style': {'line-color': '#58baff', 'width': 'data(weight)'}
                        },
                        {
                            'selector': '.node_highlight',
                            'style': {'content': 'data(label)','background-color': '#FFD610'}
                        },
                        {
                            'selector': '.edge_highlight',
                            'style': {'line-color': '#C2AB3E', 'width': 'data(weight)'}
                        }
                    ]
                )
            ],style={"height": "100%", "background-color": "#2c3f53", 'border-style': 'solid', 'border-width': '1px', 'border-color': '#445462'}), 
        ],width={"size": 6},style={"height": '650px', "padding": "5px"}),

        dbc.Col([

            dbc.Row([
                html.Div([
                    html.Div([
                        html.H5(
                            children="Select Member State in Graph", # replace with ms-name - Details when selected
                            id='details',
                            style={'margin-bottom': 5, 'padding-bottom': 5, 'margin-top': 10}),

                        html.Div([
                            html.P(
                                children="Total number of mentions: ", # replace with ms-name - Details when selected
                                id='mentions',
                                style={'padding-left': 8, 'margin': 2}),
                        
                            html.P(
                                children="Degree Centrality:", # replace with ms-name - Details when selected
                                id='degree_centrality',
                                style={'padding-left': 8, 'margin': 2}),

                            html.P(
                                children="Eigenvektor Centrality:", # replace with ms-name - Details when selected
                                id='eigenvektor_centrality',
                                style={'padding-left': 8, 'margin': 2}),
                        ], style={'margin-bottom': 10}),

                        html.P(
                            children="Strongest intermediary:", # replace with ms-name - Details when selected
                            id='strongest_intermediary',
                            style={'padding-left': 8, 'margin': 2}),

                        #dcc.Dropdown(ms, 'title', style={'margin-bottom': 10})
                        dbc.DropdownMenu(
                            label="Select Member State",
                            children=[dbc.DropdownMenuItem(ms_dict[m], id=m) for m in ms],
                            style = {'margin-left': 15, 'margin-top': 5},
                            size="sm",
                            id='intermediary_dropdown',
                            disabled = True
                        )
                    ],style={"maxHeight": "75%"}, id='analysis_container'),

                    html.Div([
                        html.H6(
                            children="Most like-minded Member States",
                            style={'margin-bottom': 5, 'padding-bottom': 5, 'margin-top': 10, 'padding-left': 10})
                    ]),

                    html.Div([
                        dbc.Table.from_dataframe(
                            like_minded_table, 
                            striped=True, 
                            bordered=True,
                            hover=True)
                    ],style={"maxHeight": "33%", "overflow": "scroll", 'margin-left': 15, 'margin-right': 10, 'font-size': '15px'}, id='like_minded_table_container'),

                    dbc.Button(
                            "Show Dominating Set", 
                            id="dominating_set_button", 
                            n_clicks=0, 
                            size="sm",
                            style={'margin-left': 10, 'margin-top': 15},
                            disabled=True
                    )

                ],style={'height': '100%', "maxHeight": "100%", "background-color": "#2c3f53", 'border-style': 'solid', 'border-width': '1px', 'border-color': '#445462',}), 
            ],style={"height": "66%", "padding": 5}),

            dbc.Row([
                html.Div([
                    html.H5(
                        children="General Analysis",
                        style={'margin-bottom': 5, 'padding-bottom': 5, 'margin-top': 10}),

                    html.Div([
                        html.P(
                            children= str("Total Number of Connections: " + str(round(nx_graph.number_of_edges(),2))), # replace with ms-name - Details when selected
                            id='total_edges',
                            style={'padding-left': 8, 'margin': 2}),

                        html.P(
                            children=str("Average Connectivity: " + str(round(connectivity.average_node_connectivity(nx_graph),2))), # replace with ms-name - Details when selected
                            id='average_connectivity',
                            style={'padding-left': 8, 'margin': 2}),

                        html.P(
                            children=str("Assortativity: " + str(round(assortativity.degree_assortativity_coefficient(nx_graph),2))), # replace with ms-name - Details when selected
                            id='assortativity',
                            style={'padding-left': 8, 'margin': 2}),
                        
                        html.P(
                            children=str("Global Efficiency: " + str(round(efficiency.global_efficiency(nx_graph),2))), # replace with ms-name - Details when selected
                            id='global_efficiency',
                            style={'padding-left': 8, 'margin': 2}),
                    ]),

                    dbc.Button(
                        "Maximum Spanning Tree", 
                        id="spanning_tree_button", 
                        n_clicks=0, 
                        size="sm",
                        style={'margin-left': 10, 'margin-top': 15}
                    )

                ],style={"maxHeight": "100%", "background-color": "#2c3f53", 'border-style': 'solid', 'border-width': '1px', 'border-color': '#445462'}), 
            ],style={"height": "34%", "padding": 5}),

        ],width={"size": 3}, style={"height": '650px'}),

    ]),

    dbc.Row([
            html.Footer(
            children='Footer',
            style={'height': '100%', 'vertical-align': 'middle', 'text-align': 'right'}
            ),
    ],style= {'background-color': '#2c3f53', 'border-style': 'solid', 'border-width': '1px', 'border-color': '#445462', 'height': 35, 'vertical-align': 'middle'}),

])

# select ms
@app.callback(
    Output("dkor_graph", "elements"),
    Output("details", "children"),
    Output("mentions", "children"),
    Output("degree_centrality", "children"),
    Output("eigenvektor_centrality", "children"),
    Output("like_minded_table_container", "children"),
    Output("intermediary_dropdown", "label"),
    Output("intermediary_dropdown", "disabled"),
    Output("dominating_set_button", "disabled"),
    Output("strongest_intermediary","children"),
    Output("total_edges","children"),
    Output("average_connectivity","children"),
    Output("assortativity","children"),
    Output("global_efficiency","children"),


    [Input("build_button", "n_clicks")],
    Input("dkor_graph", "elements"),
    [Input("dkor_graph", "tapNode")],
    [Input("dominating_set_button", "n_clicks")],
    [Input("spanning_tree_button", "n_clicks")],
    Input("dominating_set_button", "disabled"),
    Input("intermediary_dropdown", "disabled"),

    [Input("BEL", "n_clicks")],
    [Input("BGR", "n_clicks")], 
    [Input("DNK", "n_clicks")], 
    [Input("DEU", "n_clicks")], 
    [Input("EST", "n_clicks")], 
    [Input("FIN", "n_clicks")], 
    [Input("FRA", "n_clicks")], 
    [Input("GBR", "n_clicks")], 
    [Input("GRC", "n_clicks")], 
    [Input("IRL", "n_clicks")], 
    [Input("ITA", "n_clicks")], 
    [Input("HRV", "n_clicks")], 
    [Input("LAT", "n_clicks")], 
    [Input("LTU", "n_clicks")], 
    [Input("LUX", "n_clicks")], 
    [Input("MLT", "n_clicks")], 
    [Input("NLD", "n_clicks")],
    [Input("AUT", "n_clicks")], 
    [Input("POL", "n_clicks")], 
    [Input("PRT", "n_clicks")], 
    [Input("ROU", "n_clicks")], 
    [Input("SWE", "n_clicks")], 
    [Input("SVK", "n_clicks")], 
    [Input("SVN", "n_clicks")], 
    [Input("ESP", "n_clicks")], 
    [Input("CZE", "n_clicks")], 
    [Input("HUN", "n_clicks")], 
    [Input("CYP", "n_clicks")],

    [State("dkor_checklist", "value")],
    prevent_initial_call=True
)

def refresh(n, elements, graph_tapNode, dominating_set_n, spanning_tree_button_n, dominating_set_disable, intermediary_dropdown_disable, intermediary_dropdown_BEL, intermediary_dropdown_BGR, intermediary_dropdown_DNK, intermediary_dropdown_DEU, intermediary_dropdown_EST, intermediary_dropdown_FIN, intermediary_dropdown_FRA, intermediary_dropdown_GBR, intermediary_dropdown_GRC, intermediary_dropdown_IRL, intermediary_dropdown_ITA, intermediary_dropdown_HRV, intermediary_dropdown_LAT, intermediary_dropdown_LTU, intermediary_dropdown_LUX, intermediary_dropdown_MLT, intermediary_dropdown_NLD, intermediary_dropdown_AUT, intermediary_dropdown_POL, intermediary_dropdown_PRT, intermediary_dropdown_ROU, intermediary_dropdown_SWE, intermediary_dropdown_SVK, intermediary_dropdown_SVN, intermediary_dropdown_ESP, intermediary_dropdown_CZE, intermediary_dropdown_HUN, intermediary_dropdown_CYP, selected):

    global n_clicks_count
    global dominating_set_n_clicks_count
    global spanning_tree_button_n_clicks_count
    global nx_graph

    intermediary_list_unlabled = [intermediary_dropdown_BEL, intermediary_dropdown_BGR, intermediary_dropdown_DNK, intermediary_dropdown_DEU, intermediary_dropdown_EST, intermediary_dropdown_FIN, intermediary_dropdown_FRA, intermediary_dropdown_GBR, intermediary_dropdown_GRC, intermediary_dropdown_IRL, intermediary_dropdown_ITA, intermediary_dropdown_HRV, intermediary_dropdown_LAT, intermediary_dropdown_LTU, intermediary_dropdown_LUX, intermediary_dropdown_MLT, intermediary_dropdown_NLD, intermediary_dropdown_AUT, intermediary_dropdown_POL, intermediary_dropdown_PRT, intermediary_dropdown_ROU, intermediary_dropdown_SWE, intermediary_dropdown_SVK, intermediary_dropdown_SVN, intermediary_dropdown_ESP, intermediary_dropdown_CZE, intermediary_dropdown_HUN, intermediary_dropdown_CYP,]
    
    intermediary_dict = {}

    for i in range(0,len(intermediary_list_unlabled)):
        intermediary_dict[ms_unsorted[i]] = intermediary_list_unlabled[i]

    intermediary_secondary = ""
    intermediary_secondary = find_secondary(intermediary_dict)
    return_intermediary_label = "Select Member State"

    elements = elements
    return_details_label = "Select Member State"
    return_mentions_label = "Total number of mentions: "
    return_degree_centrality_label = "Degree Centrality:"
    return_eigenvektor_centrality_label = "Eigenvektor Centrality:"
    return_table = dbc.Table.from_dataframe(like_minded_table, striped=True, bordered=True,hover=True)
    return_intermediary_secondary_label = "Strongest intermediary:"
    return_total_edges = "Total Number of Connections: " + str(round(nx_graph.number_of_edges(),2))
    return_average_connectivity = "Average Connectivity: " + str(round(connectivity.average_node_connectivity(nx_graph),2))
    return_assortativity = "Assortativity: " + str(round(assortativity.degree_assortativity_coefficient(nx_graph),2))
    return_global_efficiency = "Global Efficiency: " + str(round(efficiency.global_efficiency(nx_graph),2))

    #update dkors
    if n > n_clicks_count:
        n_clicks_count = n
        if len(selected)>0:
            elements=build_graph(directory_name,selected)
        elif len(selected)==0:
            dash.exceptions.PreventUpdate

        intermediary_dropdown_disable = True
        dominating_set_disable = True

    elif spanning_tree_button_n > spanning_tree_button_n_clicks_count:
        spanning_tree = list(tree.maximum_spanning_edges(nx_graph, algorithm="kruskal", data=False))
        print(spanning_tree)

        for e in elements:
            for edge in spanning_tree:
                if e['data']['id'] == edge[0] or e['data']['id'] == edge[1]:
                        e['classes'] = 'node_highlight'
                if e['data']['id'] == str(edge[0] + "_" + edge[1]) or e['data']['id'] == str(edge[1] + "_" + edge[0]):
                    e['classes'] = 'edge_highlight'

        spanning_tree_button_n_clicks_count = spanning_tree_button_n

    # select ms
    else:
        primary_id = graph_tapNode['data']['id']

        # highlight intermediary
        return_intermediary_secondary_label = "Strongest intermediary: " + ms_dict[primary_id] + " and"

        if intermediary_secondary != "" and intermediary_dropdown_disable == False:
            return_intermediary_label = ms_dict[intermediary_secondary]
            intermediary_ids = find_intermediary(primary_id, intermediary_secondary)
            #print(intermediary_ids)

        # highlight dominant set with ms
        if dominating_set_n > dominating_set_n_clicks_count and dominating_set_disable == False:
            dominating_set = dominating.dominating_set(nx_graph, start_with=primary_id)

        table = pd.DataFrame(data=like_minded_table_data)
        percent = pd.DataFrame(data={'percent': ["%"]*len(ms)})

        for e in elements:
            if e['classes'] == 'node_primary' or e['classes'] == 'node_secondary' or e['classes'] == 'node_highlight':
                e['classes'] = 'node_not_selected'
            
            if e['classes'] == 'edge_primary' or e['classes'] == 'edge_highlight':
                e['classes'] = 'edge_not_selected'

            if e['data'] == graph_tapNode['data']:
                e['classes'] = 'node_primary'
            
            for edge in graph_tapNode['edgesData']:
                if (e['data']['id'] == edge['source'] and primary_id == edge['target']) or (primary_id == edge['source'] and e['data']['id'] == edge['target']):
                    e['classes'] = 'node_secondary'
                if e['data']['id'] == str(edge['source'] + "_" + edge['target']) or e['data']['id'] == str(edge['target'] + "_" + edge['source']):
                    e['classes'] = 'edge_primary'
            
            # color intermediary nodes and edges
            if intermediary_secondary != "" and intermediary_dropdown_disable == False:
                if e['data']['id'] == intermediary_secondary:
                            e['classes'] = 'node_highlight'

                if e['data'] == graph_tapNode['data']:
                        e['classes'] = 'node_highlight'

                if intermediary_ids !=[]:
                    for intermediaries in intermediary_ids:
                        if e['data']['id'] == intermediaries:
                            e['classes'] = 'node_highlight'
                        if e['data']['id'] == str(intermediaries + "_" + primary_id) or e['data']['id'] == str(primary_id + "_" + intermediaries):
                            e['classes'] = 'edge_highlight'
                        if e['data']['id'] == str(intermediaries + "_" + intermediary_secondary) or e['data']['id'] == str(intermediary_secondary + "_" + intermediaries):
                            e['classes'] = 'edge_highlight'

                    if e['data']['id'] == str(intermediary_secondary + "_" + primary_id) or e['data']['id'] == str(primary_id + "_" + intermediary_secondary):
                        e['classes'] = 'edge_highlight'

            # color dominating set
            if dominating_set_n > dominating_set_n_clicks_count and dominating_set_disable == False:
                if e['data']['id'] in dominating_set:
                    e['classes'] = 'node_highlight'

                if e['classes'] == 'edge_primary' or e['classes'] == 'edge_highlight' or e['classes'] == 'edge_not_selected':
                    edge_split = copy.deepcopy(e['data']['id'])
                    edge_split = edge_split.split("_")
                    for s in dominating_set:
                        if e['data']['id'] == str(edge_split[0] + "_" + s) or e['data']['id'] == str(s + "_" + edge_split[1]):
                            e['classes'] = 'edge_highlight'

        dominating_set_n_clicks_count = dominating_set_n

        table = like_minded_table_dict[primary_id].copy(deep=True)
        table['Degree of like-mindedness'] = table['Degree of like-mindedness'].map(str) + " " + percent['percent']

        return_details_label = str("Details - " + ms_dict[primary_id])
        return_mentions_label = "Total number of mentions: " + str(graph_tapNode['data']['weight'])
        return_degree_centrality_label = "Degree Centrality: " + str(round(dg_centrality.degree_centrality(nx_graph)[primary_id],2))
        return_eigenvektor_centrality_label = "Eigenvektor Centrality: " + str(round(ev_centrality.eigenvector_centrality(nx_graph)[primary_id],2))
        return_table = dbc.Table.from_dataframe(table, striped=True, bordered=True, hover=True)

        intermediary_dropdown_disable = False
        dominating_set_disable = False

    return elements, return_details_label, return_mentions_label, return_degree_centrality_label, return_eigenvektor_centrality_label, return_table, return_intermediary_label, intermediary_dropdown_disable, dominating_set_disable, return_intermediary_secondary_label, return_total_edges, return_average_connectivity, return_assortativity, return_global_efficiency

if __name__ == '__main__':
    app.run_server(debug=True)
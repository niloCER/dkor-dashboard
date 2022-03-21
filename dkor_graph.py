import os
from pyvis.network import Network
import pandas as pd
import dkor_nlp
import dkor_adjacency

ms = ['BEL','BGR','DNK','DEU','EST','FIN','FRA','GBR','GRC','IRL','ITA','HRV','LAT','LTU','LUX','MLT','NLD','AUT','POL','PRT','ROU','SWE','SVK','SVN','ESP','CZE','HUN','CYP']
ms.sort()

# dkor paths
directory_name = "./DKORs_clean"
directory = os.fsencode(directory_name)
dkor_list = []
    
for file in os.listdir(directory):
     filename = os.fsdecode(file)
     if filename.endswith(".txt"): 
         dkor_list.append(filename)
         continue
     else:
         continue

# graph from set of dkors
def dkor_graph(directory_name, dkor_list):

    # get adjacency matrix
    dkor_df = dkor_adjacency.dkor_adjacency(directory_name, dkor_list)

    # build network
    dkor_net = Network(height='100%', width='100%')

    # add nodes
    dkor_net.add_nodes(ms)


    # add edges
    for i in range(0,len(ms)-1):
        for j in range(i+1,len(ms)):
            #print(ms[i], ms[j],dkor_df.at[ms[j],ms[i]])
            if(dkor_df.at[ms[i],ms[j]]>0):
                dkor_net.add_edge(ms[i], ms[j],weight=dkor_df.at[ms[i],ms[j]],value=dkor_df.at[ms[i],ms[j]])
        
    #print(dkor_net.get_edges())

    # network graphic
    dkor_net.repulsion(node_distance=150, central_gravity=0.01, spring_length=400, spring_strength=0.01, damping=0.05)

    # show network
    #dkor_net.show('dkor_graph.html')
    return dkor_net

# graph from adjacency matrix
def dkor_graph_from_adjacency(dkor_df):

    # build network
    dkor_net = Network(height='100%', width='100%')

    # add nodes
    dkor_net.add_nodes(ms)

    # add edges
    for i in range(0,len(ms)-1):
        for j in range(i+1,len(ms)):
            #print(ms[i], ms[j],dkor_df.at[ms[j],ms[i]])
            if(dkor_df.at[ms[i],ms[j]]>0):
                dkor_net.add_edge(ms[i], ms[j],weight=dkor_df.at[ms[i],ms[j]],value=dkor_df.at[ms[i],ms[j]])
        
    #print(dkor_net.get_edges())

    # network graphic
    dkor_net.repulsion(node_distance=150, central_gravity=0.01, spring_length=400, spring_strength=0.01, damping=0.05)

    # show network
    #dkor_net.show('dkor_graph.html')
    return dkor_net

def dkor_graph_dict(directory_name, dkor_list):

    # get adjacency matrix
    dkor_df = dkor_adjacency.dkor_adjacency(directory_name, dkor_list)

    # add nodes
    nodes_list = []
    for m in ms:
        nodes_list.append({'data': {'id': m, 'label': m}, 'classes': 'node_not_selected'})

    # add edges
    edges_list = []
    for i in range(0,len(ms)-1):
        for j in range(i+1,len(ms)):
            #print(ms[i], ms[j],dkor_df.at[ms[j],ms[i]])
            if(dkor_df.at[ms[i],ms[j]]>0):
                edges_list.append({'data': {'source': ms[i], 'target': ms[j], 'weight': dkor_df.at[ms[i],ms[j]], 'id': str(ms[i] + "_" + ms[j])}, 'classes': 'edge_not_selected'})
                #edges_list.append(ms[i], ms[j],dkor_df.at[ms[i],ms[j]])
        
    return nodes_list + edges_list

def dkor_graph_dict_preloaded(directory_name, dkor_list):

    # get adjacency matrix
    dkor_df = dkor_adjacency.dkor_adjacency_preloaded_with_node_weights(directory_name, dkor_list)

    # add nodes
    nodes_list = []
    for m in ms:
        nodes_list.append({'data': {'id': m, 'label': m, 'weight': dkor_df.at[m,m]}, 'classes': 'node_not_selected'})

    # add edges
    edges_list = []
    for i in range(0,len(ms)-1):
        for j in range(i+1,len(ms)):
            #print(ms[i], ms[j],dkor_df.at[ms[j],ms[i]])
            if(dkor_df.at[ms[i],ms[j]]>0):
                edges_list.append({'data': {'source': ms[i], 'target': ms[j], 'weight': dkor_df.at[ms[i],ms[j]], 'id': str(ms[i] + "_" + ms[j])}, 'classes': 'edge_not_selected'})
                #edges_list.append(ms[i], ms[j],dkor_df.at[ms[i],ms[j]])

    #print(nodes_list + edges_list)     
        
    return nodes_list + edges_list

"""
Ideas: include spellchecking 

"""

import os
from re import split
import pandas as pd
import numpy as np
import dkor_nlp

# prebuild
dkor_dict = {
    '20130716_JI ReferentInnen EU US Gruppe.txt': [['FRA', 'DEU', 'ESP', 'POL', 'SWE', 'BEL', 'NLD'], ['EST', 'AUT', 'SVN'], ['CZE', 'GBR']],
    '20130724_AStV 2 EU US Gruppe.txt': [['LUX', 'DEU', 'ITA']],
    '20130625_TAG CORTA EU US Datenschutzabkommen.txt': [['DEU', 'GBR', 'SWE'], ['DEU', 'GBR', 'SWE'], ['DEU', 'FRA'], ['DEU', 'NLD', 'FRA', 'GBR'], ['NLD', 'FRA']],
    '20130624_JI ReferentInnen EU US Gruppe.txt': [['FRA', 'ESP', 'GBR', 'LUX'], ['FRA', 'GBR'], ['FRA', 'ESP', 'GBR', 'LUX'], ['FRA', 'GBR']],
    '20130715_JI ReferentInnen EU US Gruppe.txt': [['EST', 'POL', 'SVN'], ['ESP', 'DEU', 'FRA', 'SWE', 'BEL']],
    '20130710_AStV 2 EU US Gruppe.txt': [['GBR', 'FRA', 'IRL', 'SVN', 'ITA', 'DNK', 'NLD', 'CZE', 'ESP', 'BGR', 'SWE', 'HUN', 'POL', 'SVK', 'LUX', 'ROU'], ['NLD', 'LUX', 'IRL'], ['FRA', 'IRL', 'GBR', 'SWE', 'POL', 'LUX', 'ESP'], ['ESP', 'LUX', 'POL'], ['GBR', 'NLD', 'ITA']],
    '20130704_AStV 2 EU US Gruppe.txt': [['GBR', 'SWE'], ['FRA', 'DEU', 'DNK', 'NLD', 'BEL', 'AUT', 'ITA', 'GRC', 'PRT', 'FIN', 'HUN', 'BGR'], ['GBR', 'SWE'], ['FRA', 'NLD', 'ITA', 'GRC', 'ESP', 'DNK', 'BEL', 'DEU'], ['GBR', 'EST', 'FRA', 'DEU', 'ITA', 'DNK', 'NLD', 'PRT', 'ROU'], ['EST', 'NLD', 'SWE'], ['FRA', 'DEU', 'DNK', 'NLD', 'BEL', 'AUT', 'ITA', 'GRC', 'PRT', 'FIN', 'HUN', 'BGR'], ['DEU', 'DNK', 'NLD'], ['DEU', 'DNK', 'ROU', 'NLD', 'FIN', 'LUX'], ['GBR', 'SWE'], ['SVN', 'MLT', 'LUX'], ['FRA', 'ITA', 'MLT', 'GRC'], ['GBR', 'FRA'], ['SWE', 'POL', 'EST', 'SVN', 'CZE'], ['ROU', 'BGR', 'HUN']],
    '20130718_AStV 2 EU US Gruppe.txt': [['AUT', 'CZE'], ['DEU', 'CZE', 'DNK', 'POL', 'NLD', 'ITA', 'ESP', 'PRT', 'SVK', 'SVN', 'SWE', 'BEL'], ['FRA', 'DEU', 'ESP', 'BEL', 'DNK']]
}

ms = ['BEL','BGR','DNK','DEU','EST','FIN','FRA','GBR','GRC','IRL','ITA','HRV','LAT','LTU','LUX','MLT','NLD','AUT','POL','PRT','ROU','SWE','SVK','SVN','ESP','CZE','HUN','CYP']
ms.sort()

def dkor_adjacency(directory_name, dkor_list):
    
    # dkor to cluster_list
    cluster_list = []

    for f in dkor_list:
        cluster_list = cluster_list + dkor_nlp.dkor_nlp(directory_name + "/" + f)

    #print(cluster_list)

    # edge weights dataframe
    dkor_df = pd.DataFrame(None,columns=ms,index=ms)

    for i in range(0,len(ms)-1):
        for j in range(i+1,len(ms)):
            dkor_df.iat[i,j] = 0

    # get edge weights
    for ms_cluster in cluster_list:
        for i in range(0,len(ms_cluster)-1):
            for j in range(i+1,len(ms_cluster)):
                if ms_cluster[i]<ms_cluster[j]:
                    dkor_df.at[ms_cluster[i],ms_cluster[j]] += 1
                    #print("edge: " + ms_cluster[i] + " + " + ms_cluster[j])
                else:
                    dkor_df.at[ms_cluster[j],ms_cluster[i]] += 1
                    #print("edge: " + ms_cluster[j] + " + " + ms_cluster[i])

    #print(dkor_df)
    return dkor_df

def dkor_adjacency_preloaded_with_node_weights(directory_name, dkor_list):
        
    # dkor to cluster_list
    cluster_list = []

    for f in dkor_list:
        cluster_list = cluster_list + dkor_dict[f]

    #print(cluster_list)

    # edge weights dataframe
    dkor_df = pd.DataFrame(None,columns=ms,index=ms)

    for i in range(0,len(ms)):
        for j in range(i,len(ms)):
            dkor_df.iat[i,j] = 0

    # get edge weights
    for ms_cluster in cluster_list:
        for i in range(0,len(ms_cluster)-1):
            for j in range(i+1,len(ms_cluster)):
                if ms_cluster[i]<ms_cluster[j]:
                    dkor_df.at[ms_cluster[i],ms_cluster[j]] += 1
                    #print("edge: " + ms_cluster[i] + " + " + ms_cluster[j])
                else:
                    dkor_df.at[ms_cluster[j],ms_cluster[i]] += 1
                    #print("edge: " + ms_cluster[j] + " + " + ms_cluster[i])

    for ms_cluster in cluster_list:
        for m in ms_cluster:
            dkor_df.at[m,m] += 1

    #print(dkor_df)
    return dkor_df

def dkor_adjacency_preloaded_without_node_weights(directory_name, dkor_list):
        
    # dkor to cluster_list
    cluster_list = []

    for f in dkor_list:
        cluster_list = cluster_list + dkor_dict[f]

    #print(cluster_list)

    # edge weights dataframe
    dkor_df = pd.DataFrame(0,columns=ms,index=ms)

    # get edge weights
    for ms_cluster in cluster_list:
        for i in range(0,len(ms_cluster)-1):
            for j in range(i+1,len(ms_cluster)):
                if ms_cluster[i]<ms_cluster[j]:
                    dkor_df.at[ms_cluster[i],ms_cluster[j]] += 1
                    #print("edge: " + ms_cluster[i] + " + " + ms_cluster[j])
                else:
                    dkor_df.at[ms_cluster[j],ms_cluster[i]] += 1
                    #print("edge: " + ms_cluster[j] + " + " + ms_cluster[i])

    #print(dkor_df)
    return dkor_df

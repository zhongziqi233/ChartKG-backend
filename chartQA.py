import re
import json
import networkx as nx
from collections import defaultdict


def run_chart_QA(qs, chart, type):
    graphPath = f"./data/{chart.split(' ')[0]}/graphs_current/{chart.split(' ')[1]}.json"
    if type == 'DC':
        return answer_DC(qs, graphPath)
    elif type == 'VE':
        return answer_VE(qs, graphPath)
    elif type == 'VI':
        return answer_VI(qs, graphPath)
    else:
        raise Exception("错误的QA类型")


def answer_DC(qs, graphPath):
    # print("Question: ", qs, sep='\n')
    items = re.findall(r'\{(.*?)\}', qs)
    item1 = items[0]
    item2 = items[1]
    h1 = 0
    h2 = 0
    # print("Items: ", item1, item2, sep='\n')
    with open(graphPath, 'r', encoding='utf-8') as f:
        graph_ = json.load(f)
        graph = {
            'directed': False,
            'multigraph': True,
            'nodes': graph_['nodes'],
            'links': graph_['edges'],
        }
        G = nx.node_link_graph(graph)
        TBM, LBM, BHM = construct_DC_mapper(G)
        # print("Mappers: ", TBM, LBM, BHM, sep='\n')

        collection1  = [None, None]
        collection2 = [None, None]

        for k in TBM.keys():
            if k in item1:
                collection1[0] = TBM[k]
            if k in item2:
                collection2[0] = TBM[k]
        if len(LBM.keys()) > 0:
            for k in LBM.keys():
                if k in item1:
                    collection1[1] = LBM[k]
                if k in item2:
                    collection2[1] = LBM[k]
            h1 = BHM[[_ for _ in collection1[0] if _ in collection1[1]][0]]
            h2 = BHM[[_ for _ in collection2[0] if _ in collection2[1]][0]]
        else:
            h1 = BHM[collection1[0][0]]
            h2 = BHM[collection2[0][0]]

        ifmore = h1 > h2
        ifmoreQ = 'more than' in qs

        if 'equal' in qs and h1 == h2:
            return True
        elif ifmore == ifmoreQ:
            return True
        else:
            return False


def answer_VE(qs, graphPath):
    # print("Question: ", qs, sep='\n')
    with open(graphPath, 'r', encoding='utf-8') as f:
        graph_ = json.load(f)
        graph = {
            'directed': False,
            'multigraph': True,
            'nodes': graph_['nodes'],
            'links': graph_['edges'],
        }
        G = nx.node_link_graph(graph)
        color_legend_mapper = construct_VE_mapper(G)
        # print("Mappers:", color_legend_mapper, sep='\n')
        for k in color_legend_mapper.keys():
            if k in qs:
                return color_legend_mapper[k]
        return G.nodes['y_title']['name']


def answer_VI(qs, graphPath):
    # print("Question: ", qs, sep='\n')
    with open(graphPath, 'r', encoding='utf-8') as f:
        graph_ = json.load(f)
        graph = {
            'directed': False,
            'multigraph': True,
            'nodes': graph_['nodes'],
            'links': graph_['edges'],
        }
        G = nx.node_link_graph(graph)
        insight_tick_mapper, insight_legend_mapper = construct_VI_mapper(G)
        # print("Mapper: ", insight_tick_mapper, insight_legend_mapper, sep='\n')
        if qs.startswith('Which '):
            for k1 in insight_tick_mapper.keys():
                if k1 in qs:
                    for k2 in insight_tick_mapper[k1].keys():
                        answer = f"{k1} is the one of "
                        for idx, label in enumerate(insight_legend_mapper[k1][k2]):
                            if idx == 0:
                                answer += f"{label}"
                            else:
                                answer += f" and {label}"
                        answer += " in "
                        for idx, label in enumerate(insight_tick_mapper[k1][k2]):
                            if idx == 0:
                                answer += f"{label}"
                            else:
                                answer += f" and {label}"
            return answer
        elif qs.startswith('What is the ') and " obvious visual insight " in qs:
            answer = ""
            for idx, k in enumerate(insight_tick_mapper.keys()):
                if idx == 0:
                    answer += f"{k}"
                else:
                    answer += f" and {k}"
            return answer
        elif qs.startswith('What is the ') and " trend " in qs:
            answer = "unknown"
            for k1 in insight_legend_mapper.keys():
                if 'trend' in k1.lower():
                    for k2 in insight_legend_mapper[k1].keys():
                        if insight_legend_mapper[k1][k2][0].lower() in qs.lower():
                            answer = f"{k1}"
            return answer
        else:
            raise Exception("未定义的QA模板")

def construct_DC_mapper(G):
    valid_paths1 = find_specific_structure(G, ['VE', 'VEPV', 'DVV'])
    tick_bar_mapper = {}
    legend_bar_mapper = {}
    for item in valid_paths1:
        if item[1].startswith('Position'):
            if G.has_node(item[0]) and G.has_node(item[2]):
                node_info = G.nodes[item[2]]
                if node_info['name'] in tick_bar_mapper.keys():
                    tick_bar_mapper[node_info['name']].append(item[0])
                else:
                    tick_bar_mapper[node_info['name']] = [item[0]]
        elif item[1].startswith('Color'):
            if G.has_node(item[0]) and G.has_node(item[2]):
                node_info = G.nodes[item[2]]
                if node_info['name'] in legend_bar_mapper.keys():
                    legend_bar_mapper[node_info['name']].append(item[0])
                else:
                    legend_bar_mapper[node_info['name']] = [item[0]]

    valid_paths2 = find_specific_structure(G, ['VE', 'VEPV', 'DV'])
    bar_height_mapper = {}
    for item in valid_paths2:
        if G.has_node(item[0]) and G.has_node(item[1]):
            node_info = G.nodes[item[1]]
            bar_height_mapper[item[0]] = node_info['name']
    return tick_bar_mapper, legend_bar_mapper, bar_height_mapper


def construct_VE_mapper(G):
    valid_paths = find_specific_structure(G, ['VEPV', 'DVV'])
    color_legend_mapper = {}
    for item in valid_paths:
        if item[0].startswith('Color'):
            if G.has_node(item[0]) and G.has_node(item[1]):
                node_info1 = G.nodes[item[0]]
                node_info2 = G.nodes[item[1]]
                color_legend_mapper[node_info1['name']] = node_info2['name']
    return color_legend_mapper


def construct_VI_mapper(G):
    valid_paths = find_specific_structure(G, ['VI', 'DVV', 'VEPV'])
    insight_tick_mapper = {}
    insight_legend_mapper = {}
    for item in valid_paths:
        if G.has_node(item[0]) and G.has_node(item[1]):
            node_info1 = G.nodes[item[0]]
            node_info2 = G.nodes[item[1]]
            if item[1].startswith('Tick'):
                if node_info1['name'] in insight_tick_mapper.keys():
                    if item[0] in insight_tick_mapper[node_info1['name']].keys():
                        insight_tick_mapper[node_info1['name']][item[0]].append(node_info2['name'])
                    else:
                        insight_tick_mapper[node_info1['name']][item[0]] = [node_info2['name']]
                else:
                    insight_tick_mapper[node_info1['name']] = {}
                    if item[0] in insight_tick_mapper[node_info1['name']].keys():
                        insight_tick_mapper[node_info1['name']][item[0]].append(node_info2['name'])
                    else:
                        insight_tick_mapper[node_info1['name']][item[0]] = [node_info2['name']]
            if item[1].startswith('Legend'):
                if node_info1['name'] in insight_legend_mapper.keys():
                    if node_info1['name'] in insight_tick_mapper.keys():
                        if item[0] in insight_tick_mapper[node_info1['name']].keys():
                            insight_tick_mapper[node_info1['name']][item[0]].append(node_info2['name'])
                        else:
                            insight_tick_mapper[node_info1['name']][item[0]] = [node_info2['name']]
                    else:
                        insight_tick_mapper[node_info1['name']] = {}
                        if item[0] in insight_tick_mapper[node_info1['name']].keys():
                            insight_tick_mapper[node_info1['name']][item[0]].append(node_info2['name'])
                        else:
                            insight_tick_mapper[node_info1['name']][item[0]] = [node_info2['name']]
                else:
                    if node_info1['name'] in insight_legend_mapper.keys():
                        if item[0] in insight_legend_mapper[node_info1['name']].keys():
                            insight_legend_mapper[node_info1['name']][item[0]].append(node_info2['name'])
                        else:
                            insight_legend_mapper[node_info1['name']][item[0]] = [node_info2['name']]
                    else:
                        insight_legend_mapper[node_info1['name']] = {}
                        if item[0] in insight_legend_mapper[node_info1['name']].keys():
                            insight_legend_mapper[node_info1['name']][item[0]].append(node_info2['name'])
                        else:
                            insight_legend_mapper[node_info1['name']][item[0]] = [node_info2['name']]

    return insight_tick_mapper, insight_legend_mapper


def find_specific_structure(graph, target_types):
    node_types = nx.get_node_attributes(graph, 'type')
    valid_paths = []
    for source in graph.nodes():
        for target in graph.nodes():
            if source == target:
                continue
            for path in nx.all_simple_paths(graph, source=source, target=target, cutoff=len(target_types) - 1):
                if len(path) == len(target_types):
                    types_in_path = [node_types[node] for node in path]
                    if types_in_path == target_types:
                        valid_paths.append(path)
    return valid_paths

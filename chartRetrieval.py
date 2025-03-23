import pandas as pd
from nltk.tokenize import word_tokenize
import time
from config import *


def run_chart_retrieval(d):
    gq = GraphQuery(f"{CHART_RETRIEVAL_DATA_PATH}/", cType=d["type"], entity=d["entity"], encode=d["encode"], insight=d["insight"])
    result = gq.query()
    return result

class GraphQuery:
    def __init__(self, data_path, cType=None, entity=None, encode=None, insight=None):
        # 初始化 四种检索条件
        if cType is None:
            cType = []
        TYPE = ["bar", "line", "pie", "scatter"]
        self.type = [t for t in cType if t in TYPE]
        self.entity = entity
        self.encode = encode
        self.insight = insight
        self.data_path = data_path
        # 读入检索库
        # self.nodes = pd.read_csv(data_path + 'node.csv').iterrows()  # [(index: int, node: object)]
        # self.edges = pd.read_csv(data_path + 'edge.csv').iterrows()  # [(index: int, edge: object)]
        # 检索结果
        self.node_result = []
        self.encode_result = []
        self.insight_result = []
        self.result = []
        return

    def keyword_query(self):
        start = time.time()
        nodes = pd.read_csv(self.data_path + 'queryDatabase.csv').iterrows()
        node_result = {}
        result = []
        for n in nodes:
            chartId = n[1]["type"] + " " + str(n[1]["id"])
            if len(self.entity):
                filteredNodeName = word_tokenize(n[1]['nodeName'].lower())
                overlap = [e for e in filteredNodeName if e in self.entity]
                if len(overlap) > 0 and chartId not in node_result.keys():
                    node_result[chartId] = overlap
                elif len(overlap) > 0 and chartId in node_result.keys():
                    node_result[chartId] = list(set(node_result[chartId]).union(set(overlap)))
        self.node_result = [k for k in node_result.keys() if len(node_result[k]) == len(self.entity)]
        end = time.time()
        return self.node_result, end - start

    def node_query(self):
        nodes = pd.read_csv(self.data_path + 'node.csv').iterrows()  # [(index: int, node: object)]
        start = time.time()
        node_result = {}
        for n in nodes:
            chartId = n[1]["type"] + " " + str(n[1]["id"])
            if len(self.entity):
                if n[1]["type"] in self.type:
                    filteredNodeName = word_tokenize(str(n[1]['nodeName']).lower())
                    overlap = [e for e in filteredNodeName if e in self.entity]
                    if len(overlap) > 0 and chartId not in node_result.keys():
                        node_result[chartId] = overlap
                    elif len(overlap) > 0 and chartId in node_result.keys():
                        node_result[chartId] = list(set(node_result[chartId]).union(set(overlap)))
                self.node_result = [k for k in node_result.keys() if len(node_result[k]) == len(self.entity)]
            else:
                if n[1]["type"] in self.type and chartId not in self.node_result:
                    self.node_result.append(chartId)
        end = time.time()
        print("node query 花费时间：", end - start)
        return self.node_result

    def encode_query(self):
        if len(self.encode) <= 0:
            self.encode_result = self.node_result
            return self.node_result
        nodes = pd.read_csv(self.data_path + 'node.csv').iterrows()  # [(index: int, node: object)]
        start = time.time()
        X_KEYWORDS = ["x_axis", "bar_position", "point_position_x"]
        Y_KEYWORDS = ["y_axis", "bar_height", "point_position_y"]
        kw = None
        if self.encode[0] in X_KEYWORDS:
            kw = "x_title"
        elif self.encode[0] in Y_KEYWORDS:
            kw = "y_title"
        for n in nodes:
            if kw in n[1]["nodeId"].lower():
                chartId = n[1]["type"] + " " + str(n[1]["id"])
                filteredNodeName = word_tokenize(n[1]['nodeName'].lower())
                overlap = [e for e in filteredNodeName if e in self.encode[1]]
                if len(overlap) > 0 and chartId not in self.encode_result:
                    self.encode_result.append(chartId)
        end = time.time()
        print("encode query 花费时间：", end - start)
        return self.encode_result

    def insight_query(self):
        if len(self.insight) <= 0:
            self.insight_result = self.encode_result
            return self.encode_result
        nodes = pd.read_csv(self.data_path + 'queryDatabase.csv').iterrows()  # [(index: int, node: object)]
        start = time.time()
        result = {}
        for n in nodes:
            ni = n[1]["nodeId"]
            if ("Position" in ni or "Color" in ni or "Bar" in ni or "Point" in ni or "Pie" in ni or "Height" in ni or
                    "Position-Y" in ni or "Position-X" in ni or "chart" in ni):
                continue
            chartId = n[1]["type"] + " " + str(n[1]["id"])
            for kw in self.insight:
                if kw.lower() in str(n[1]["nodeName"]).lower():
                    if chartId not in result.keys():
                        result[chartId] = [kw]
                    else:
                        result[chartId].append(kw)
                        result[chartId] = list(set(result[chartId]))
        self.insight_result = [k for k in result.keys() if len(result[k]) == len(self.insight)]
        end = time.time()
        print("insight query 花费时间：", end - start)
        return self.insight_result

    def edge_query(self):
        pass

    def total_query(self):
        start = time.time()
        nodes = pd.read_csv(self.data_path + 'node.csv').iterrows()
        node_result = {}
        insight_result = {}
        nd = []
        ec = []
        it = []
        X_KEYWORDS = ["x_axis", "bar_position", "point_position_x"]
        Y_KEYWORDS = ["y_axis", "bar_height", "point_position_y"]
        kw = None
        if self.encode[0] in X_KEYWORDS:
            kw = "x_title"
        elif self.encode[0] in Y_KEYWORDS:
            kw = "y_title"
        for n in nodes:
            if n[1]["type"] in self.type:
                chartId = n[1]["type"] + " " + str(n[1]["id"])
                filteredNodeName = word_tokenize(n[1]['nodeName'].lower())
                overlap = [e for e in filteredNodeName if e in self.entity]
                if len(overlap) > 0 and chartId not in node_result.keys():
                    node_result[chartId] = overlap
                elif len(overlap) > 0 and chartId in node_result.keys():
                    node_result[chartId] = list(set(node_result[chartId]).union(set(overlap)))
                if kw in n[1]["nodeId"].lower():
                    filteredNodeName = word_tokenize(n[1]['nodeName'].lower())
                    overlap = [e for e in filteredNodeName if e in self.encode[1]]
                    if len(overlap) > 0 and chartId not in self.encode_result:
                        ec.append(chartId)
                for kwi in self.insight:
                    if kwi.lower() in n[1]["nodeName"].lower():
                        if chartId not in insight_result.keys():
                            insight_result[chartId] = [kwi]
                        else:
                            insight_result[chartId].append(kwi)
                            insight_result[chartId] = list(set(insight_result[chartId]))

        nd = [k for k in node_result.keys() if len(node_result[k]) == len(self.entity)]
        it = [k for k in insight_result.keys() if len(insight_result[k]) == len(self.insight)]
        end = time.time()
        print("query 花费时间：", end - start)
        print(len(nd), len(ec), len(it))
        return [e for e in nd if e in ec and e in it], end - start

    def query(self):
        # 进行query
        if len(self.insight) == 0:
            self.node_query()
            return self.node_result
        elif len(self.entity) == 0:
            self.insight_query()
            return self.insight_result
        else:
            self.node_query()
            self.insight_query()
            self.result = [e for e in self.node_result if e in self.insight_result]
            return self.result

    def encode_query_current(self):
        nodes = pd.read_csv(self.data_path + 'queryDatabase.csv').iterrows()  # [(index: int, node: object)]
        start = time.time()
        X_KEYWORDS = ["x_axis", "bar_position", "point_position_x"]
        Y_KEYWORDS = ["y_axis", "bar_height", "point_position_y"]
        kw = None
        if self.encode[0] in X_KEYWORDS:
            kw = "x_title"
        elif self.encode[0] in Y_KEYWORDS:
            kw = "y_title"
        node_result = {}
        for n in nodes:
            if n[1]["type"] not in self.type:
                continue
            chartId = n[1]["type"] + " " + str(n[1]["id"])
            filteredNodeName = word_tokenize(n[1]['nodeName'].lower())
            overlap = [e for e in filteredNodeName if e in self.entity]
            if len(overlap) > 0 and chartId not in node_result.keys():
                node_result[chartId] = overlap
            elif len(overlap) > 0 and chartId in node_result.keys():
                node_result[chartId] = list(set(node_result[chartId]).union(set(overlap)))
            if kw in n[1]["nodeId"].lower():
                filteredNodeName = word_tokenize(n[1]['nodeName'].lower())
                overlap = [e for e in filteredNodeName if e in self.encode[1]]
                if len(overlap) > 0 and chartId not in self.encode_result:
                    self.encode_result.append(chartId)
        result = [k for k in node_result.keys() if len(node_result[k]) == len(self.entity) and k in self.encode_result]
        end = time.time()
        print("encode query 花费时间：", end - start)
        return result, end - start


    def insight_query_current(self):
        nodes = pd.read_csv(self.data_path + 'queryDatabase.csv').iterrows()  # [(index: int, node: object)]
        start = time.time()
        insight_result = {}
        node_result = {}
        for n in nodes:
            chartId = n[1]["type"] + " " + str(n[1]["id"])
            for kw in self.insight:
                if kw.lower() in str(n[1]["nodeName"]).lower():
                    if chartId not in insight_result.keys():
                        insight_result[chartId] = [kw]
                    else:
                        insight_result[chartId].append(kw)
                        insight_result[chartId] = list(set(insight_result[chartId]))

            filteredNodeName = word_tokenize(str(n[1]['nodeName']).lower())
            overlap = [e for e in filteredNodeName if e in self.entity]
            if len(overlap) > 0 and chartId not in node_result.keys():
                node_result[chartId] = overlap
            elif len(overlap) > 0 and chartId in node_result.keys():
                node_result[chartId] = list(set(node_result[chartId]).union(set(overlap)))
        result1 = [k for k in node_result.keys() if len(node_result[k]) == len(self.entity)]
        result2 = [k for k in insight_result.keys() if len(insight_result[k]) == len(self.insight)]
        result = [r for r in result1 if r in result2]
        end = time.time()
        return result, end - start

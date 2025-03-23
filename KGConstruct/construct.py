import traceback
import os
import json
from collections import Counter

from KGConstruct.insights import get_insight


def bar_construct(ann, df):
    # print(ann)
    # print(df)
    print("============= bar =============")
    bar = ann['bar']
    bar.sort(key=lambda x: x['position-x'])
    x_axis = ann['x_axis']
    y_axis = ann['y_axis']
    legend = ann['legend']
    graph = {'nodes': [], 'edges': []}

    # 创建基础节点和基础边并加入图
    title = {'id': 'title', 'name': ann['title'], 'type': 'VEPV'}
    chartType = {'id': "chart", 'name': "Bar chart", 'type': 'VEPV'}
    tc = {'source': 'chart', 'target': 'title', 'type': 'Chart title'}
    graph['nodes'].append(title)
    graph['nodes'].append(chartType)
    graph['edges'].append(tc)

    x_title = {'id': 'x_title', 'name': x_axis['title'], 'type': 'DV'}
    graph['nodes'].append(x_title)
    # 添加x轴ticks，Tick的序号是组号（组号按照图像中从左到右排序）
    for tk in x_axis['ticks']:
        t = {'id': 'Tick' + str(tk['groupIdx']), 'name': tk['label'], 'type': 'DVV'}
        p = {'id': 'Position' + str(tk['groupIdx']), 'name': tk['groupIdx'], 'type': 'VEPV'}
        graph['nodes'].append(t)
        graph['nodes'].append(p)
        txt = {'source': 'Tick' + str(tk['groupIdx']), 'target': 'x_title', 'type': 'Values of'}
        pt = {'source': 'Position' + str(tk['groupIdx']), 'target': 'Tick' + str(tk['groupIdx']), 'type': 'Encode'}
        graph['edges'].append(txt)
        graph['edges'].append(pt)

    y_title = {'id': 'y_title', 'name': y_axis['title'], 'type': 'DV'}
    graph['nodes'].append(y_title)

    # 有图例的图
    if len(legend) > 0:
        # 添加图例结点，序号按照数组顺序，连接图例颜色和图例label
        for i in range(len(legend)):
            l = {'id': 'Legend' + str(i), 'name': legend[i]['label'], 'type': 'DVV'}
            c = {'id': 'Color' + str(i), 'name': legend[i]['color'], 'type': 'VEPV'}
            graph['nodes'].append(l)
            graph['nodes'].append(c)
            cl = {'source': 'Color' + str(i), 'target': 'Legend' + str(i), 'type': 'Encode'}
            graph['edges'].append(cl)
        # 添加柱结点，序号按照数组顺序
        for i in range(len(bar)):
            b = {'id': 'Bar' + str(i), 'name': 'Bar', 'type': 'VE'}
            h = {'id': 'Height' + str(i), 'name': bar[i]['height'], 'type': 'VEPV'}
            graph['nodes'].append(b)
            graph['nodes'].append(h)
            # 连接柱和高度 连接高度和y_title
            bh = {'source': 'Bar' + str(i), 'target': 'Height' + str(i), 'type': 'Height ix'}
            graph['edges'].append(bh)
            hyt = {'source': 'Height' + str(i), 'target': 'y_title', 'type': 'Encode'}
            graph['edges'].append(hyt)
            # 检索颜色，连接柱和图例颜色
            for j in range(len(legend)):
                if legend[j]['color'] == bar[i]['color']:
                    bc = {'source': 'Bar' + str(i), 'target': 'Color' + str(j), 'type': 'Color is'}
                    graph['edges'].append(bc)
                    break
            # 检索位置，连接柱子和x轴tick
            for tk in x_axis['ticks']:
                if tk['groupIdx'] == bar[i]['group']:
                    bp = {'source': 'Bar' + str(i), 'target': 'Position' + str(tk['groupIdx']), 'type': 'Position index is'}
                    graph['edges'].append(bp)
                    break
        # 添加insight types
        n = 0
        os1_list = df["OutstandingFirst"]
        os2_list = df["OutstandingTwo"]
        for os1 in os1_list:
            o = {"id": "Insight" + str(n), "name": "OutstandingNo1", "type": "VI"}
            graph["nodes"].append(o)
            n += 1
            ot = {"source": o["id"], "target": "title", "type": "insight"}
            graph["edges"].append(ot)
        for os2 in os2_list:
            o = {"id": "Insight" + str(n), "name": "OutstandingNo2", "type": "VI"}
            graph["nodes"].append(o)
            n += 1
            ot = {"source": o["id"], "target": "title", "type": "insight"}
            graph["edges"].append(ot)
        # for i in range(len(bar)):
        #     for os1 in os1_list:
        #         if os1["element"]["color"] == bar[i]["color"] and os1["element"]["group"] == bar[i]["group"]:
        #             for j in range(len(bar)):
        #                 if os1["element"]["color"] == bar[j]["color"] and not i == j:
        #                     bbi = {'source': 'Bar' + str(i), 'target': 'Bar' + str(j), 'type': 'Insight OutstandingNo1'}
        #                     graph['edges'].append(bbi)
        #             break
        #     for os2 in os2_list:
        #         if os2["element"][0]["color"] == bar[i]["color"] and os2["element"][0]["group"] == bar[i]["group"]:
        #             for j in range(len(bar)):
        #                 if os2["element"][0]["color"] == bar[j]["color"] and not i == j and not os2["element"][1]["group"] == bar[j]["group"]:
        #                     bbi = {'source': 'Bar' + str(i), 'target': 'Bar' + str(j), 'type': 'Insight OutstandingNo2'}
        #                     graph['edges'].append(bbi)
        #         if os2["element"][1]["color"] == bar[i]["color"] and os2["element"][1]["group"] == bar[i]["group"]:
        #             for j in range(len(bar)):
        #                 if os2["element"][1]["color"] == bar[j]["color"] and not i == j and not os2["element"][0]["group"] == bar[j]["group"]:
        #                     bbi = {'source': 'Bar' + str(i), 'target': 'Bar' + str(j), 'type': 'Insight OutstandingNo2'}
        #                     graph['edges'].append(bbi)
        en_list = df["Evenness"]
        for en in en_list:
            e = {"id": "Insight" + str(n), "name": "Evenness", "type": "VI"}
            graph["nodes"].append(e)
            n += 1
            et = {"source": e["id"], "target": "title", "type": "insight"}
            graph["edges"].append(et)
        # for en in en_list:
        #     bar_o = None
        #     bar_c = None
        #     for i in range(len(bar)):
        #         if bar[i]["color"] == en["color"]:
        #             if bar_o is None:
        #                 bar_o = "Bar" + str(i)
        #                 bar_c = "Bar" + str(i)
        #             else:
        #                 bbi = {'source': 'Bar' + str(i), 'target': bar_c, 'type': 'Insight Evenness'}
        #                 graph['edges'].append(bbi)
        #                 bar_c = 'Bar' + str(i)
        #     bbi = {'source': bar_c, 'target': bar_o, 'type': 'Insight Evenness'}
        #     graph['edges'].append(bbi)

    # 无图例的图
    else:
        for i in range(len(bar)):
            b = {'id': 'Bar' + str(i), 'name': 'Bar', 'type': 'VE'}
            h = {'id': 'Height' + str(i), 'name': bar[i]['height'], 'type': 'VEPV'}
            graph['nodes'].append(b)
            graph['nodes'].append(h)
            bh = {'source': 'Bar' + str(i), 'target': 'Height' + str(i), 'type': 'Height is'}
            graph['edges'].append(bh)
            hyt = {'source': 'Height' + str(i), 'target': 'y_title', 'type': 'Encode'}
            graph['edges'].append(hyt)
            for tk in x_axis['ticks']:  # 检索位置
                if tk['groupIdx'] == bar[i]['group']:
                    bp = {'source': 'Bar' + str(i), 'target': 'Position' + str(tk['groupIdx']), 'type': 'Position index is'}
                    graph['edges'].append(bp)
                    break
        # 添加insight types
        n = 0
        os1 = None if len(df["OutstandingFirst"]) <= 0 else df["OutstandingFirst"][0]
        os2 = None if len(df["OutstandingTwo"]) <= 0 else df["OutstandingTwo"][0]
        if os1 is not None:
            o = {"id": "Insight" + str(n), "name": "OutstandingNo1", "type": "VI"}
            graph["nodes"].append(o)
            n += 1
            ot = {"source": o["id"], "target": "title", "type": "insight"}
            graph["edges"].append(ot)

        if os2 is not None:
            o = {"id": "Insight" + str(n), "name": "OutstandingNo2", "type": "VI"}
            graph["nodes"].append(o)
            n += 1
            ot = {"source": o["id"], "target": "title", "type": "insight"}
            graph["edges"].append(ot)
        # for i in range(len(bar)):
        #     if os1 is not None and os1["element"]["group"] == bar[i]["group"]:
        #         for j in range(len(bar)):
        #             if not i == j:
        #                 bbi = {'source': 'Bar' + str(i), 'target': 'Bar' + str(j), 'type': 'Insight OutstandingNo1'}
        #                 graph['edges'].append(bbi)
        #         break
        #     if os2 is not None and os2["element"][0]["group"] == bar[i]["group"]:
        #         for j in range(len(bar)):
        #             if not i == j and not os2["element"][1]["group"] == bar[j]["group"]:
        #                 bbi = {'source': 'Bar' + str(i), 'target': 'Bar' + str(j), 'type': 'Insight OutstandingNo2'}
        #                 graph['edges'].append(bbi)
        #     if os2 is not None and os2["element"][1]["group"] == bar[i]["group"]:
        #         for j in range(len(bar)):
        #             if not i == j and not os2["element"][0]["group"] == bar[j]["group"]:
        #                 bbi = {'source': 'Bar' + str(i), 'target': 'Bar' + str(j), 'type': 'Insight OutstandingNo2'}
        #                 graph['edges'].append(bbi)

        en = None if len(df["Evenness"]) <= 0 else df["Evenness"][0]
        if en is not None:
            e = {"id": "Insight" + str(n), "name": "OutstandingNo1", "type": "VI"}
            graph["nodes"].append(e)
            n += 1
            et = {"source": e["id"], "target": "title", "type": "insight"}
            graph["edges"].append(et)
        # if en is not None:
        #     for i in range(1, len(bar)):
        #         bbi = {'source': 'Bar' + str(i), 'target': 'Bar' + str(i-1), 'type': 'Insight Evenness'}
        #         graph['edges'].append(bbi)
        #     bbi = {'source': "Bar0", 'target': 'Bar' + str(len(bar) - 1), 'type': 'Insight Evenness'}
        #     graph['edges'].append(bbi)
    # print(graph)
    return graph


def line_construct(ann, df):
    # print(ann)
    # print(df)
    print("============= line =============")
    points = ann['points']
    points.sort(key=lambda x: x['position']['x'])
    x_axis = ann['x_axis']
    y_axis = ann['y_axis']
    legend = ann['legend']
    graph = {'nodes': [], 'edges': []}

    title = {'id': 'title', 'name': ann['title'], 'type': 'VEPV'}
    chartType = {'id': "chart", 'name': "Line chart", 'type': 'VEPV'}
    tc = {'source': 'chart', 'target': 'title', 'type': 'Chart title'}
    graph['edges'].append(tc)
    graph['nodes'].append(title)
    graph['nodes'].append(chartType)

    x_title = {'id': 'x_title', 'name': x_axis['title'], 'type': 'DV'}
    graph['nodes'].append(x_title)
    for tk in x_axis['ticks']:
        t = {'id': 'Tick' + str(tk['groupIdx']), 'name': tk['label'], 'type': 'DVV'}
        p = {'id': 'Position' + str(tk['groupIdx']), 'name': tk['groupIdx'], 'type': 'VEPV'}
        graph['nodes'].append(t)
        graph['nodes'].append(p)
        txt = {'source': 'Tick' + str(tk['groupIdx']), 'target': 'x_title', 'type': 'Values of'}
        pt = {'source': 'Position' + str(tk['groupIdx']), 'target': 'Tick' + str(tk['groupIdx']), 'type': 'Encode'}
        graph['edges'].append(txt)
        graph['edges'].append(pt)

    y_title = {'id': 'y_title', 'name': y_axis['title'], 'type': 'DV'}
    graph['nodes'].append(y_title)

    if len(legend) >= 0:
        for i in range(len(legend)):
            l = {'id': 'Legend' + str(i), 'name': legend[i]['label'], 'type': 'DVV'}
            c = {'id': 'Color' + str(i), 'name': legend[i]['color'], 'type': 'VEPV'}
            graph['nodes'].append(l)
            graph['nodes'].append(c)
            cl = {'source': 'Color' + str(i), 'target': 'Legend' + str(i), 'type': 'Encode'}
            graph['edges'].append(cl)
        for i in range(len(points)):
            b = {'id': 'Point' + str(i), 'name': 'Point', 'type': 'VE'}
            h = {'id': 'Position-Y' + str(i), 'name': points[i]['position']['y'], 'type': 'VEPV'}
            graph['nodes'].append(b)
            graph['nodes'].append(h)
            bh = {'source': 'Point' + str(i), 'target': 'Position-Y' + str(i), 'type': 'Position-Y is'}
            graph['edges'].append(bh)
            hyt = {'source': 'Position-Y' + str(i), 'target': 'y_title', 'type': 'Encode'}
            graph['edges'].append(hyt)
            for j in range(len(legend)):    # 检索颜色
                if legend[j]['color'] == points[i]['color']:
                    bc = {'source': 'Point' + str(i), 'target': 'Color' + str(j), 'type': 'Color is'}
                    graph['edges'].append(bc)
                    break
            for tk in x_axis['ticks']:  # 检索位置
                if tk['groupIdx'] == points[i]['group']:
                    bp = {'source': 'Point' + str(i), 'target': 'Position' + str(tk['groupIdx']), 'type': 'Position index is'}
                    graph['edges'].append(bp)
                    break
        # 添加insights
        n = 0
        cp_list = df["ChangePoint"]
        for cp in cp_list:
            c = {"id": "Insight" + str(n), "name": "ChangePoint", "type": "VI"}
            graph["nodes"].append(c)
            n += 1
            ct = {"source": c["id"], "target": "title", "type": "VI"}
            graph["edges"].append(ct)

        td_list = df["Trend"]
        for td in td_list:
            t = {"id": "Insight" + str(n), "name": "Trend " + td["trend"], "type": "VI"}
            graph["nodes"].append(t)
            n += 1
            tt = {"source": t["id"], "target": "title", "type": "VI"}
            graph["edges"].append(tt)
        # for td in td_list:
        #     pt_c = None
        #     for i in range(len(points)):
        #         if pt_c is None:
        #             pt_c = "Point" + str(i)
        #         else:
        #             if points[i]["color"] == td["color"]:
        #                 ppi = {'source': pt_c, 'target': "Point" + str(i), 'type': "Insight trend " + td["trend"]}
        #                 graph['edges'].append(ppi)
        #                 pt_c = "Point" + str(i)

        ol_list = df["Outlier"]
        for ol in ol_list:
            o = {"id": "Insight" + str(n), "name": "Outlier", "type": "VI"}
            graph["nodes"].append(o)
            n += 1
            ot = {"source": o["id"], "target": "title", "type": "VI"}
            graph["edges"].append(ot)
        # for ol in ol_list:
        #     eles = ol["element"]
        #     for ele in eles:
        #         ln = None
        #         rn = None
        #         for i in range(len(points)):
        #             if ele["color"] == points[i]["color"] and points[i]["group"] == ele["group"] - 1:
        #                 ln = "Point" + str(i)
        #             if ele["color"] == points[i]["color"] and points[i]["group"] == ele["group"] + 1:
        #                 rn = "Point" + str(i)
        #         if ln is not None and rn is not None:
        #             ppi = {'source': ln, 'target': rn, 'type': "Insight outlier"}
        #             graph['edges'].append(ppi)

        cl_list = df["Correlation"]
        for cl in cl_list:
            c = {"id": "Insight" + str(n), "name": "Correlation", "type": "VI"}
            graph["nodes"].append(c)
            n += 1
            ct = {"source": c["id"], "target": "title", "type": "insight"}
            graph["edges"].append(ct)
        # for cl in cl_list:
        #     v1 = None
        #     v2 = None
        #     for i in range(len(legend)):
        #         if cl["correlationValues"][0] == legend[i]['color']:
        #             v1 = "Legend" + str(i)
        #         if cl["correlationValues"][1] == legend[i]['color']:
        #             v2 = "Legend" + str(i)
        #     if v1 is not None and v2 is not None:
        #         ppi = {'source': v1, 'target': v2, 'type': "Insight correlation " + cl["correlation"]}
        #         graph['edges'].append(ppi)

    # 无图例
    else:
        for i in range(len(points)):
            b = {'id': 'Point' + str(i), 'name': 'Point', 'type': 'VE'}
            h = {'id': 'Position-Y' + str(i), 'name': points[i]['position']['y'], 'type': 'VEPV'}
            graph['nodes'].append(b)
            graph['nodes'].append(h)
            bh = {'source': 'Point' + str(i), 'target': 'Position-Y' + str(i), 'type': 'Position-Y ix'}
            graph['edges'].append(bh)
            hyt = {'source': 'Position-Y' + str(i), 'target': 'y_title', 'type': 'Encode'}
            graph['edges'].append(hyt)
            for tk in x_axis['ticks']:  # 检索位置
                if tk['groupIdx'] == points[i]['group']:
                    bp = {'source': 'Point' + str(i), 'target': 'Position' + str(tk['groupIdx']), 'type': 'Position index is'}
                    graph['edges'].append(bp)
                    break
        # 添加insights
        n = 0

        cp = None if len(df["ChangePoint"]) <= 0 else df["ChangePoint"][0]
        if cp is not None:
            c = {"id": "Insight" + str(n), "name": "ChangePoint", "type": "VI"}
            graph["nodes"].append(c)
            n += 1
            ct = {"source": c["id"], "target": "title", "type": "VI"}
            graph["edges"].append(ct)

        td = None if len(df["Trend"]) <= 0 else df["Trend"][0]
        if td is not None:
            c = {"id": "Insight" + str(n), "name": "Trend " + td["trend"], "type": "VI"}
            graph["nodes"].append(c)
            n += 1
            ct = {"source": c["id"], "target": "title", "type": "VI"}
            graph["edges"].append(ct)
        # pt_c = None
        # for i in range(len(points)):
        #     if pt_c is None:
        #         pt_c = "Point" + str(i)
        #     else:
        #         ppi = {'source': pt_c, 'target': "Point" + str(i), 'type': "Insight trend " + td["trend"]}
        #         graph['edges'].append(ppi)

        ol = None if len(df["Outlier"]) <= 0 else df["Outlier"][0]
        if ol is not None:
            o = {"id": "Insight" + str(n), "name": "Outlier", "type": "VI"}
            graph["nodes"].append(o)
            n += 1
            ot = {"source": o["id"], "target": "title", "type": "VI"}
            graph["edges"].append(ot)
        # eles = ol["element"]
        # for ele in eles:
        #     ln = None
        #     rn = None
        #     for i in range(len(points)):
        #         if points[i]["group"] == ele["group"] - 1:
        #             ln = "Point" + str(i)
        #         if points[i]["group"] == ele["group"] + 1:
        #             rn = "Point" + str(i)
        #     if ln is not None and rn is not None:
        #         ppi = {'source': ln, 'target': rn, 'type': "Insight outlier"}
        #         graph['edges'].append(ppi)
    return graph


def pie_construct(ann, df):
    # print(ann)
    # print(df)
    print("============= pie =============")
    pies = ann['pie']
    graph = {'nodes': [], 'edges': []}
    title = {'id': 'title', 'name': ann['title'], 'type': 'DV'}
    chartType = {'id': "chart", 'name': "Pie chart", 'type': 'VEPV'}
    tc = {'source': 'chart', 'target': 'title', 'type': 'Chart title'}
    graph['edges'].append(tc)
    graph['nodes'].append(title)
    graph['nodes'].append(chartType)
    for p in range(len(pies)):
        ps = {'id': 'Pie' + str(p), 'name': 'Pie slice', 'type': 'VE'}
        a = {'id': 'Angle' + str(p), 'name': round(pies[p]['rate'] * 360, 2), 'type': 'VEPV'}
        c = {'id': 'Color' + str(p), 'name': pies[p]['color'], 'type': 'VEPV'}
        plb = pies[p]['label'] if "label" in pies[p].keys() and not pies[p]['label'] == "" else "None"
        l = {'id': 'Label' + str(p), 'name': plb, 'type': 'DVV'}
        graph['nodes'].append(ps)
        graph['nodes'].append(a)
        graph['nodes'].append(c)
        graph['nodes'].append(l)
        at = {'source': 'Angle' + str(p), 'target': 'title', 'type': 'Encode'}
        psa = {'source': 'Pie' + str(p), 'target': 'Angle' + str(p), 'type': 'Angle is'}
        psc = {'source': 'Pie' + str(p), 'target': 'Color' + str(p), 'type': 'Color is'}
        cl = {'source': 'Color' + str(p), 'target': 'Label' + str(p), 'type': 'Encode'}
        graph['edges'].append(at)
        graph['edges'].append(psa)
        graph['edges'].append(psc)
        graph['edges'].append(cl)
    # 添加insights
    atr_list = df["Attribution"]
    for atr in atr_list:
        a = {"id": "Insight0", "name": "Attribution", "type": "VI"}
        graph["nodes"].append(a)
        at = {"source": a["id"], "target": "title", "type": "insight"}
        graph["edges"].append(at)
    # for atr in atr_list:
    #     for p in range(len(pies)):
    #         if atr["element"]["color"] == pies[p]["color"]:
    #             for p_ in range(len(pies)):
    #                 if not p == p_:
    #                     ppi = {'source': "Pie" + str(p), 'target': "Pie" + str(p_), 'type': "Insight Attribution"}
    #                     graph['edges'].append(ppi)
    #         break
    return graph


def scatter_construct(ann, df):
    # print(ann)
    # print(df)
    print("============= scatter =============")
    scatter = ann['scatter']
    x_axis = ann['x_axis']
    y_axis = ann['y_axis']
    legend = ann['legend']

    graph = {'nodes': [], 'edges': []}

    title = {'id': 'title', 'name': ann['title'], 'type': 'DV'}
    chartType = {'id': "chart", 'name': "Scatter chart", 'type': 'VEPV'}
    tc = {'source': 'chart', 'target': 'title', 'type': 'Chart title'}
    graph['edges'].append(tc)
    graph['nodes'].append(title)
    graph['nodes'].append(chartType)

    x_title = {'id': 'x_title', 'name': x_axis['title'], 'type': 'DV'}
    graph['nodes'].append(x_title)
    y_title = {'id': 'y_title', 'name': y_axis['title'], 'type': 'DV'}
    graph['nodes'].append(y_title)

    # if len(legend) > 0:
    #     for i in range(len(legend)):
    #         l = {'id': 'Legend' + str(i), 'name': legend[i]['label'], 'type': 'DVV'}
    #         c = {'id': 'Color' + str(i), 'name': legend[i]['color'], 'type': 'VEPV'}
    #         graph['nodes'].append(l)
    #         graph['nodes'].append(c)
    #         cl = {'source': 'Color' + str(i), 'target': 'Legend' + str(i), 'type': 'Encode'}
    #         graph['edges'].append(cl)
    #     for i in range(len(scatter)):
    #         p = {'id': 'Point' + str(i), 'name': 'Point', 'type': 'VE'}
    #         x = {'id': 'Position-X' + str(i), 'name': scatter[i]['position']['x'], 'type': 'VEPV'}
    #         y = {'id': 'Position-Y' + str(i), 'name': scatter[i]['position']['y'], 'type': 'VEPV'}
    #         graph['nodes'].append(p)
    #         graph['nodes'].append(x)
    #         graph['nodes'].append(y)
    #         px = {'source': 'Point' + str(i), 'target': 'Position-X' + str(i), 'type': 'Position-X'}
    #         py = {'source': 'Point' + str(i), 'target': 'Position-Y' + str(i), 'type': 'Position-Y'}
    #         graph['edges'].append(px)
    #         graph['edges'].append(py)
    #         pxxt = {'source': 'Position-X' + str(i), 'target': 'x_title', 'type': 'Encode'}
    #         pyyt = {'source': 'Position-Y' + str(i), 'target': 'y_title', 'type': 'Encode'}
    #         graph['edges'].append(pxxt)
    #         graph['edges'].append(pyyt)
    #         for j in range(len(legend)):
    #             if legend[j]['color'] == scatter[i]['color']:
    #                 pc = {'source': 'Point' + str(i), 'target': 'Color' + str(j), 'type': 'Color is'}
    #                 graph['edges'].append(pc)
    #                 break
    # else:
    for i in range(len(scatter)):
        p = {'id': 'Point' + str(i), 'name': 'Point', 'type': 'VE'}
        x = {'id': 'Position-X' + str(i), 'name': scatter[i]['position']['x'], 'type': 'VEPV'}
        y = {'id': 'Position-Y' + str(i), 'name': scatter[i]['position']['y'], 'type': 'VEPV'}
        graph['nodes'].append(p)
        graph['nodes'].append(x)
        graph['nodes'].append(y)
        px = {'source': 'Point' + str(i), 'target': 'Position-X' + str(i), 'type': 'Position-X'}
        py = {'source': 'Point' + str(i), 'target': 'Position-Y' + str(i), 'type': 'Position-Y'}
        graph['edges'].append(px)
        graph['edges'].append(py)
        pxxt = {'source': 'Position-X' + str(i), 'target': 'x_title', 'type': 'Encode'}
        pyyt = {'source': 'Position-Y' + str(i), 'target': 'y_title', 'type': 'Encode'}
        graph['edges'].append(pxxt)
        graph['edges'].append(pyyt)
    n = 0
    group = df["2DClustering&Outlier"]["label"]
    c = {"id": "Insight" + str(n), "name": "2DClustering", "type": "VI"}
    graph["nodes"].append(c)
    n += 1
    ct = {"source": c["id"], "target": "title", "type": "Insight"}
    graph["edges"].append(ct)

    g = Counter(group)
    if "-1" in g.keys():
        for i in range(len(list(g["-1"]))):
            o = {"id": "Insight" + str(n), "name": "Outlier", "type": "VI"}
            graph["nodes"].append(o)
            n += 1
            ot = {"source": o["id"], "target": "title", "type": "insight"}
            graph["edges"].append(ot)
    # print(group)
    # for i in group.keys():
    #     if not i == "-1":
    #         for j in group[i]:
    #             for k in group[i]:
    #                 if j < k:
    #                     ppi = {'source': 'Point' + str(j), 'target': 'Point' + str(k), 'type': 'Insight 2DClustering'}
    #                     graph["edges"].append(ppi)
    return graph

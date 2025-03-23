import random
from typing import List, Tuple
from scipy.stats import pearsonr, ttest_rel, linregress
from scipy.stats import norm, ks_2samp
from scipy.cluster.vq import kmeans, whiten
from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pylab as plt


VectorStr = List[str]
VectorNum = List[float]
VectorObj = List[object]

RATE = 0.95
TYPES = {
    "bar": ["OutstandingFirst", "OutstandingTwo", "Evenness"],
    "line": ["ChangePoint", "Outlier", "Seasonality", "Trend", "Correlation", "CrossMeasureCorrelation"],
    "pie": ["Attribution"],
    "scatter": ["2DClustering", "Outlier", "Fitting", "Correlation", "CrossMeasureCorrelation"],
}


def data_shift(ann: object, tp: str) -> List:
    hasLgd = True if "legend" in ann.keys() and len(ann["legend"]) > 0 else False
    if tp == "bar":
        if hasLgd:
            return [e for e in ann["bar"]]
        else:
            return [e for e in ann["bar"]]
    if tp == "line":
        if hasLgd:
            return [e for e in ann["points"]]
        else:
            return [e for e in ann["points"]]
    if tp == "pie":
        return [e for e in ann["pie"]]
    if tp == "scatter":
        return [e for e in ann["scatter"]]


def gua(data, avg, sig):
    sqrt_2pi = np.power(2 * np.pi, 0.5)
    coef = 1 / (sqrt_2pi * sig)
    powercoef = -1 / (2 * np.power(sig, 2))
    mypow = powercoef * (np.power((data - avg), 2))
    return coef * (np.exp(mypow))


def sigma(data):
    n = len(data)
    sumy = 0
    sumySqr = 0
    for _ in data:
        sumy += _ ** 2
        sumySqr += _
    part1 = 1 / n ** 0.5
    part2 = sumy / (2 * n)
    part3 = (sumySqr / (2 * n)) ** 2
    part4 = (part2 - part3) ** 0.5
    return part1 * part4


# def func_residuals(x: VectorNum, alpha: float, beta: float) -> VectorNum:
#     return alpha * (x ** -beta)


def cal_CrossMeasureCorrelation_Line(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for (i, e) in enumerate(lgd):
        for j in range(i + 1, len(lgd)):
            singleRet = {}
            x = np.array([ele["position"]['y'] for ele in df if ele["color"] == e])
            y = np.array([ele["position"]['y'] for ele in df if ele["color"] == list(lgd)[j]])
            if x.shape[0] == y.shape[0]:
                whitened = whiten(np.array([x, y]))
                x = whitened[0, :]
                y = whitened[1, :]
                pccs, p_value = pearsonr(x, y)
                if np.std(whitened[0, :]) == 0 or np.std(whitened[1, :]) == 0:
                    score = 0
                else:
                    score = 1 - p_value
                if score > RATE:
                    singleRet["score"] = score
                    singleRet["correlation"] = "positive" if pccs > 0 else "negative"
                    singleRet["crossMeasureCorrelationValues"] = [e, list(lgd)[j]]
                    ret.append(singleRet)
    return ret


def cal_Correlation_Line(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for (i, e) in enumerate(lgd):
        for j in range(i + 1, len(lgd)):
            singleRet = {}
            x = np.array([ele["position"]['y'] for ele in df if ele["color"] == e])
            y = np.array([ele["position"]['y'] for ele in df if ele["color"] == list(lgd)[j]])
            if x.shape[0] == y.shape[0]:
                pccs, p_value = pearsonr(x, y)
                if np.std(x) == 0 or np.std(y) == 0:
                    score = 0
                else:
                    score = 1 - p_value
                if score > RATE:
                    singleRet["score"] = score
                    singleRet["correlation"] = "positive" if pccs > 0 else "negative"
                    singleRet["correlationValues"] = [e, list(lgd)[j]]
                    ret.append(singleRet)
    return ret


def cal_Attribution(df: list) -> List[object]:
    ret = []
    current_data = df
    current_data.sort(reverse=True, key=lambda e: e["rate"])
    data = np.array([e["rate"] for e in current_data])
    first_persent = data[0] / np.sum(data)
    if not first_persent == np.nan:
        score = max(first_persent - 0.5, 0) / 0.1
        score = min(score, 1)
        if score > RATE:
            ret.append({"score": score, "element": current_data[0]})
    else:
        score = 0
    return ret


def cal_OutstandingNo1(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for i in lgd:
        current_data = [e for e in df if e["color"] == i]
        current_data.sort(reverse=True, key=lambda e: e["height"])
        sorted_list = np.array([e["height"] for e in current_data])
        ydata = np.where(sorted_list > 0, sorted_list, 0)
        singleRet = {}
        score = 0 if ydata.shape[0] <= 2 else min(np.abs(ydata[0] / ydata[1] - 1), 1)
        if score > RATE:
            singleRet["score"] = score
            singleRet["element"] = current_data[0]
            ret.append(singleRet)
    return ret


def cal_OutstandingNo2(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for i in lgd:
        current_data = [e for e in df if e["color"] == i]
        current_data.sort(reverse=True, key=lambda e: e["height"])
        sorted_list = np.array([e["height"] for e in current_data])
        ydata = np.where(sorted_list > 0, sorted_list, 0)
        singleRet = {}
        score = 0 if ydata.shape[0] <= 2 else min(np.abs(ydata[1] / ydata[2] - 1), 1)
        if score > RATE:
            singleRet["score"] = score
            singleRet["element"] = [current_data[0], current_data[1]]
            ret.append(singleRet)
    return ret


def cal_Evenness(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for i in lgd:
        current_data = [e for e in df if e["color"] == i]
        ydata = np.array([e["height"] for e in current_data])
        std = np.std(ydata)
        singleRet = {}
        alpha = abs(np.mean(ydata)) / (std + abs(np.mean(ydata)))
        score = 1 if std == 0 else max(alpha - 0.85, 0) / 0.15
        if score > RATE:
            singleRet["score"] = score
            singleRet["color"] = i
            ret.append(singleRet)
    return ret


def cal_ChangePoint(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for i in lgd:
        current_data = [e for e in df if e["color"] == i]
        current_data.sort(reverse=False, key=lambda e: e["group"])
        ydata = [e["position"]['y'] for e in current_data]
        s = sigma(ydata)
        ydata = np.array(ydata)
        for j in range(1, len(ydata) - 1):
            leftMean = np.mean(ydata[0:j])
            rightMean = np.mean(ydata[j:])
            k = math.fabs(leftMean - rightMean) / s
            p = gua(k, 0, 1)
            score = 1 - p
            singleRet = {}
            if score > RATE:
                singleRet["element"] = current_data[j]
                singleRet["score"] = score
                ret.append(singleRet)
    return ret


def cal_Outlier_Line(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for i in lgd:
        current_data = [e for e in df if e["color"] == i]
        ydata = [e["position"]['y'] for e in current_data]
        singleRet = {}
        p_list = norm.cdf(ydata, np.mean(ydata), np.std(ydata) ** 2)
        score = -p_list + 1
        if score.shape[0] > 3:
            singleRet["element"] = [current_data[e] for e in np.argwhere(score > RATE).flatten()]
            singleRet["score"] = score[np.argwhere(score > RATE).flatten()].tolist()
            if len(singleRet["score"]) > 0:
                ret.append(singleRet)
        else:
            singleRet["element"] = []
            singleRet["score"] = []
    return ret


def cal_Seasonality(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for i in lgd:
        current_data = [e for e in df if e["color"] == i]
        ydata = [e["position"]['y'] for e in current_data]
        xdata = [e["group"] + 1 for e in current_data]
        time = pd.to_datetime(xdata, format='%m')
        winter = np.array([ydata[i] for i in range(len(time)) if time[i].month in {12, 1, 2}])
        spring = np.array([ydata[i] for i in range(len(time)) if time[i].month in {3, 4, 5}])
        summer = np.array([ydata[i] for i in range(len(time)) if time[i].month in {6, 7, 8}])
        autumn = np.array([ydata[i] for i in range(len(time)) if time[i].month in {9, 10, 11}])
        para = {}
        if len(winter) != 0 or len(spring) != 0 or len(summer) != 0 or len(summer) != 0:
            season = np.array([i for i in winter - np.mean(winter)] + [i for i in spring - np.mean(spring)] + [i for i in summer - np.mean(summer)] + [i for i in autumn - np.mean(autumn)])
            ttest, pval = ttest_rel(season, ydata - np.mean(ydata))
            score = 1 - pval
            score = np.where(np.isnan(score), 0, score)
            print(score)
        else:
            score = 0
    return ret


def cal_Trend(df: list) -> List[object]:
    lgd = set([e["color"] for e in df])
    ret = []
    for i in lgd:
        current_data = [e for e in df if e["color"] == i]
        current_data.sort(reverse=False, key=lambda e: e["group"])
        ydata = [e["position"]['y'] for e in current_data]
        slope, intercept, r, p, se = linregress(range(len(ydata)), ydata)
        timeseries_avg = ydata - np.array(range(len(ydata))) * slope + intercept
        std = np.std(timeseries_avg)
        alpha = abs(np.mean(timeseries_avg)) / (std + abs(np.mean(timeseries_avg)))
        score = 0 if std == 0 else max(alpha - 0.85, 0) / 0.15
        singleRet = {}
        if math.fabs(slope) > 5 and not slope == 0:
            singleRet["score"] = score
            singleRet["color"] = i
            singleRet["trend"] = "increase" if slope < 0 else "decrease"
            ret.append(singleRet)
    return ret


def cal_Fitting_Scatter(df: List) -> List[object]:
    ret = {}
    return ret

def cal_2DClustering_Outlier(df: list) -> List[object]:
    ret = []
    xdata = np.array([e["position"]["x"] for e in df]).reshape([-1, 1])
    ydata = np.array([e["position"]["y"] for e in df]).reshape([-1, 1])
    transfer = MinMaxScaler((0, 1))
    xdata_std = transfer.fit_transform(xdata)
    ydata_std = transfer.fit_transform(ydata)
    d = np.concatenate((xdata_std, ydata_std), axis=1)
    if np.std(d[:, 0]) == 0 or np.std(d[:, 1]) == 0:
        score = 0
        ret = {}
    else:
        clustering = DBSCAN(eps=0.2, min_samples=3).fit(d)
        label = clustering.labels_
        label_list = set(label)
        group = {}
        for l in label_list:
            group[str(l)] = np.where(label == l)[0].tolist()
        ret = {"label": group}
    return ret


def get_insight(ann: object, tp: str) -> object:
    d = data_shift(ann, tp)
    if tp == "bar":
        return {
            "OutstandingFirst": cal_OutstandingNo1(d),
            "OutstandingTwo": cal_OutstandingNo2(d),
            "Evenness": cal_Evenness(d)
        }
    elif tp == "line":
        return {
            "ChangePoint": cal_ChangePoint(d),
            "Outlier": cal_Outlier_Line(d),
            # "Seasonality": [],
            "Trend": cal_Trend(d),
            "Correlation": cal_Correlation_Line(d),
            "CrossMeasureCorrelation": cal_CrossMeasureCorrelation_Line(d)
        }
    elif tp == "pie":
        return {
            "Attribution": cal_Attribution(d)
        }
    elif tp == "scatter":
        return {
            "2DClustering&Outlier": cal_2DClustering_Outlier(d)
        }
    else:
        print("未知图像类型")

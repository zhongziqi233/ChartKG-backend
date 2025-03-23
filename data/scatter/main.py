import json

import numpy as np
import random
import matplotlib.pyplot as plt
import cv2
import matplotlib
matplotlib.use("Agg")
cname = ['#8B0000','#228B22','#FF1493','#B22222','#ADFF2F','#FFA756','#0000CD','#9370DB','#0CFF0C','#808000','#3CB371']


def draw(imgname, img_path):
    imgInfo = {}
    fig = plt.figure(figsize=(12,6.5),facecolor='pink')
    ax = plt.axes([0,0,1,1])
    ax.set(xlim=[0, 1], ylim=[0, 1], facecolor='w')
    c = random.randint(1,9)
    c1 = cname[c]
    c2 = cname[c+1]
    c3 = cname[c-1]

    # 5s
    s_x = []
    s_num = 15
    for i in range(s_num):
        s_x.append(random.uniform(0.2, 0.5))
    s_y = []
    for i in range(s_num):
        s_y.append(random.uniform(0.3, 0.5))
    ss_x = []
    ss_num = 10
    for i in range(ss_num):
        ss_x.append(random.uniform(0.5, 0.7))
    ss_y = []
    for i in range(ss_num):
        ss_y.append(random.uniform(0.4, 0.7))
    sss_x = []
    sss_num = 10
    for i in range(sss_num):
        sss_x.append(random.uniform(0.5, 0.7))
    sss_y = []
    for i in range(sss_num):
        sss_y.append(random.uniform(0.2, 0.5))


    title_x = random.randint(60, 600)
    legend_y = random.randint(180,680)

    #0title
    title = 'title title title title abcdef'
    ax.text(title_x/1000, 0.9, title,  fontsize=14, color = "black", style = "italic", weight = "light", verticalalignment='bottom', horizontalalignment='left', rotation=0)
    #1xtitle
    x_title = 'x_axis_title'
    ax.text(0.505, 0.055, x_title,  fontsize=14, color = "black", style = "italic", weight = "light",  rotation=0)
    #2xlabel
    ax.text(0.305, 0.08, '5',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.505, 0.08, '10',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.705, 0.08, '15',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.905, 0.08, '20',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    #3ytitle
    y_title = 'y_axis_title'
    ax.text(0.037, 0.455, y_title,  fontsize=14, color = "black", style = "italic", weight = "light", verticalalignment='bottom', horizontalalignment='center', rotation=90)
    #4ylabel
    ax.text(0.075, 0.1, '1',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.075, 0.2, '2',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.075, 0.3, '3',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.075, 0.4, '4',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.075, 0.5, '5',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.075, 0.6, '6',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.075, 0.7, '7',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    ax.text(0.075, 0.8, '8',  fontsize=12, color = "b", style = "italic", weight = "light",  rotation=0)
    #5s
    plt.plot(s_x, s_y, 'o', markersize=10, color=c1)
    plt.plot(ss_x, ss_y, 'o', markersize=10, color=c2)
    plt.plot(sss_x, sss_y, 'o', markersize=10, color=c3)
    # 6legend
    legend_labels = ['label-1', 'label-2', 'label-3']
    plt.plot(0.8, legend_y/1000+0.04, 'o', markersize=10, color=c1)
    plt.plot(0.8, legend_y/1000+0.1, 'o', markersize=10, color=c2)
    plt.plot(0.8, legend_y/1000+0.16, 'o', markersize=10, color=c3)
    ax.text(0.82, legend_y/1000+0.03, legend_labels[2], fontsize=14, color="black", style="italic", weight="light", rotation=0)
    ax.text(0.82, legend_y/1000+0.09, legend_labels[1], fontsize=14, color="black", style="italic", weight="light", rotation=0)
    ax.text(0.82, legend_y/1000+0.15, legend_labels[0], fontsize=14, color="black", style="italic", weight= "light", rotation=0)
    ax.add_patch(plt.Rectangle((0.77, legend_y/1000), 0.2, 0.2, color="black", fill=False, linewidth=1))
    #xy
    plt.arrow(0.1, 0.1, 0.87, 0)
    plt.arrow(0.1, 0.1, 0, 0.78)

    # plt.show()
    fig.savefig(img_path + '/' + imgname, dpi=100)

    imgg_path = img_path + '/' + str(imgname) + ".png"
    imgInfo['title'] = title
    imgInfo['x_axis'] = {'title': x_title}
    imgInfo['y_axis'] = {'title': y_title}
    imgInfo['legend'] = [
        {'label': legend_labels[0], 'color': c1},
        {'label': legend_labels[1], 'color': c2},
        {'label': legend_labels[2], 'color': c3},
    ]
    imgInfo['scatter'] = []
    for i in range(s_num):
        imgInfo['scatter'].append({
            'position': {'x': int((s_x[i] - 0.01) * 1000), 'y': int((s_y[i] - 0.01) * 1000)},
            'color': c1,
        })
    for i in range(ss_num):
        imgInfo['scatter'].append({
            'position': {'x': int((ss_x[i] - 0.01) * 1000), 'y': int((ss_y[i] - 0.01) * 1000)},
            'color': c2,
        })
    for i in range(sss_num):
        imgInfo['scatter'].append({
            'position': {'x': int((sss_x[i] - 0.01) * 1000), 'y': int((sss_y[i] - 0.01) * 1000)},
            'color': c3,
        })

    return imgInfo


if __name__ == '__main__':
    sav_path = './labels'
    img_path = './images'
    img_information = []
    for i in range(5000):
        img_info = draw(str(i), img_path)
        # img_information.append(img_info)
        with open(sav_path + '/' + str(i) + '.json', 'w') as f:
            f.write(json.dumps(img_info, indent=4))





















import matplotlib.pyplot as plt
import random
import string
import json
import numpy as np
import copy
import cv2
import os
'''
0: title
1: legend
2: pie
'''



def random_title(length_of_string=0):
    if length_of_string == 0:
        length_of_string = random.randint(5, 10)
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string))


def random_data():
    random_number = random.randint(3, 6)
    random_data = {}
    for i in range(random_number):
        random_name_number = random.randint(3, 6)
        random_name = random_title(length_of_string=random_name_number)
        data = random.randint(10, 100)
        random_data[random_name] = data
    return random_data


def random_color(number):
    colors = ['r', 'c', 'g', 'y', 'm', 'b']
    return random.sample(colors, number)


def random_legend_loc():
    state = random.randint(0, 1)
    if state == 0:
        loc = ['best', 'upper right', 'upper left', 'lower left', 'lower right']
    else:
        loc = ['lower center']
    return state, random.sample(loc, 1)[0]


def randomPie(file_name):
    election_data = random_data()
    candidate = [key for key in election_data]
    votes = [value for value in election_data.values()]
    plt.figure(figsize=(12, 6.5), dpi=100)
    plt.pie(votes, labels=candidate, autopct="%1.2f%%", colors=random_color(len(candidate)),
            textprops={'fontsize': 24}, labeldistance=1.05)
    (legend_state, legend_loc) = random_legend_loc()
    if legend_state == 0:
        legend = plt.legend(fontsize=16, loc=legend_loc)
    else:
        legend = plt.legend(fontsize=16, loc=legend_loc, ncol=len(candidate))
    title = plt.title(random_title(), fontsize=36)
    plt.gcf().canvas.draw()
    plt.savefig(save_path + file_name + '.png')
    legend_bbox = legend.get_window_extent()
    title_bbox = title.get_window_extent()
    center = [600, 600]
    r = 370
    plt.close()

    return {'pie': {'bbox': {'x0': center[0]-r, 'y0': center[1] - r - 20, 'x1': center[0] + r + 20, 'y1': center[1] + r + 10}},
            'title': {'bbox': {'x0': title_bbox.x0, 'y0': title_bbox.y0,
                               'x1': title_bbox.x1,
                               'y1': title_bbox.y1}},
            'legend': {'bbox': {'x0': legend_bbox.x0, 'y0': legend_bbox.y0,
                                'x1': legend_bbox.x1,
                                'y1': legend_bbox.y1}},
            'image_index': file_name
            }






def convert_labels(path_img, test_bbox):
    img = cv2.imread(path_img)
    size = img.shape
    test_bbox['y0'] = size[0] - test_bbox['y0']
    test_bbox['y1'] = size[0] - test_bbox['y1']

    # print(test_bbox)
    x1 = test_bbox['x0']
    y1 = test_bbox['y0']
    x2 = test_bbox['x1']
    y2 = test_bbox['y1']

    def sorting(l1, l2):
        if l1 > l2:
            lmax, lmin = l1, l2
            return lmax, lmin
        else:
            lmax, lmin = l2, l1
            return lmax, lmin


    # print(size)
    xmax, xmin = sorting(x1, x2)
    ymax, ymin = sorting(y1, y2)
    dw = 1. / size[1]
    dh = 1. / size[0]
    x = (xmin + xmax) / 2.0
    y = (ymin + ymax) / 2.0
    w = xmax - xmin
    h = ymax - ymin
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def get_title(p, image_path):
    try:
        ann = convert_labels(image_path, copy.copy(p["title"]["bbox"]))
        return [0, ann[0], ann[1], ann[2], ann[3]]
    except:
        return None

def get_legend(p, image_path):
    try:
        ann = convert_labels(image_path, copy.copy(p["legend"]["bbox"]))
        return [1, ann[0], ann[1], ann[2], ann[3]]
    except:
        return None

def get_pie(p, image_path):
    try:
        ann = convert_labels(image_path, copy.copy(p["pie"]["bbox"]))
        return [2, ann[0], ann[1], ann[2], ann[3]]
    except:
        return None

if __name__ == '__main__':
    count = 5000
    annotation = []
    type = 'val'
    save_path = f'./images/'

    for i in range(count):
        print('generate:', i)
        txt = randomPie(str(i))
        annotation.append(txt)
    with open(f'./{type}_annotation.json', 'w') as f:
        json.dump(annotation, f)

    annotations_path = f'./{type}_annotation.json'
    img_path = f'./images/'
    sav_path = f'./labels/'
    list_images = os.listdir(img_path)
    int_list_images = []

    for i in list_images:
        int_list_images.append(int(i.replace('.png', '')))


    with open(annotations_path, 'r', encoding='utf8') as fs:
        f = json.load(fs)
        count = 5000
        for i in int_list_images:
            print('extract:', count)
            p = f[i]
            path = img_path + '/' + str(p['image_index']) + '.png'
            title = get_title(p, path)
            legend = get_legend(p, path)
            pie = get_pie(p, path)
            # y_axis_label = get_y_axis_label(p, path)
            annotations_array = []
            if title:
                annotations_array += [title]
            if legend:
                annotations_array += [legend]
            if pie:
                annotations_array += [pie]
            name = (sav_path + '/' + str(p['image_index']) + '.txt')
            np.savetxt(name, np.array(annotations_array), delimiter=" ", fmt='%1.9f')
            count += 1

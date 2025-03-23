import cv2
import os

import numpy as np
import torch
from tensorflow.keras.applications.resnet50 import preprocess_input
from keras_preprocessing.image import ImageDataGenerator

from models.common import DetectMultiBackend
from utils.general import check_img_size, non_max_suppression, scale_boxes, xyxy2xywh
from utils.torch_utils import select_device
from KGConstruct.construct import *

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf

from config import *

def chart_classify(path, filename):
    size = CHART_CLASSIFY_RESIZE_SIZE
    img = cv2.imread(path)
    img = cv2.resize(img, size)
    imgFile = path.replace(filename, f"classifyTemp/resize{filename}")
    cv2.imwrite(imgFile, img)

    model = tf.keras.models.load_model("classifyModel")

    datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
    testgen = datagen.flow_from_directory('./static/images/temp', shuffle=False, class_mode='categorical')
    prediction = model.predict(testgen, verbose=1)
    os.remove(imgFile)
    for (index, d) in enumerate(prediction[0]):
        if d == 1:
            return CHART_CLASSES[index]
    return 'none'

def chart_yolo(chart_type, chart_path, dnn=False, half=False, conf_thres=0.25, iou_thres=0.45, classes=None):
    # 使用yolo识别图片信息
    data = f"{MODEL_PATH}/train_{chart_type}.yaml"
    model_path = f"{MODEL_PATH}/{chart_type}/weights/best.pt"
    device = select_device('0')
    model = DetectMultiBackend(model_path, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(CHART_YOLO_SIZE, s=stride)
    img = cv2.imread(chart_path)
    img0 = img.copy()
    img = cv2.resize(img, imgsz)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.transpose(2, 0, 1)
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device)
    img = img.float() / 255.0
    if len(img.shape) == 3:
        img = img[None]

    pred = model(img)

    pred = non_max_suppression(pred, conf_thres, iou_thres, classes=classes)

    # 处理检测结果
    det = pred[0]  # 单张图片结果
    txt_path = chart_path.replace(".png", ".txt")

    if len(det):
        det[:, :4] = scale_boxes(img.shape[2:], det[:, :4], img0.shape).round()
        gn = torch.tensor(img0.shape)[[1, 0, 1, 0]]  # 归一化系数
        for *xyxy, conf, cls in reversed(det):
            xywh = xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn
            line = (cls.item(), *xywh.view(-1).tolist())
            with open(f'{txt_path}', 'a') as f:
                f.write(('%g ' * len(line)).rstrip() % line + '\n')


def construct_charKG(chart_type, chart_path):
    # 通过yolo识别图像信息后构建图谱
    chart_yolo(chart_type, chart_path)
    construct(chart_type, chart_path)
    update_general_dataset()
    pass

def construct(chart_type, chart_path):
    types_ = ['bar', 'line', 'pie', 'scatter']
    if chart_type in types_ :
        for chartType in types_:
            annPath = '../data/' + chartType + '/labels'
            graphPath = '../data/' + chartType + '/graphs'
            listAnns = os.listdir(annPath)
            for p in listAnns:
                with open(annPath + '/' + p) as f:
                    ann = json.load(f)
                    dataFeature = get_insight(ann, chartType)
                    if chartType == 'bar':
                        res = bar_construct(ann, dataFeature)
                    elif chartType == 'line':
                        res = line_construct(ann, dataFeature)
                    elif chartType == 'pie':
                        res = pie_construct(ann, dataFeature)
                    elif chartType == 'scatter':
                        res = scatter_construct(ann, dataFeature)
                    with open(graphPath + '/' + p, 'w') as r:
                        r.write(json.dumps(res, indent=4))
                        r.write('\n')
        return True
    else:
        return False


def update_general_dataset():
    # 更新总库和总库地址（包括QA和query的总库）
    pass

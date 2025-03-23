import json
from shutil import copyfile

from flask import Flask, request, send_file
import os

from chartProcess import construct_charKG, chart_classify
from chartRetrieval import run_chart_retrieval
from chartQA import run_chart_QA

from config import *

app = Flask(__name__)


@app.route("/chart_upload", methods=["POST"])
# 图片上传并且进行处理
def chart_upload():
    file = request.files.getlist('fileToUpload')[0]
    # 保存图片
    temp_save_path = f"{IMAGE_PATH}/temp/{file.filename}"
    file.save(temp_save_path)
    # 处理图片
    chart_type = chart_classify(temp_save_path, file.filename)
    save_path = f"{IMAGE_PATH}/{chart_type}/{file.filename}"
    print(save_path, chart_type, sep=' | ')
    copyfile(temp_save_path, save_path)
    os.remove(temp_save_path)
    res = construct_charKG(chart_type, save_path)
    print(res)
    return {'code': 200}


@app.route("/chart_retrieval", methods=["POST"])
# 图表问答
def chart_retrieval():
    data = json.loads(request.data.decode('utf-8').strip())
    retrieval_result = run_chart_retrieval(data)
    print(retrieval_result)
    return {'code': 200, 'data': retrieval_result}


@app.route("/chart_QA", methods=["POST"])
# 图表问答
def chart_QA():
    data = json.loads(request.data.decode('utf-8').strip())
    result = run_chart_QA(data['qs'], data['chart'], data['type'])
    print(result)
    return {'code': 200, 'data': result}


@app.route("/get_chart_KG/<string:chartType>/<int:chartId>", methods=["GET"])
def get_chart_KG(chartType, chartId):
    return send_file(f"{CHART_RETRIEVAL_DATA_PATH}/{chartType}/graphs_current/{chartId}.json", mimetype='application/json')


@app.route("/get_chart_image/<string:chartType>/<int:chartName>", methods=["GET"])
def get_chart_image(chartType, chartName):
    return send_file(f"{CHART_RETRIEVAL_DATA_PATH}/{chartType}/images/{chartName}.png", mimetype='image/png')


if __name__ == "__main__":
    app.run(debug=True, port=3000)

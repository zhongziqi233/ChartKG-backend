from flask import Flask

from chartProcess import construct_charKG
from chartRetrieval import run_chart_retrieval
from chartQA import run_chart_QA

app = Flask(__name__)


@app.route("/chart_upload", methods=["POST"])
# 图片上传并且进行处理，使用soket返回处理进度
def chart_upload():
    construct_charKG()
    return {'code': 503}


@app.route("/chart_retrieval", methods=["POST"])
# 图表问答
def chart_retrieval():
    run_chart_retrieval()
    return {'code': 503}


@app.route("/chart_QA", methods=["POST"])
# 图表问答
def chart_QA():
    run_chart_QA()
    return {'code': 503}


@app.route("/get_chart_image/<int:chartId>", methods=["GET"])
def get_chart_image(chartId):
    # 通过id获取图表图像
    return {'code': 503}


@app.route("/get_chart_KG/<int:chartId>", methods=["GET"])
def get_chart_KG(chartId):
    # 通过id获取图表知识图谱
    return {'code': 503}


if __name__ == "__main__":
    app.run(port=3000)

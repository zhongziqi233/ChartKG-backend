import os
import json
import pandas as pd


types = ['bar', 'line', 'pie', 'scatter']

items = []

need = ['title', 'x_title', 'y_title', 'Tick', 'Legend']

for type_ in types:
    for _,_,files in os.walk(f'./{type_}/graphs_current'):
        for file in files:
            with open(f'./{type_}/graphs_current/{file}','r',encoding='utf-8') as f:
                data = json.load(f)
                for node in data['nodes']:
                    for n in need:
                        if n in str(node['id']):
                            item = {'id': file.replace('.json',''), 'nodeId': node['id'], 'nodeName': node['name'], 'type': type_}
                            items.append(item)
                            break

df = pd.DataFrame(items)
df.to_csv("./node.csv", index=False)

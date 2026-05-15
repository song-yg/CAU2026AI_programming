import json
import os
def load_json(path,default_data):
    if not os.path.exists(path):
        return default_data
    try:
        with open(path,'r',encoding='utf-8') as file:
            return json.load(file)
    except:print(path,'파일을 불러오지 못했습니다.')
    return default_data
def save_json(path,data):
    folder = os.path.dirname(path)

    if folder != '' and not os.path.exists(folder):
        os.makedirs(folder)

    with open(path,'w',encoding='utf-8') as file:
        json.dump(data,file,indent=2,ensure_ascii=False)

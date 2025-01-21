import json
import re
def correct_json_content(data):
    # if isinstance(data, list):
    #     # 将列表中的元素拼接成一个完整的字符串
    #     return ''.join(data)
    return str(data)
def extract_ids(corrected_data):
    # 使用正则表达式提取ID
    ids = re.findall(r'\d{4}\.\d{5}', corrected_data)
    return ids
with open("./Paper_metadata_download/2025-01-20.json", 'r', encoding='utf-8') as file:
    data = json.load(file)
    for i in data:
        print(i['paper']['id'])



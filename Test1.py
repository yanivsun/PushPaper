import os
import json
from datetime import datetime, timedelta,timezone
import requests
import random
import unittest
import re
from tqdm import tqdm
from openai import AzureOpenAI
from bs4 import BeautifulSoup
import glob

file_path = "./Paper_metadata_download/2025-01-20.json"
results = []
OPENAI_API_KEY = "4f1442ffe47143018f91f0e956f61a15"
AZURE_OPENAI_ENDPOINT = "https://gtkchatgpt.openai.azure.com"
OPENAI_API_VERSION = "2024-02-15-preview"
deployment_name = "GPT4o"
# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
# os.environ["OPENAI_API_VERSION"] = OPENAI_API_VERSION
client = AzureOpenAI(
    api_version=OPENAI_API_VERSION,
    api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)
#TODO: change 2 get_config
def get_proxies():
    # return {
    #     'http': '127.0.0.1:443',
    #     'https': '127.0.0.1:443',
    # }
    return None


def get_name(_url_):
    print('正在获取文献名！')
    print(_url_)
    proxies = get_proxies()

    res = requests.get(_url_, proxies=proxies)
    bs = BeautifulSoup(res.text, 'html.parser')
    other_details = {}

    #TODO: Maybe changed
    try:
        year = bs.find_all(class_='dateline')[0].text
        year = re.search(r'(\d{4})', year, re.M | re.I).group(1)
        other_details['year'] = year
        abstract = bs.find_all(class_='abstract mathjax')[0].text
        other_details['abstract'] = abstract
    except:
        other_details['year'] = ''
        print('年份获取失败')

    # get author
    try:
        authors = bs.find_all(class_='authors')[0].text
        authors = authors.split('Authors:')[1]
        other_details['authors'] = authors
    except:
        other_details['authors'] = ''
        print('authors获取失败')

        # get comment
    try:
        comment = bs.find_all(class_='metatable')[0].text
        real_comment = None
        for item in comment.replace('\n', ' ').split('   '):
            if 'Comments' in item:
                real_comment = item
        if real_comment is not None:
            other_details['comment'] = real_comment
        else:
            other_details['comment'] = ''
    except:
        other_details['comment'] = ''
        print('Comments 获取失败')
    title_str = BeautifulSoup(
        res.text, 'html.parser').find('title').contents[0]
    print('获取成功：', title_str)

    return title_str + '.pdf', other_details


def download_arxiv_(url_pdf):
    if 'arxiv.org' not in url_pdf:
        # formate URL
        if ('.' in url_pdf) and ('/' not in url_pdf):
            new_url = 'https://arxiv.org/abs/' + url_pdf
            print('下载编号：', url_pdf, '自动定位：', new_url)
            return download_arxiv_(new_url)
        else:
            print('不能识别的URL！')
            return None
    if 'abs' in url_pdf:
        url_pdf = url_pdf.replace('abs', 'pdf')
        url_pdf = url_pdf + '.pdf'
    url_abs = url_pdf.replace('.pdf', '').replace('pdf', 'abs')
    title, other_info = get_name(_url_=url_abs)
    paper_id = title.split()[0]  # '[1712.00559]'
    if '2' in other_info['year']:
        title = other_info['year'] + ' ' + title

    known_conf = ['NeurIPS', 'NIPS', 'Nature', 'Science', 'ICLR', 'AAAI']
    for k in known_conf:
        if k in other_info['comment']:
            title = k + ' ' + title

    download_dir = "paper_dir"
    #TODO: Change Dir?
    os.makedirs(download_dir, exist_ok=True)

    title_str = title.replace('?', '？') \
        .replace(':', '：') \
        .replace('\"', '“') \
        .replace('\n', '') \
        .replace('  ', ' ') \
        .replace('  ', ' ')

    requests_pdf_url = url_pdf
    file_path = download_dir + title_str
    print('下载中')
    r = requests.get(requests_pdf_url, proxies=get_proxies())
    with open(file_path, 'wb+') as f:
        f.write(r.content)
    print('下载完成')
    x = "%s  %s %s.bib" % (paper_id, other_info['year'], other_info['authors'])
    x = x.replace('?', '？') \
        .replace(':', '：') \
        .replace('\"', '“') \
        .replace('\n', '') \
        .replace('  ', ' ') \
        .replace('  ', ' ')
    return file_path, other_info

def downandtranslate(file_path,output_file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # corrected_data = correct_json_content(data)
        # print(f"矫正后的文件内容：\n{corrected_data}")
        #
        # # 提取ID并生成URL
        # ids = extract_ids(corrected_data)

        ids = []
        for i in data:
            ids.append(i['paper']['id'])

        # 使用tqdm显示进度条
        for arxiv_id in tqdm(ids, desc=f"Processing {file_path}", unit="id"):
            url = f"https://arxiv.org/abs/{arxiv_id}"
            print(f"Arxiv URL: {url}")

            # 提取摘要，下载PDF文档
            try:
                pdf_path, info = download_arxiv_(url)
            except:
                print("Failed to download arxiv.org pdf")

            i_say = f"请你阅读以下学术论文相关的材料，提取摘要，翻译为中文。材料如下：{str(info)}"

            # 调用OpenAI API处理URL
            result = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "你是一个优秀的文档阅读助手，你需要按照我的要求，对我给你的文档完成相应的操作."
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{i_say}"
                            }
                        ]
                    }
                ],
                stream=False
            )

            # 输出调用结果
            print(result)
            # print(result.choices[0].message.content)

            # 保存结果到列表中
            results.append({
                "url": url,
                "content": result.choices[0].message.content
            })


    # 创建保存文件夹
    output_folder = 'HF-day-paper+GLMs-api'
    os.makedirs(output_folder, exist_ok=True)

    # 保存结果到JSON文件
    output_file_path = os.path.join(output_folder, f"HHHHF_glms_api_clean.json")
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, ensure_ascii=False, indent=4)

    print(f"结果已保存到文件：{output_file_path}")

if __name__ == '__main__':
    downandtranslate(file_path,"HHHHH")
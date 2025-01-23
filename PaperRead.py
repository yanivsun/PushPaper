from utils import get_proxies,get_name,download_arxiv_
import json
from tqdm import tqdm
from openai import AzureOpenAI
import os

file_path = "./Paper_metadata_download/2025-01-20.json"
results = []
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
deployment_name = "GPT4o"

client = AzureOpenAI(
    api_version=OPENAI_API_VERSION,
    api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def downandtranslate(file_path,output_folder):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    ids = []
    for tmp in data:
        ids.append(tmp['paper']['id'])

    for arxiv_id in tqdm(ids, desc=f"Processing {file_path}", unit="id"):
        url = f"https://arxiv.org/abs/{arxiv_id}"
        print(f"Arxiv URL: {url}")
        title = ""
        info = ""
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
        #TODO：代码地址 + star数量
        results.append({
            "名称":info["title"],
            "作者":info["authors"]  if info != "" else "",
            "摘要":result.choices[0].message.content,
            "地址":info["url"]
        })

    # 创建保存文件夹
    os.makedirs(output_folder, exist_ok=True)
    # 保存结果到JSON文件
    out_name = file_path.split("/")[-1]
    output_file_path = os.path.join(output_folder, f"{out_name}")
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, ensure_ascii=False, indent=4)

    print(f"结果已保存到文件：{output_file_path}")
    return output_file_path

def SummaryDay():
    content = ""
    for i,data in enumerate(results):
        content += f"第{i+1}篇文章 标题为：{data['名称']},摘要为：{data['摘要']}。\n"
    i_say = (f"以下是我的文档的一些内容，其中包含了许多论文的内容，请帮我总结以下这些论文有多少篇，分别是什么方向的论文。内容如下：{str(content)}"             )

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
    return result.choices[0].message.content
if __name__ == "__main__":
    downandtranslate(file_path, "./output")
    print(SummaryDay())
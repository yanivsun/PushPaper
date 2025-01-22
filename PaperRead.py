from utils import get_proxies,get_name,download_arxiv_
import json
from tqdm import tqdm
from openai import AzureOpenAI
import os

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

if __name__ == "__main__":
    downandtranslate(file_path, "./output")
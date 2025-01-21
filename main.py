from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import os
import json
from datetime import datetime, timedelta,UTC,timezone
import requests
import random
import unittest
import re
from tqdm import tqdm
from openai import AzureOpenAI

# https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index


nowtime = datetime.now(UTC) + timedelta(hours=8)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)

#得到当前时间 eg : 2025年01月18日星期六
def get_time():
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日") + a

#获取天气
def get_weather(city, key):
    url = f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={city}&language=zh-Hans&unit=c&start=-1&days=5"
    res = requests.get(url).json()
    print(res)
    weather = (res['results'][0])["daily"][0]
    city = (res['results'][0])["location"]["name"]
    return city, weather

# 获取距离指定时间还有多少天
def get_count(born_date):
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days

# 获取距离指定时间还有多少天
def get_birthday(birthday):
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days


def get_words():
    words = requests.get("https://tenapi.cn/v2/yiyan?format=json").json()
    print(words)
    if words['code'] != 200:
        return get_words()
    return words['data']['hitokoto']

def send_wechat():
    '''
        生日的日期格式是：05-20，
        纪念日的格式是 2022-08-09
        '''
    client = WeChatClient(app_id, app_secret)
    wm = WeChatMessage(client)

    f = open("user_info.json", encoding="utf-8")
    js_text = json.load(f)
    f.close()
    data = js_text['data']
    num = 0
    # words = get_words()
    out_time = get_time()

    for user_info in data:
        born_date = user_info['born_date']
        birthday = born_date[5:]
        city = user_info['city']
        user_id = user_info['user_id']
        name = user_info['user_name'].upper()

        # wea_city, weather = get_weather(city, weather_key)
        data = dict()
        # data['time'] = {'value': out_time}
        # data['words'] = {'value': words}#当前城市地点
        # data['weather'] = {'value': weather['text_day']}
        # data['city'] = {'value': wea_city}
        # data['tem_high'] = {'value': weather['high']}
        # data['tem_low'] = {'value': weather['low']}
        # data['born_days'] = {'value': get_count(born_date)}
        # data['birthday_left'] = {'value': get_birthday(birthday)}
        # data['wind'] = {'value': weather['wind_direction']}
        # data['name'] = {'value': name}

        data['time'] = {'value': "out_time"}
        data['words'] = {'value': "words"}  # 当前城市地点
        data['weather'] = {'value': "sdsdsdas"}
        data['city'] = {'value': "sdsdsdas"}
        data['tem_high'] = {'value': "sdsdsdas"}
        data['tem_low'] = {'value': "sdsdsdas"}
        data['born_days'] = {'value': get_count(born_date)}
        data['birthday_left'] = {'value': get_birthday(birthday)}
        data['wind'] = {'value': "sdsdsdas"}
        data['name'] = {'value': name}

        res = wm.send_template(user_id, template_id, data)
        print(res)
        num += 1
    print(f"成功发送{num}条信息")


#读论文
# class TestDailyPapers(unittest.TestCase):
#     def setUp(self):
#         # 获取当前日期和时间 (UTC 时间)
#         self.current_date = datetime.now(timezone.utc)
#         print(f"当前 UTC 日期和时间: {self.current_date}")
#
#         # 将 UTC 时间转换为北京时间 (UTC+8)
#         beijing_timezone = timezone(timedelta(hours=8))
#         self.current_date_beijing = self.current_date.astimezone(beijing_timezone)
#         print(f"当前北京时间和时间: {self.current_date_beijing}")
#
#         # 计算查询的日期(前一天)
#         self.query_date = (self.current_date_beijing - timedelta(days=1)).strftime('%Y-%m-%d')
#         print(f"查询的日期: {self.query_date}")
#
#         # 构建API URL
#         self.url = f"https://huggingface.co/api/daily_papers?date={self.query_date}"
#         print(f"API URL: {self.url}")
#
#     def test_get_daily_papers(self):
#         # 发送GET请求
#         # 设置本地代理
#         proxies = {
#             'http': '127.0.0.1:443',
#             'https': '127.0.0.1:443',
#         }
#         response = requests.get(self.url, proxies=proxies)
#
#         # 定义文件夹和文件名
#         folder_name = 'Paper_metadata_download'
#         file_name = f"{self.query_date}.json"
#
#         # 创建文件夹（如果不存在）
#         os.makedirs(folder_name, exist_ok=True)
#
#         # 完整文件路径
#         file_path = os.path.join(folder_name, file_name)
#
#         try:
#             if response.status_code == 200:
#                 # 检查是否有数据
#                 data = response.json()
#                 if data:
#                     # 如果返回的不是空列表
#                     print(f"在 {self.query_date} 找到数据:")
#                     print(data)
#                     # 写入数据到文件
#                     with open(file_path, 'w', encoding='utf-8') as f:
#                         json.dump(data, f, ensure_ascii=False, indent=4)
#                     print(f"数据已写入文件 {file_path}")
#                 else:
#                     print(f"在 {self.query_date} 没有找到数据")
#                     # 写入1到文件
#                     with open(file_path, 'w', encoding='utf-8') as f:
#                         json.dump(1, f)
#                     print(f"1 已写入文件 {file_path}")
#             else:
#                 print(f"请求失败，状态码：{response.status_code}")
#                 print(response.json())  # 打印出详细的错误信息
#                 # 写入1到文件
#                 with open(file_path, 'w', encoding='utf-8') as f:
#                     json.dump(1, f)
#                 print(f"1 已写入文件 {file_path}")
#         except Exception as e:
#             print(f"写入文件时发生异常: {e}")
#             self.fail(f"写入文件时发生异常: {e}")

# 搜索包含前一天日期的JSON文件
def find_files_with_date(search_path, date_str):
    result = []
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if date_str in file and file.endswith('.json'):
                result.append(os.path.join(root, file))
    return result
# 矫正文件内容
def correct_json_content(data):
    if isinstance(data, list):
        # 将列表中的元素拼接成一个完整的字符串
        return ''.join(data)
    return data

# 提取ID并生成URL
def extract_ids(corrected_data):
    # 使用正则表达式提取ID
    ids = re.findall(r'\d{4}\.\d{5}', corrected_data)
    return ids
def read_paper():

    pass


if __name__ == "__main__":
    app_id = os.getenv("WECHAT_ID")
    app_secret = os.getenv("WECHAT_KEY")
    template_id = os.getenv("WECAHT_TEMPLATE")
    weather_key = os.getenv("WEATHER_API_KEY")


    # unittest.main(exit=False)

    # OPENAI_API_KEY = "4f1442ffe47143018f91f0e956f61a15"
    # AZURE_OPENAI_ENDPOINT = "https://gtkchatgpt.openai.azure.com"
    OPENAI_API_VERSION = "2024-02-15-preview"
    deployment_name = "GPT4o"
    # os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    # os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
    # os.environ["OPENAI_API_VERSION"] = OPENAI_API_VERSION
    client = AzureOpenAI(
        api_version=OPENAI_API_VERSION,
        # api_key=OPENAI_API_KEY,
        # azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    # 获取当前UTC时间
    current_utc_time = datetime.now(timezone.utc)
    print(f"当前 UTC 日期和时间: {current_utc_time}")

    # 将UTC时间转换为北京时间 (UTC+8)
    beijing_timezone = timezone(timedelta(hours=8))
    current_beijing_time = current_utc_time.astimezone(beijing_timezone)
    print(f"当前北京时间和时间: {current_beijing_time}")

    # 计算查询的日期(前一天)
    yesterday_beijing = current_beijing_time - timedelta(days=1)
    yesterday_str = yesterday_beijing.strftime('%Y-%m-%d')
    print(f"查询的日期: {yesterday_str}")
    # 设置搜索路径为当前项目根目录
    search_path = './Paper_metadata_download'

    # 查找包含前一天日期的JSON文件
    json_files = find_files_with_date(search_path, yesterday_str)
    if not json_files:
        print(f"未找到包含前一天日期“{yesterday_str}”的JSON文件。")
    else:
        print(f"找到以下文件：{json_files}")

    # 处理找到的JSON文件并保存结果
    results = []

    for file_path in json_files:
        file_path = file_path.replace("\\","/")
        print(f"找到文件：{file_path}")
        # try:
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

                # 调用OpenAI API处理URL
                result = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"这篇文章的URL是：{url}。这篇文章讲了什么？"
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
        # except Exception as e:
        #     print(f"无法读取文件 {file_path}：{e}")

    # 创建保存文件夹
    output_folder = 'HF-day-paper+GLMs-api'
    os.makedirs(output_folder, exist_ok=True)

    # 保存结果到JSON文件
    output_file = os.path.join(output_folder, f"{yesterday_str}_HF_glms_api_clean.json")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, ensure_ascii=False, indent=4)

    print(f"结果已保存到文件：{output_file}")
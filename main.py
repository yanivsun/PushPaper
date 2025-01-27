import os
from datetime import datetime, timedelta,timezone
from PaperRead import downandtranslate,SummaryDay
import re
from utils import mail

nowtime = datetime.now(timezone.utc) + timedelta(hours=8)
today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")
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

if __name__ == "__main__":

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

    output_file = "./output"
    for file_path in json_files:
        file_path = file_path.replace("\\","/")
        print(f"找到文件：{file_path}")
        out_path = downandtranslate(file_path,output_file)
        if out_path is None:
            break
        data = SummaryDay()
        mail(data,out_path)
    print(f"结果已保存到文件：{output_file}")
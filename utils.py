import re
import os
import json
import requests
from bs4 import BeautifulSoup
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
from datetime import datetime, timedelta,timezone
import random
import zmail
import smtplib

USE_PROXIES = False
NEED_DOWNLOAD = False

# 设置代理（Clash端口号）
def get_proxies():
    return {
        'http': '127.0.0.1:443',
        'https': '127.0.0.1:443',
    } if USE_PROXIES else None

# 获取论文网址中的内容
def get_name(_url_):
    proxies = get_proxies()
    res = requests.get(_url_, proxies=proxies)
    bs = BeautifulSoup(res.text, 'html.parser')
    other_details = {}
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

# 下载文章到指定的位置
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
    other_info["url"] = url_pdf
    other_info["title"] = title
    known_conf = ['NeurIPS', 'NIPS', 'Nature', 'Science', 'ICLR', 'AAAI']
    for k in known_conf:
        if k in other_info['comment']:
            title = k + ' ' + title

    #TODO: Change Dir?
    file_path = ""
    download_dir = "paper_dir"
    if NEED_DOWNLOAD:
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

        if NEED_DOWNLOAD:
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


#得到当前时间 eg : 2025年01月18日星期六
def get_time():
    nowtime = datetime.now(timezone.utc) + timedelta(hours=8)
    dictDate = {'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三', 'Thursday': '星期四',
                'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期天'}
    a = dictDate[nowtime.strftime('%A')]
    return nowtime.strftime("%Y年%m月%d日") + a

# TODO：获取地理位置
def get_words():
    words = requests.get("https://tenapi.cn/v2/yiyan?format=json").json()
    print(words)
    if words['code'] != 200:
        return get_words()
    return words['data']['hitokoto']

def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)
# 获取距离指定时间还有多少天
def get_count(born_date):
    nowtime = datetime.now(timezone.utc) + timedelta(hours=8)
    today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")
    delta = today - datetime.strptime(born_date, "%Y-%m-%d")
    return delta.days

def get_birthday(birthday):
    nowtime = datetime.now(timezone.utc) + timedelta(hours=8)
    today = datetime.strptime(str(nowtime.date()), "%Y-%m-%d")
    nextdate = datetime.strptime(str(today.year) + "-" + birthday, "%Y-%m-%d")
    if nextdate < today:
        nextdate = nextdate.replace(year=nextdate.year + 1)
    return (nextdate - today).days

# 获取天气
def get_weather(city, key):
    url = f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={city}&language=zh-Hans&unit=c&start=-1&days=5"
    res = requests.get(url).json()
    print(res)
    weather = (res['results'][0])["daily"][0]
    city = (res['results'][0])["location"]["name"]
    return city, weather

# 发送消息到wechat
def send_wechat():
    '''
        生日的日期格式是：05-20，
        纪念日的格式是 2022-08-09
    '''
    app_id = os.getenv("WECHAT_ID")
    app_secret = os.getenv("WECHAT_KEY")
    template_id = os.getenv("WECAHT_TEMPLATE")
    weather_key = os.getenv("WEATHER_API_KEY")
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

        wea_city, weather = get_weather(city, weather_key)
        data = dict()
        data['time'] = {'value': out_time}
        data['words'] = {'value': "None"}#当前城市地点
        data['weather'] = {'value': weather['text_day']}
        data['city'] = {'value': wea_city}
        data['tem_high'] = {'value': weather['high']}
        data['tem_low'] = {'value': weather['low']}
        data['born_days'] = {'value': get_count(born_date)}
        data['birthday_left'] = {'value': get_birthday(birthday)}
        data['wind'] = {'value': weather['wind_direction']}
        data['name'] = {'value': name}

        res = wm.send_template(user_id, template_id, data)
        print(res)
        num += 1
    print(f"成功发送{num}条信息")

# 给邮箱发送消息
def mail(str,file_path):
    titil = file_path.split("/")[-1].split(".")[0]
    username = os.getenv('QQ_USER_NAME')
    password = os.getenv('QQ_PASSWORD')
    mail_server = zmail.server(username = username, password = password)

    mail_info = {
        'subject': f'{titil}的论文内容',
        'content_text': str,
        # 'content_html': f'<div>{str}</div>',  # html邮件内容
        'attachments': file_path,
    }
    try:
        mail_server.send_mail(['1109812755@qq.com','yaniv.sun@goertek.com'], mail_info)
    except smtplib.SMTPResponseException as e:
        # 打印异常信息，但继续执行程序
        print(f"SMTPResponseException: {e}")
        pass  # 或者其他处理逻辑

if __name__ == "__main__":
    mail("附件为今天的论文内容。总结为：XXXXX",'./output/2025-01-22.json')
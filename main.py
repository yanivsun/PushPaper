from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage
import os
import json
from datetime import datetime, timedelta,UTC
import requests
import random

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

if __name__ == "__main__":
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
    words = get_words()
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


    '''
    生日的日期格式是：05-20，
    纪念日的格式是 2022-08-09
    '''
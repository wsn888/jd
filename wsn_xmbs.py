#-*- coodeing = utf-8 -*-
#@Time : 2021/8/7 0:20
#@File : 小米新.py
#@Software:
import requests
import random
#=============需要修改的参数==========

phone = ''#小米账号
password = ''#密码
step = int(random.uniform(30000,35000))

#=============需要修改的参数==========

def main_handler(event, context):
    url = 'https://run.nanjin1937.com/API/s_xm.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 QQ/8.8.17.612 V1_IPH_SQ_8.8.17_1_APP_A Pixel/1125 MiniAppEnable SimpleUISwitch/0 StudyMode/0 QQTheme/1102 Core/WKWebView Device/Apple(iPhone X) NetType/4G QBWebViewType/1 WKType/1'

    }
    data = {
        'phone':phone,
        'password':password,
        'step':step
    }
    print(data)
    response = requests.post(url=url,headers=headers,data=data).text
    print(response)

#本地测试，挂云函数不用下面这句
if __name__ == '__main__':

    main_handler(0,0)


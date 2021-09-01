from requests import get, post, put, packages
from re import findall
from os.path import exists
import json

packages.urllib3.disable_warnings()

"""
cron 57 5,17 * * *
"""


def getcookie(key):
    url = 'https://api.m.jd.com/client.action'
    headers = {
        'cookie': key,
        'User-Agent': 'okhttp/3.12.1;jdmall;android;version/10.1.2;build/89743;screen/1440x3007;os/11;network/wifi;',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'charset': 'UTF-8',
        'accept-encoding': 'br,gzip,deflate'
    }
    params = {
        'functionId': 'genToken',
        'client': 'apple',
        'clientVersion': '10.1.0',
        'lang': 'zh_CN',
        'st': '1630414739465',
        'uuid': 'hjudwgohxzVu96krv/T6Hg%3D%3D',
        'openudid': '4774db7d9faeb1e17962c620a6c9d088c50f8b77',
        'sign': '7a8c2ed53ec971372f0364d51a44c343',
        'sv': '100'
    }
    data = 'body=%7B%22to%22%3A%22https%3A%5C/%5C/plogin.m.jd.com%5C/jd-mlogin%5C/static%5C/html%5C/appjmp_blank.html%22%2C%22action%22%3A%22to%22%7D'
    totokenKey = post(url=url, headers=headers, params=params, data=data, verify=False).json()['tokenKey']
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'
    params = {
        'tokenKey': totokenKey,
        'to': 'https://plogin.m.jd.com/cgi-bin/m/thirdapp_auth_page?token=AAEAIEijIw6wxF2s3bNKF0bmGsI8xfw6hkQT6Ui2QVP7z1Xg',
        'client_type': 'android',
        'appid': 879,
        'appup_type': 1,
    }
    res = get(url=url, params=params, verify=False, allow_redirects=False).cookies.get_dict()
    pt_pin = res['pt_pin']
    cookie = f"pt_key={res['pt_key']};pt_pin={pt_pin};"
    return pt_pin, cookie


def subcookie(pt_pin, cookie, env):
    if env:
        sh = "/jd/config/config.sh"
        with open(sh, "r", encoding="utf-8") as read:
            configs = read.readlines()
        cknums = []
        for config in configs:
            cknum = findall(r'(?<=Cookie)[\d]+(?==")', config)
            if cknum != []:
                m = configs.index(config)
                cknums.append(cknum[0])
                if pt_pin in config:
                    configs[m] = f'Cookie{cknum[0]}="{cookie}"\n'
                    print(f"更新cookie成功！pt_pin：{pt_pin}")
                    break
            elif "第二区域" in config:
                newcknum = int(cknums[-1]) + 1
                configs.insert(m + 1, f'Cookie{newcknum}="{cookie}"\n')
                print(f"新增cookie成功！pt_pin：{pt_pin}")
                break
        with open(sh, "w", encoding="utf-8") as write:
            write.write("".join(configs))
    else:
        config = "/ql/config/auth.json"
        with open(config, "r", encoding="utf-8") as f1:
            token = json.load(f1)['token']
        if exists("/ql/config/env.sh"):
            url = 'http://127.0.0.1:5600/api/envs'
            headers = {'Authorization': f'Bearer {token}'}
            body = {
                'searchValue': pt_pin,
                'Authorization': f'Bearer {token}'
            }
            datas = get(url, params=body, headers=headers).json()['data']
            old = False
            for data in datas:
                if "pt_key" in data['value']:
                    body = {"name": "JD_COOKIE", "value": cookie, "_id": data['_id']}
                    old = True
                    break
            if old:
                put(url, json=body, headers=headers)
                url = 'http://127.0.0.1:5600/api/envs/enable'
                body = [body['_id']]
                put(url, json=body, headers=headers)
                print(f"更新cookie成功！pt_pin：{pt_pin}")
            else:
                body = [{"value": cookie, "name": "JD_COOKIE"}]
                post(url, json=body, headers=headers)
                print(f"新增cookie成功！pt_pin：{pt_pin}")


def notify(text):
    if exists("/jd/config/bot.json"):
        bot = "/jd/config/bot.json"
    else:
        bot = "/ql/config/bot.json"
    with open(bot, "r", encoding="utf-8") as botset:
        bot = json.load(botset)
    bot_token, user_id = bot['bot_token'], bot['user_id']
    TG_API_HOST = 'api.telegram.org'
    url = f'https://{TG_API_HOST}/bot{bot_token}/sendMessage'
    body = {
        "chat_id": user_id,
        "text": text,
        "disable_web_page_preview": True
    }
    headers = {"ontent-Type": "application/x-www-form-urlencoded"}
    try:
        if len(str(bot_token)) > 1 and len(str(user_id)) > 1:
            r = post(url, data=body, headers=headers)
            if r.ok:
                print("Telegram发送通知消息成功🎉。\n")
            elif r.status_code == '400':
                print("请主动给bot发送一条消息并检查接收用户ID是否正确。\n")
            elif r.status_code == '401':
                print("Telegram bot token 填写错误。\n")
        else:
            print('未提供telegram机器人推送所需的TG_BOT_TOKEN和TG_USER_ID，取消telegram推送消息通知\n')
    except Exception as error:
        print(f"telegram发送通知消息失败！！\n{error}")


def main():
    if exists("/jd/config/config.sh"):
        if not exists("/jd/config/wskey.list"):
            config = "/jd/config/config.sh"
            with open(config, "r", encoding="utf-8") as f1:
                configs = f1.read()
            keys = findall(r'wskey.*="(.*)"', configs)
        else:
            wskey = "/jd/config/wskey.list"
            with open(wskey, "r", encoding="utf-8") as f1:
                keys = f1.readlines()
        for key in keys:
            if "\n" in key:
                key = key[:-1]
            pin, cookie = getcookie(key)
            if "app_open" in cookie:
                subcookie(pin, cookie, True)
            else:
                pin = key.split(";")[0].split("=")[1]
                message = f"pin为{pin}的wskey貌似过期了！"
                print(message)
                notify(message)
    else:
        config = "/ql/config/auth.json"
        with open(config, "r", encoding="utf-8") as f1:
            token = json.load(f1)['token']
        url = 'http://127.0.0.1:5600/api/envs'
        headers = {'Authorization': f'Bearer {token}'}
        body = {
            'searchValue': 'JD_WSCK',
            'Authorization': f'Bearer {token}'
        }
        datas = get(url, params=body, headers=headers).json()['data']
        for data in datas:
            key = data['value']
            pin, cookie = getcookie(key)
            if "app_open" in cookie:
                subcookie(pin, cookie, False)
            else:
                pin = key.split(";")[0].split("=")[1]
                message = f"pin为{pin}的wskey貌似过期了！"
                print(message)
                notify(message)


if __name__ == '__main__':
    main()
